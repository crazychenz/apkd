
from ppadb.client import Client as AdbClient

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

