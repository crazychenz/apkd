def apkd_dbg_deploy(config, active, proj_dir):

    deploy_proj(proj_dir, active["avd"], config)


def deploy_proj(proj_dir, avd, config):

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

    from pathlib import Path
    apk_path = proj_dir / "working" / "pkg" / "working.apk"

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

    # TODO: Verify APK actually works normally and then test this again.
    
    install_result = device.install(str(apk_path))
    if install_result is not True and install_result is not None and "Success" not in str(install_result):
        raise RuntimeError(f"Install failed: {install_result}")

    print(f"Installed {str(apk_path)}")