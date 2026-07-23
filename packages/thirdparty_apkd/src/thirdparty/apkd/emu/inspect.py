
from ppadb.client import Client as AdbClient
import os
from pathlib import Path


def all_avd_names():
    import subprocess
    result = subprocess.run(["emulator", "-list-avds"], capture_output=True, text=True, check=True)
    #subprocess.run(["avdmanager", "list", "avds"], check=True) # this has more complex output
    return [avd_name for avd_name in result.stdout.splitlines() if avd_name.strip()]


def running_avd_names(host: str = "127.0.0.1", port: int = 5037):
    client = AdbClient(host=host, port=port)
    devices = client.devices()

    results = {}
    for device in devices:
        if not device.serial.startswith("emulator-"):
            continue  # skip physical/USB devices, keep only emulator instances

        props_output = device.shell("getprop")
        name = None
        for line in props_output.splitlines():
            if "avd_name" in line:
                # e.g. [ro.boot.qemu.avd_name]: [Pixel_7_API_33]
                name = line.split("]: [")[-1].rstrip("]").strip()
                break

        results[name] = device.serial

    return results


def _parse_avd_properties(path: Path) -> dict:
    """
    Parses AVD .ini / config.ini files, which are flat key=value pairs
    with no section headers (so configparser doesn't apply cleanly).
    """
    props = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            props[key.strip()] = value.strip()
    return props


def get_avd_home() -> Path:
    """
    Resolves where AVD definitions live, respecting ANDROID_AVD_HOME if set,
    falling back to the standard ~/.android/avd location.
    """
    env_home = os.environ.get("ANDROID_AVD_HOME")
    if env_home:
        return Path(env_home)
    return Path.home() / ".android" / "avd"


def get_system_image_for_avd(avd_name: str, avd_home: Path | None = None) -> dict:
    """
    Given an AVD name, returns info about the system image it was created
    from by reading its config.ini.

    Returns a dict:
    {
        "raw_sysdir": "system-images/android-34/google_apis_playstore/x86_64/",
        "package_id_slash": "system-images/android-34/google_apis_playstore/x86_64",
        "package_id_semicolon": "system-images;android-34;google_apis_playstore;x86_64",
        "api_level": "android-34",
        "tag": "google_apis_playstore",
        "abi": "x86_64",
        "target": "android-34" (from config.ini's "target" or "AvdId", if present),
    }
    """
    avd_home = avd_home or get_avd_home()

    avd_ini_path = avd_home / f"{avd_name}.ini"
    if not avd_ini_path.exists():
        raise FileNotFoundError(
            f"No AVD named '{avd_name}' found (expected {avd_ini_path})"
        )

    avd_ini = _parse_avd_properties(avd_ini_path)
    avd_path_str = avd_ini.get("path")
    if not avd_path_str:
        raise ValueError(f"'{avd_ini_path}' has no 'path' entry")

    config_ini_path = Path(avd_path_str) / "config.ini"
    if not config_ini_path.exists():
        raise FileNotFoundError(f"Expected config.ini at {config_ini_path}, not found")

    config = _parse_avd_properties(config_ini_path)

    sysdir = config.get("image.sysdir.1")
    if not sysdir:
        raise ValueError(
            f"'{config_ini_path}' has no 'image.sysdir.1' entry -- "
            f"available keys: {list(config.keys())}"
        )

    parts = [p for p in sysdir.strip("/").split("/") if p]
    # Expected shape: ['system-images', 'android-34', 'google_apis_playstore', 'x86_64']

    result = {
        "raw_sysdir": sysdir,
        "package_id_slash": "/".join(parts),
        "package_id_semicolon": ";".join(parts),
    }

    if len(parts) >= 4:
        result["api_level"] = parts[1]
        result["tag"] = parts[2]
        result["abi"] = parts[3]

    # A couple of extra fields worth surfacing if present
    if "target" in config:
        result["target"] = config["target"]
    if "abi.type" in config:
        result["abi_type"] = config["abi.type"]
    if "tag.id" in config:
        result["tag_id"] = config["tag.id"]

    return result


def parse_installed_system_images(pattern: str = "system-images*") -> list[dict]:
    import re
    import subprocess
    cmd = ["android", "sdk", "list", pattern]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    entries = []
    in_installed_section = True  # default (no --all) output starts here

    for raw_line in result.stdout.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        # Section headers -- stop once we hit "Available packages:",
        # since we only want the installed section
        if stripped.lower().startswith("installed packages"):
            in_installed_section = True
            continue
        if stripped.lower().startswith("available packages"):
            in_installed_section = False
            continue
        if "no installed packages" in stripped.lower() or "no available packages" in stripped.lower():
            continue

        if not in_installed_section:
            continue

        # Skip anything that isn't an actual package row
        if not stripped.startswith("system-images"):
            continue

        columns = re.split(r"\s{2,}", stripped)
        if len(columns) < 3:
            continue

        path, version, description = columns[0], columns[1], columns[2]
        parts = [p for p in path.split("/") if p]

        entry = {
            "path": path,
            "version": version,
            "description": description,
        }
        if len(parts) >= 4:
            entry["api_level"] = parts[1]
            entry["tag"] = parts[2]
            entry["abi"] = parts[3]

        entries.append(entry)

    return entries