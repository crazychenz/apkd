import subprocess
import psutil

from thirdparty.apkd.emu.inspect import running_avd_names


def apkd_emu_start(config, avd_name):

    #import tempfile
    import subprocess
    import os

    running = running_avd_names()
    if avd_name in running:
        print(f"avd {avd_name} already running as ({running[avd_name]}).")
        return

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


def is_scrcpy_running_for_serial(serial: str) -> int | None:
    """
    Returns the PID of a running scrcpy process targeting this serial,
    or None if there isn't one.
    """
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info["cmdline"] or []
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        if not cmdline:
            continue

        # Match "scrcpy" as the executable, and "-s <serial>" (or
        # "--serial <serial>"/"--serial=<serial>") anywhere in the args
        if "scrcpy" not in cmdline[0]:
            continue

        for i, arg in enumerate(cmdline):
            if arg in ("-s", "--serial") and i + 1 < len(cmdline) and cmdline[i + 1] == serial:
                return proc.info["pid"]
            if arg.startswith("--serial=") and arg.split("=", 1)[1] == serial:
                return proc.info["pid"]

    return None


def apkd_emu_scrcpy(config, avd_name):
    running = running_avd_names()

    if avd_name not in running:
        print(f"No avd {avd_name} detected as running.")
        return

    serial = running[avd_name]

    existing_pid = is_scrcpy_running_for_serial(serial)
    if existing_pid is not None:
        print(f"scrcpy already running for {avd_name} ({serial}), pid={existing_pid}")
        return

    proc = subprocess.Popen(
        ["scrcpy", "-s", serial],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )

    print(f"Started scrcpy for {avd_name} ({serial}), pid={proc.pid}")