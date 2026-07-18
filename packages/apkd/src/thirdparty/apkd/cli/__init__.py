
import logging
log = logging.getLogger(__name__)


import argparse
import sys
import argcomplete

import thirdparty.apkd.apk as apkd_apk


def init_argparse():
    # --- apkd
    apkd_parser = argparse.ArgumentParser(prog="apkd")
    apkd_parser.add_argument("--config", dest="config", action="store", help="path to config.yaml")
    apkd_parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity")
    apkd_parser.add_argument(
        "--log-level",
        metavar="MODULE:LEVEL",
        action="append",
        default=[],
        help="Example: --log-level thirdparty.apkd:DEBUG",
    )
    apkd_subparsers = apkd_parser.add_subparsers(dest="category", required=True)

    # --- apkd config
    apkd_config_parser = apkd_subparsers.add_parser("config", help="Config management")
    apkd_config_subparsers = apkd_config_parser.add_subparsers(dest="config_command", required=True)

    # --- apkd config init
    apkd_config_init_parser = apkd_config_subparsers.add_parser("init")
    apkd_config_init_parser.set_defaults(func=apkd_config_init_func)

    # --- apkd sdk
    apkd_sdk_parser = apkd_subparsers.add_parser("sdk", help="apkd sdk management")
    apkd_sdk_subparsers = apkd_sdk_parser.add_subparsers(dest="sdk_command", required=True)

    # --- apkd sdk init [--no-cache]
    apkd_sdk_init_parser = apkd_sdk_subparsers.add_parser("init")
    apkd_sdk_init_parser.add_argument("--no-cache", action="store_true")
    apkd_sdk_init_parser.set_defaults(func=apkd_sdk_init_func)

    # --- apkd sdk env
    apkd_sdk_env_parser = apkd_sdk_subparsers.add_parser("env")
    apkd_sdk_env_parser.set_defaults(func=apkd_sdk_env_func)

    # TODO: apkd sdk search
    # TODO: apkd sdk update
    # TODO: apkd sdk install
    # TODO: apkd sdk remove
    # TODO: apkd sdk show



    # --- apkd apk
    apkd_apk_parser = apkd_subparsers.add_parser("apk", help="Static APK analysis")
    apkd_apk_subparsers = apkd_apk_parser.add_subparsers(dest="apk_command", required=True)

    # --- apkd apk ls
    apkd_apk_ls_parser = apkd_apk_subparsers.add_parser("ls")
    apkd_apk_ls_parser.add_argument("apk_path")
    apkd_apk_ls_parser.set_defaults(func=apkd_apk_ls_func)

    # --- apkd apk manifest
    apkd_apk_manifest_parser = apkd_apk_subparsers.add_parser("manifest")
    apkd_apk_manifest_parser.add_argument("apk_path")
    apkd_apk_manifest_parser.set_defaults(func=apkd_apk_manifest_func)

    # --- apkd apk resources
    apkd_apk_resources_parser = apkd_apk_subparsers.add_parser("resources")
    apkd_apk_resources_parser.add_argument("apk_path")
    apkd_apk_resources_parser.set_defaults(func=apkd_apk_resources_func)

    # --- apkd apk extract
    apkd_apk_extract_parser = apkd_apk_subparsers.add_parser("extract")
    apkd_apk_extract_parser.add_argument("apk_path")
    apkd_apk_extract_parser.add_argument("proj_name")
    apkd_apk_extract_parser.set_defaults(func=apkd_apk_extract_func)

    # --- apkd apk patch
    apkd_apk_patch_parser = apkd_apk_subparsers.add_parser("patch")
    apkd_apk_patch_subparsers = apkd_apk_patch_parser.add_subparsers(dest="apk_patch_command", required=True)

    # --- apkd apk patch debug
    apkd_apk_patch_debug_parser = apkd_apk_patch_subparsers.add_parser("debug")
    apkd_apk_patch_debug_parser.add_argument("proj_name")
    apkd_apk_patch_debug_parser.set_defaults(func=apkd_apk_patch_debug_func)

    # --- apkd apk patch frida
    apkd_apk_patch_frida_parser = apkd_apk_patch_subparsers.add_parser("frida")
    # TODO: Need to think through the bias here.
    apkd_apk_patch_frida_parser.add_argument("--skip-gadget", action="store_true", default=False, required=False)
    apkd_apk_patch_frida_parser.add_argument("--skip-smali-patch", action="store_true", default=False, required=False)
    apkd_apk_patch_frida_parser.add_argument("proj_name")
    apkd_apk_patch_frida_parser.set_defaults(func=apkd_apk_patch_frida_func)

    # --- apkd apk pack
    apkd_apk_pack_parser = apkd_apk_subparsers.add_parser("pack")
    # apkd_apk_pack_parser.add_argument('--ks', dest="keystore")
    # apkd_apk_pack_parser.add_argument('--kspass', dest="kspass")
    # apkd_apk_pack_parser.add_argument('--key', dest="keyname")
    # apkd_apk_pack_parser.add_argument('--keypass', dest="keypass")
    apkd_apk_pack_parser.add_argument("proj_name")
    #apkd_apk_pack_parser.add_argument("new_apk_path")
    apkd_apk_pack_parser.set_defaults(func=apkd_apk_pack_func)

    # --- apkd apk debugify
    apkd_apk_debugify_parser = apkd_apk_subparsers.add_parser("debugify")
    # TODO: Need to think through the bias here.
    apkd_apk_debugify_parser.add_argument("--skip-gadget", action="store_true", default=False, required=False)
    apkd_apk_debugify_parser.add_argument("--skip-smali-patch", action="store_true", default=False, required=False)
    apkd_apk_debugify_parser.add_argument("apk_path")
    apkd_apk_debugify_parser.add_argument("proj_name")
    #apkd_apk_debugify_parser.add_argument("new_apk_path")
    apkd_apk_debugify_parser.set_defaults(func=apkd_apk_debugify_func)




    # --- apkd emu
    apkd_emu_parser = apkd_subparsers.add_parser("emu", help="Android emulator management")
    apkd_emu_subparsers = apkd_emu_parser.add_subparsers(dest="emu_command", required=True)

    # --- apkd emu list-remote
    apkd_emu_list_remote_parser = apkd_emu_subparsers.add_parser("list-remote")
    apkd_emu_list_remote_parser.set_defaults(func=apkd_emu_list_remote_func)

    # --- apkd emu pull
    apkd_emu_pull_parser = apkd_emu_subparsers.add_parser("pull")
    apkd_emu_pull_parser.add_argument("spec")
    apkd_emu_pull_parser.set_defaults(func=apkd_emu_pull_func)

    # --- apkd emu pull
    apkd_emu_images_parser = apkd_emu_subparsers.add_parser("images")
    apkd_emu_images_parser.set_defaults(func=apkd_emu_images_func)

    # --- apkd emu create
    apkd_emu_create_parser = apkd_emu_subparsers.add_parser("create")
    apkd_emu_create_parser.add_argument("name")
    apkd_emu_create_parser.add_argument("package")
    apkd_emu_create_parser.add_argument("--device", action="store", default=None)
    apkd_emu_create_parser.add_argument("--force", action="store_true", default=False)
    apkd_emu_create_parser.set_defaults(func=apkd_emu_create_func)

    # --- apkd emu ps
    apkd_emu_ps_parser = apkd_emu_subparsers.add_parser("ps")
    apkd_emu_ps_parser.set_defaults(func=apkd_emu_ps_func)

    # --- apkd emu start
    apkd_emu_start_parser = apkd_emu_subparsers.add_parser("start")
    apkd_emu_start_parser.add_argument("name")
    apkd_emu_start_parser.set_defaults(func=apkd_emu_start_func)

    # --- apkd emu gui
    apkd_emu_gui_parser = apkd_emu_subparsers.add_parser("gui")
    apkd_emu_gui_parser.add_argument("name")
    apkd_emu_gui_parser.set_defaults(func=apkd_emu_gui_func)

    # --- apkd emu stop
    apkd_emu_stop_parser = apkd_emu_subparsers.add_parser("stop")
    apkd_emu_stop_parser.add_argument("name")
    apkd_emu_stop_parser.set_defaults(func=apkd_emu_stop_func)





    # --- apkd runtime
    apkd_runtime_parser = apkd_subparsers.add_parser("runtime", help="Android runtime management")
    apkd_runtime_subparsers = apkd_runtime_parser.add_subparsers(dest="runtime_command", required=True)

    # --- apkd runtime deploy
    apkd_runtime_deploy_parser = apkd_runtime_subparsers.add_parser("deploy")
    apkd_runtime_deploy_parser.add_argument("--as-apk", action="store_true", default=False, required=False)
    apkd_runtime_deploy_parser.add_argument("application")
    apkd_runtime_deploy_parser.set_defaults(func=apkd_runtime_deploy_func)

    # --- apkd runtime stage
    apkd_runtime_stage_parser = apkd_runtime_subparsers.add_parser("stage")
    apkd_runtime_stage_parser.add_argument("--as-pkgname", action="store_true", default=False, required=False)
    apkd_runtime_stage_parser.add_argument("application")
    apkd_runtime_stage_parser.set_defaults(func=apkd_runtime_stage_func)

    # --- apkd runtime connect
    apkd_runtime_connect_parser = apkd_runtime_subparsers.add_parser("connect")
    apkd_runtime_connect_parser.add_argument("application")
    apkd_runtime_connect_parser.set_defaults(func=apkd_runtime_connect_func)

    # --- apkd runtime easy_debug
    apkd_runtime_easy_debug_parser = apkd_runtime_subparsers.add_parser("easy_debug")
    apkd_runtime_easy_debug_parser.add_argument("application")
    apkd_runtime_easy_debug_parser.set_defaults(func=apkd_runtime_easy_debug_func)




    # apkd dbg [--config config_path] [--force-refresh] [--apk apk_path] \
    #          [--force-download] [--image system_image] [--avd avd_name] [--with-ui|--with-gui] \
    #          [--jdwp-port host:device] [--frida-port host:device] \
    #          [--repl-sock host:port|path] [--exec-sock host:port|path] [--dict-sock host:port|path] \
    #          [use_case_name] [proj_name]


    # --- apkd dbg
    apkd_dbg_parser = apkd_subparsers.add_parser("dbg", help="debugger")
    apkd_dbg_parser.add_argument("--config", action="store", default=None, required=False)
    # TODO: Instead of stopping, consider dry-run?
    apkd_dbg_parser.add_argument("--show-config", action="store", required=False, help="Show resolved config and stop.")
    apkd_dbg_parser.add_argument("--force-refresh", action="store_true", default=False, required=False)
    apkd_dbg_parser.add_argument("--apk", action="store", default=None, required=False)
    apkd_dbg_parser.add_argument("--force-download", action="store_true", default=False, required=False)
    apkd_dbg_parser.add_argument("--image", action="store", default=None, required=False)
    apkd_dbg_parser.add_argument("--avd", action="store", default=None, required=False)
    apkd_dbg_parser.add_argument("--gui", choices=["scrcpy", "emu"], default="scrcpy", help="scrcpy | emu")
    apkd_dbg_parser.add_argument("--jdwp-port", action="store", default=None, required=False, help="host:port")
    apkd_dbg_parser.add_argument("--frida-port", action="store", default=None, required=False, help="host:port")
    apkd_dbg_parser.add_argument("--repl-sock", action="store", default=None, help="host:port | path")
    apkd_dbg_parser.add_argument("--exec-sock", action="store", default=None, help="host:port | path")
    apkd_dbg_parser.add_argument("--dict-sock", action="store", default=None, help="host:port | path")
    apkd_dbg_parser.add_argument("--base-dir", action="store", default=None)
    apkd_dbg_parser.add_argument("--proj-dir", action="store", default=None)
    apkd_dbg_parser.add_argument("--sdk-dir", action="store", default=None)
    apkd_dbg_parser.add_argument("operation")
    apkd_dbg_parser.add_argument("proj_name")
    apkd_dbg_parser.set_defaults(func=apkd_dbg_func)

    return apkd_parser


def main():
    apkd_parser = init_argparse()
    argcomplete.autocomplete(apkd_parser)
    args = apkd_parser.parse_args()

    level = {
        0: logging.ERROR,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }.get(args.verbose, logging.DEBUG)

    logging.basicConfig(level=level, format="%(levelname)-8s %(name)s: %(message)s")

    for spec in args.log_level:
        module, level_name = spec.split(":")
        logging.getLogger(module).setLevel(getattr(logging, level_name.upper()))

    from thirdparty.apkd.config import load_apkd_config, baseline_empty_config
    from thirdparty.apkd.sdk.env import apkd_apply_env
    config = baseline_empty_config()
    if args.config:
        config = load_apkd_config(config_path=args.config)
    apkd_apply_env(config)

    args.func(args, config)


def apkd_config_init_func(args, config):
    # TODO: Consider using given config as baseline?
    from thirdparty.apkd.config import save_apkd_config
    save_apkd_config({}, args.config)


def apkd_sdk_init_func(args, config):
    # ** Any CLI arg overrides go here.
    # TODO: Allow --base-path override
    # TODO: Allow --sdk-path override
    # TODO: If both sdk-path and base-path, sdk-path wins.

    from thirdparty.apkd.sdk.init import apkd_sdk_init
    apkd_sdk_init(config=config, no_cache=args.no_cache)


def apkd_sdk_env_func(args, config):
    # ** Any CLI arg overrides go here.
    # TODO: Allow --base-path override
    # TODO: Allow --sdk-path override
    # TODO: If both sdk-path and base-path, sdk-path wins.

    from thirdparty.apkd.sdk.env import apkd_print_env
    apkd_print_env(config=config)


def apkd_apk_ls_func(args, config):
    apkd_apk.list_zip_like_ls(args.apk_path)


def apkd_apk_manifest_func(args, config):
    print(apkd_apk.get_manifest(args.apk_path))


def apkd_apk_resources_func(args, config):
    print(apkd_apk.get_resources(args.apk_path))


def apkd_apk_extract_func(args, config):
    # Extract everything.
    apkd_apk.do_extraction_process(config, args.apk_path, args.proj_name)

    # Rebuild everything.
    apkd_apk.do_pack_process(config, args.proj_name)


def apkd_apk_patch_debug_func(args, config):
    apkd_apk.apkd_apk_patch_debuggable_manifest(config, args.proj_name)


def apkd_apk_patch_frida_func(args, config):
    apkd_apk.patch_in_frida_gadget(config, args.proj_name, not args.skip_gadget, not args.skip_smali_patch)


def apkd_apk_pack_func(args, config):
    # Rebuild everything.
    apkd_apk.do_pack_process(config, args.proj_name)


def apkd_apk_debugify_func(args, config):
    # Extract everything.
    apkd_apk.do_extraction_process(config, args.apk_path, args.proj_name)

    apkd_apk.apkd_apk_patch_debuggable_manifest(config, args.proj_name)
    
    apkd_apk.patch_in_frida_gadget(config, args.proj_name, not args.skip_gadget, not args.skip_smali_patch)

    # Rebuild everything.
    apkd_apk.do_pack_process(config, args.proj_name)


# --- Emulator Management ---

def apkd_emu_list_remote_func(args, config):
    import subprocess

    print("Fetching sdbmanager packages. May take a moment if not recently cached.")
    result = subprocess.run(
        ['sdkmanager', '--list'],
        check=True,
        capture_output=True,
        text=True,
    )

    tgts = {}
    for line in result.stdout.splitlines():
        items = line.split('|')
        if len(items) > 2:
            pkg = items[0].strip()

            version = items[1].strip()
            desc = items[2].strip()
            tgts[pkg] = {
                "tags": pkg.split(';'),
                "pkg": pkg,
                "version": version,
                "desc": desc,
            }
    
    # TODO: Make these user specified.
    query = set(['system-images', 'x86_64', 'android-33'])
    results = {key: item for key, item in tgts.items() if query.issubset(item["tags"])}
    for name, pkg in results.items():
        print(f"{name}\n    {pkg['desc']}")


# apkd emu pull "system-images;android-33;default;x86_64"
def apkd_emu_pull_func(args, config):
    import subprocess
    print(f"Pulling {args.spec}")
    result = subprocess.run(['sdkmanager', args.spec], check=True)


def apkd_emu_images_func(args, config):
    import subprocess
    print(f"Installed System Images:")
    result = subprocess.run(
        ['sdkmanager', '--list_installed'],
        check=True,
        capture_output=True,
        text=True,
    )

    tgts = {}
    for line in result.stdout.splitlines():
        items = line.split('|')
        if len(items) > 2:
            pkg = items[0].strip()

            version = items[1].strip()
            desc = items[2].strip()
            tgts[pkg] = {
                "tags": pkg.split(';'),
                "pkg": pkg,
                "version": version,
                "desc": desc,
            }
    
    # TODO: Make these user specified.
    query = set(['system-images'])
    results = {key: item for key, item in tgts.items() if query.issubset(item["tags"])}
    for name, pkg in results.items():
        print(f"- {name}\n    + {pkg['desc']}")


# emulator -list-avds


def apkd_emu_create_func(args, config):
    import subprocess
    
    #avdmanager create avd -n android13 -k "system-images;android-33;default;x86_64"

    cmd = [
        "avdmanager",
        "create", "avd",
        "--name", args.name,
        "--package", args.package,
    ]
    if args.device:
        cmd += ["--device", device]
    if args.force:
        cmd.append("--force")  # overwrite existing AVD with same name, no prompt for that either

    subprocess.run(
        cmd,
        input="no\n",   # answer to "Do you wish to create a custom hardware profile?"
        text=True,
        check=True,
    )

    
def apkd_emu_ps_func(args, config):
    import subprocess
    subprocess.run(["avdmanager", "list", "avds"], check=True)


# ! TODO: Consider adb root, adb remount

def apkd_emu_start_func(args, config):
    import tempfile
    import subprocess
    import os

    cmd = [
        'emulator',
        '-avd',
        args.name,
        '-no-snapshot',
        '-writable-system',
        '-show-kernel',
        '-verbose',
        '-no-audio',
        '-no-window',
    ]

    fd, log_path = tempfile.mkstemp(prefix="apkd_emu_", suffix=".log")
    log_file = os.fdopen(fd, "w")

    proc = subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    print(f"Started emulator, pid={proc.pid}, log={log_path}")
    print(f"Can monitor with: tail -f {log_path}")
    #return proc, log_path


def apkd_emu_gui_func(args, config):
    import subprocess

    proc = subprocess.Popen(
        ["scrcpy"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,  # equivalent of setsid
    )

    print(f"Started scrcpy, pid={proc.pid}")


def apkd_emu_stop_func(args, config):
    import subprocess

    result = subprocess.run(
        ["pgrep", "-f", f"emulator.*-avd {args.name}"],
        capture_output=True, text=True,
    )
    pids = [pid for pid in result.stdout.splitlines() if pid.strip()]

    if not pids:
        print(f"No process found for AVD '{args.name}'")
        exit(1)
        #return False

    for pid in pids:
        subprocess.run(["kill", pid], check=True)
        print(f"Sent SIGTERM to pid {pid}")

    #return True


# ! TODO: Consider scrcpy integration.

# --- ADB Automation ---

"""
in general, the "apkd runtime" should be able to target apk or a apk_content_path (but not both)

The adb user precedence:
- Note: The precedence may change depending on whether config is explicit or implicit.
- CLI Argument
- Config APKD_ADB_PATH variable
- APKD_ADB_PATH env variable
- PATH
- Config PATH variable
"""


def apkd_runtime_deploy_func(args, config):

    # TODO: If we're missing the config, must quit.
    from thirdparty.apkd.config.load import load_apkd_config
    config = load_apkd_config()

    adb_host = config["adb"]["default"]["host"]
    adb_port = int(config["adb"]["default"]["port"])
    device_name = config["adb"]["default"]["device"]
    # tgt_pkg = ??

    from ppadb.client import Client as AdbClient
    client = AdbClient(host=adb_host, port=adb_port)

    # Connection sanity.
    print(f'ADB Client Version: {client.version()}')
    device = client.device(device_name)
    if device is None:
        raise RuntimeError(f"No device found with serial '{device_serial}'")

    from pathlib import Path
    apk_path = Path(args.application).resolve()
    if not args.as_apk:
        apk_path = apk_path / "working" / "pkg" / "working.apk"

    # Note: Given the project folder, we'll install the working.apk, but we
    # also need to dynamically pull out the package name with androguard.
    from androguard.core.apk import APK
    package_name = APK(str(apk_path)).get_package()

    uninstall_result = device.uninstall(package_name)
    if uninstall_result == False: 
        print(f"Uninstall skipped/failed (likely not previously installed)")
    elif uninstall_result and isinstance(uninstall_result, str) and "Success" not in str(uninstall_result):
        print(f"Uninstall skipped/failed (likely not previously installed): {uninstall_result.strip()}")
    else:
        print(f"Uninstalled {package_name}")

    install_result = device.install(str(apk_path))
    if install_result is not True and install_result is not None and "Success" not in str(install_result):
        raise RuntimeError(f"Install failed: {install_result}")

    print(f"Installed {apk_path}")










    # # Configure the tgt_pkg to wait for debugger on start.
    # cmd = f'am set-debug-app -w {self.tgt_pkg}'
    # print(cmd)
    # print(self.device.shell(cmd))

    # # Get the main activity name. (Note: This is a bit wonky.)
    # cmd = f'cmd package resolve-activity -c android.intent.category.LAUNCHER {self.tgt_pkg}'
    # print(cmd)
    # pkg_act_info = self.device.shell(cmd)

    # # import re
    # # # Get text following "name=" until end of line.
    # # pattern = re.compile(r'(?<=name=)\S+')
    # # matches = []
    # # for line in pkg_act_info.split('\n'):
    # #     found = pattern.findall(line)
    # #     matches.extend(found)
    # # #print(matches)
        
    # pkg_main_act = matches[0].replace(self.tgt_pkg, f'{self.tgt_pkg}/')
    # print(pkg_main_act)

    # # Start the tgt_pkg's main activity.
    # cmd = f'am start -n {pkg_main_act}'
    # print(cmd)
    # self.device.shell(cmd)

    # import time
    # time.sleep(0.5)

    # # Get the process id (PID) of the running tgt_pkg.
    # adb_procs = self.device.shell(f'ps -A')
    # self.proc_pid = None
    # for proc in adb_procs.split('\n'):
    #     if proc.find(self.tgt_pkg) < 0:
    #         continue
    #     self.proc_pid = int(proc.split()[1])
    #     break
    # if not self.proc_pid:
    #     print("Target process not found.")
    #     exit(1)
        
    # # Port forward internal JDWP port (same as PID) to localhost:8700
    # cmd = f'adb forward tcp:8700 jdwp:{self.proc_pid}'
    # print(cmd)
    # self.device.forward('tcp:8700', f'jdwp:{self.proc_pid}')

    # time.sleep(3)


def apkd_runtime_stage_func(args, config):
    # TODO: Do deploy
    # TODO: Tag application as "wait for debugger"
    # TODO: Make the application start but wait for debugger to attach
    print("apkd_runtime_stage_func not implemented")

    # TODO: If we're missing the config, must quit.
    from thirdparty.apkd.config.load import load_apkd_config
    config = load_apkd_config()
    
    adb_host = config["adb"]["default"]["host"]
    adb_port = int(config["adb"]["default"]["port"])
    device_name = config["adb"]["default"]["device"]

    # Package name of working.apk is the target.
    from pathlib import Path
    package_name = args.application
    if not args.as_pkgname:
        apk_path = Path(args.application).resolve() / "working" / "pkg" / "working.apk"
        from androguard.core.apk import APK
        package_name = APK(str(apk_path)).get_package()

    from ppadb.client import Client as AdbClient
    client = AdbClient(host=adb_host, port=adb_port)

    # Connection sanity.
    print(f'ADB Client Version: {client.version()}')
    device = client.device(device_name)
    if device is None:
        raise RuntimeError(f"No device found with serial '{device_serial}'")

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

    import re
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
    cmd = f'adb forward tcp:8700 jdwp:{proc_pid}'
    print(cmd)
    device.forward('tcp:8700', f'jdwp:{proc_pid}')

    import time
    time.sleep(3)

    # --- Assuming JDWP is now available, we'll use it to start frida ---




def apkd_runtime_connect_func(args, config):
    # TODO: Connect with jwdp debugger process
    print("apkd_runtime_connect_func not implemented")

    """
        Common options at this point:
        - `jdb -attach localhost:8700`
        - `jdb -connect com.sun.jdi.SocketAttach:hostname=localhost,port=8700`
          - `threads`
          - `thread 1`
          - `main[1] print System.loadLibrary("frida-gadget")`
          - `main[1] cont`
          - `main[1] quit`
        - `cat <(echo "suspend") - | jdb -attach localhost:8700`
        - Use JADX (TODO: Can we start JADX from CLI as connected to debugger session?)
        - ** Use thirdparty dalvik debugger
    """

def apkd_runtime_easy_debug_func(args, config):
    apkd_runtime_deploy_func(args)
    apkd_runtime_stage_func(args)
    apkd_runtime_connect_func(args)
    # Todo: connect
    print("apkd_runtime_easy_debug_func not implemented")





# apkd dbg [--config config_path] [--force-refresh] [--apk apk_path] \
#          [--force-download] [--image system_image] [--avd avd_name] [--with-ui|--with-gui] \
#          [--jdwp-port host:device] [--frida-port host:device] \
#          [--repl-sock host:port|path] [--exec-sock host:port|path] [--dict-sock host:port|path] \
#          [use_case_name] [proj_name]
# - proj requires apk or folder
# - avd requires image or avd
# - jdwp/frida require proj
# - use_case_name dependencies vary (implicit arguments in config?)
#   - debugify
#   - deploy - requires proj, emu
#   - stage [--no-debugify] [--no-deploy] - requires proj, emu, jdwp/frida

# python3 -m venv apkd && ./apkd/bin/python -m pip install thirdparty-apkd
# (eval "$(./apkd/bin/apkd sdk init --source)" && bash)
# Without config:
# - apkd dbg --apk `apk` --avd 'android13' --with-ui stage here
# With config:
# - apkd dbg stage here

# Panes:
# - apkd dbg logs here
# - apkd dbg logcat here
# - apkd dbg watch here
# - apkd dbg bytecode here
# - apkd dbg repl here
# - apkd dbg disassembly here
# - apkd dbg registers here





def apkd_dbg_func(args, config):
    from thirdparty.apkd.dbg.lib import xdg_config_home, has_path_delimiter

    # Default config
    config_dir = xdg_config_home() / "apkd"
    if args.config:
        config_dir = Path(args.config)

    # Hard coded base line config, override from disk config, environment, and finally CLI.
    active = {
        "force_refresh": False,
        "apk": None,
        "force_download": False,
        "image": None,
        "avd": None,
        "gui": "scrcpy",
        "jdwp_port": None,
        "frida_port": None,
        "repl_sock": None,
        "exec_sock": None,
        "dict_sock": None,
        "base_dir": None,
        "proj_dir": None,
        "sdk_dir": None,
        "proj_dir": None,
        "operation": None,
        "proj_name": None,
    }

    if not config_dir.exists():
        from thirdparty.apkd.config.init import init_apkd_config_dir
        init_apkd_config_dir(config_dir)

    # TODO: Consider using config_init as hard coded baseline? Maybe not, because of keystore?
    from thirdparty.apkd.config.load import load_apkd_config
    config = load_apkd_config(config_dir)

    # ** CLI arguments will override config going forward. **

    if "dbg" not in config:
        config["dbg"] = {}
    if "projects" not in config["dbg"]:
        config["dbg"]["projects"] = {}
    if args.proj_name is not None and args.proj_name not in config["dbg"]["projects"]:
        config["dbg"]["projects"][args.proj_name] = {}

    active = config["dbg"]["projects"][args.proj_name]

    # TODO: At this point, consider overriding config["dbg"]["autofill"] with project specific overrides.
    # TODO: - In this case, we'd use config["dbg"]["autofill"] instead of config["dbg"]["projects"][args.proj_name]

    # TODO: Override any relevant config from environment variables here.

    # CLI overrides here.
    if args.force_refresh is not None:
        active["force_refresh"] = args.force_refresh
    if args.apk is not None:
        active["apk"] = args.apk
    if args.force_download is not None:
        active["force_download"] = args.force_download
    if args.image is not None:
        active["image"] = args.image
    if args.avd is not None:
        active["avd"] = args.avd
    if args.gui is not None:
        active["gui"] = args.gui
    if args.jdwp_port is not None:
        active["jdwp_port"] = args.jdwp_port
    if args.frida_port is not None:
        active["frida_port"] = args.frida_port
    if args.repl_sock is not None:
        active["repl_sock"] = args.repl_sock
    if args.exec_sock is not None:
        active["exec_sock"] = args.exec_sock
    if args.dict_sock is not None:
        active["dict_sock"] = args.dict_sock
    if args.base_dir is not None:
        active["base_dir"] = args.base_dir
    if args.proj_dir is not None:
        active["proj_dir"] = args.proj_dir
    if args.sdk_dir is not None:
        active["sdk_dir"] = args.sdk_dir
    if args.proj_dir is not None:
        active["proj_dir"] = args.base_dir

    active["operation"] = args.operation
    active["proj_name"] = args.proj_name

    # --- Sanity Checks ---
    issues = []

    proj_name = active["proj_name"]
    if has_path_delimiter(proj_name):
        issues.append("proj_name must not have / or \\. Use --base-dir/--proj-dir to specify path.")

    # Worst case, use local folder.
    base_dir = Path('.') / "apkd"
    
    # Best implicit case, use venv as base prefix.
    if sys.prefix != sys.base_prefix:
        # We're in a venv, use it.
        base_dir = Path(sys.prefix) / "apkd"

    # Allow environment override.
    base_dir = Path(os.environ.get("APKD_BASE_DIR", base_dir))

    # CLI override always wins.
    if args.base_dir:
        base_dir = Path(args.base_dir)
    base_dir = base_dir.resolve()

    proj_dir = base_dir / "projects" / args.proj_name
    if args.proj_dir:
        proj_dir = Path(args.proj_dir).resolve()

    sdk_dir = base_dir / "sdk"
    if args.sdk_dir:
        sdk_dir = Path(args.proj_dir).resolve()



    # Does proj_name already exists?
    # - Has the user set a base_dir? <base_dir>/apkd/projects/<proj_name>
    # - No user set base_dir, are we in a venv? base_dir = sys.prefix
    # - No venv, throw user must set base_dir or be in venv.

    # - Are we in venv and is proj_name in <venv>/apkd/<proj_name>?
    # - No venv, is there a base_dir override?


    # - proj requires apk or folder
    # - avd requires image or avd
    # - jdwp/frida require proj
    # - use_case_name dependencies vary (implicit arguments in config?)
    #   - debugify
    #   - deploy - requires proj, emu
    #   - stage [--no-debugify] [--no-deploy] - requires proj, emu, jdwp/frida

    if len(issues):
        print("Can not run command with given arguments.\n\nIssues:")
        for issue in issues:
            print(f"- {issue}")
        exit(1)





if __name__ == "__main__":
    main()