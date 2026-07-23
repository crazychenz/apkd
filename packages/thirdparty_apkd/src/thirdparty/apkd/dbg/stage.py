
import logging
log = logging.getLogger(__name__)

from pathlib import Path
import re

# --- Caller must deploy before calling. ---
def apkd_dbg_stage(config, active, proj_dir):
    stage_proj(proj_dir, active["avd"], config)


def stage_proj(proj_dir, avd, config):

    adb_host = config["adb"]["default"]["host"]
    adb_port = int(config["adb"]["default"]["port"])

    from thirdparty.apkd.emu.inspect import running_avd_names
    running = running_avd_names()

    device_name = running[avd]

    from ppadb.client import Client as AdbClient
    client = AdbClient(host=adb_host, port=adb_port)

    # Connection sanity.
    print(f'ADB Client Version: {client.version()}')
    device = client.device(device_name)
    if device is None:
        raise RuntimeError(f"No device found with serial '{device_serial}'")

    from androguard.core.apk import APK
    apk_path = proj_dir / "working" / "pkg" / "working.apk"
    package_name = APK(str(apk_path)).get_package()

    # ===== wait for debugging, start app, and listen to jwdp =====

    # Configure the package_name to wait for debugger on start.
    cmd = f'am set-debug-app -w {package_name}'
    print(cmd)
    print(device.shell(cmd))

    # Get the main activity name. (Note: This is a bit wonky.)
    # TODO: Make this more versatile
    cmd = f'cmd package resolve-activity -c android.intent.category.LAUNCHER {package_name}'
    print(cmd)
    pkg_act_info = device.shell(cmd)

    # Get text following "name=" until end of line.
    pattern = re.compile(r'(?<=name=)\S+')
    matches = []
    for line in pkg_act_info.split('\n'):
        found = pattern.findall(line)
        matches.extend(found)
    #print(matches)
        
    pkg_main_act = matches[0].replace(package_name, f'{package_name}/')
    print(pkg_main_act)

    # Start the package_name's main activity.
    cmd = f'am start -n {pkg_main_act}'
    print(cmd)
    device.shell(cmd)

    import time
    time.sleep(0.5)

    # --- Assuming the application is waiting ---

    # Get the process id (PID) of the running package_name.
    adb_procs = device.shell(f'ps -A')
    proc_pid = None
    for proc in adb_procs.split('\n'):
        if proc.find(package_name) < 0:
            continue
        proc_pid = int(proc.split()[1])
        break
    if not proc_pid:
        print("Target process not found.")
        exit(1)
        
    # Port forward internal JDWP port (same as PID) to localhost:8700
    # TODO: Use ports from active['jdwp_port']
    cmd = f'adb forward tcp:8700 jdwp:{proc_pid}'
    print(cmd)
    device.forward('tcp:8700', f'jdwp:{proc_pid}')

    import time
    time.sleep(3)

    # --- Assuming JDWP is now available, we'll use it to start frida ---

    return proc_pid