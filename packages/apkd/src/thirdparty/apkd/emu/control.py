

def apkd_emu_start(config, avd_name):

    #import tempfile
    import subprocess
    import os

    cmd = [
        'emulator',
        '-avd',
        avd_name,
        '-no-snapshot',
        '-writable-system',
        '-show-kernel',
        '-verbose',
        '-no-audio',
        '-no-window',
    ]

    #fd, log_path = tempfile.mkstemp(prefix="apkd_emu_", suffix=".log")
    #log_file = os.fdopen(fd, "w")
    from thirdparty.apkd.emu.logs import build_log_path
    log_path = build_log_path(config, avd_name).resolve()
    log_file = open(str(log_path), "w")

    proc = subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    print(f"Started emulator, pid={proc.pid}, log={log_path}")
    print(f"Can monitor with: apkd emu logs {avd_name}")

def apkd_emu_scrcpy(config, avd_name):
    import subprocess

    from thirdparty.apkd.emu.inspect import running_avd_names
    running = running_avd_names()

    if avd_name not in running:
        print(f"No avd {avd_name} detected as running.")

    proc = subprocess.Popen(
        ["scrcpy", "-s", running[avd_name]],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    print(f"Started scrcpy, pid={proc.pid}")