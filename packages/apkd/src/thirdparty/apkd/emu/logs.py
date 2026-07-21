# avd_log_utils.py
import re
import os
import time
from pathlib import Path

LOG_FILENAME_RE = re.compile(
    r"^(?P<avd_name>.+)__(?P<timestamp>\d{8}T\d{6})__boot(?P<boot>\d+)\.log$"
)


def build_log_path(base_dir, avd_name: str) -> Path:
    """
    Computes the next log file path for this AVD: a fresh timestamp plus
    an auto-incremented boot count based on how many log files already
    exist for this AVD. Never reuses an existing filename.
    """

    log_dir = base_dir / "logs" / "avd"
    log_dir.mkdir(parents=True, exist_ok=True)

    existing_boot_numbers = [
        int(m.group("boot"))
        for f in log_dir.glob(f"{avd_name}__*__boot*.log")
        if (m := LOG_FILENAME_RE.match(f.name))
    ]
    next_boot = (max(existing_boot_numbers) + 1) if existing_boot_numbers else 1

    timestamp = time.strftime("%Y%m%dT%H%M%S")
    filename = f"{avd_name}__{timestamp}__boot{next_boot:04d}.log"

    path = log_dir / filename
    # Extremely unlikely, but guard against a same-second re-run colliding
    while path.exists():
        next_boot += 1
        filename = f"{avd_name}__{timestamp}__boot{next_boot:04d}.log"
        path = log_dir / filename

    return path


def find_latest_log(config, avd_name: str) -> Path | None:
    """
    Returns the most recent log file for this AVD, or None if there isn't
    one. "Most recent" = highest timestamp string, which sorts correctly
    since the format is zero-padded and lexicographically ordered.
    """
    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)

    log_dir = base_dir / "logs" / "avd"
    if not log_dir.exists():
        return None

    candidates = [
        f for f in log_dir.glob(f"{avd_name}__*__boot*.log")
        if LOG_FILENAME_RE.match(f.name)
    ]
    if not candidates:
        return None

    # Filename format sorts correctly as plain strings because of the
    # fixed-width timestamp and zero-padded boot number.
    return max(candidates, key=lambda p: p.name)


def tail_f_simple(path, poll_interval: float = 0.5):
    with open(path, "r") as f:
        f.seek(0, 2)  # seek to end of file
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                time.sleep(poll_interval)


def tail_f_replaced(path, poll_interval: float = 0.5):
    with open(path, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                yield line
                continue

            # No new data -- check if the file got truncated
            # (e.g. someone rewrote it out from under us)
            current_size = os.fstat(f.fileno()).st_size
            if current_size < f.tell():
                f.seek(0)

            time.sleep(poll_interval)


def tail_f_rotated(path, poll_interval: float = 0.5):
    f = open(path, "r")
    f.seek(0, 2)

    try:
        while True:
            line = f.readline()
            if line:
                yield line
                continue

            time.sleep(poll_interval)

            # Detect rotation: current path now points to a different inode
            try:
                if os.stat(path).st_ino != os.fstat(f.fileno()).st_ino:
                    f.close()
                    f = open(path, "r")
            except FileNotFoundError:
                pass  # file momentarily missing during rotation
    finally:
        f.close()
