
import os


# TODO: Make sure this only runs once per run.
def apkd_apply_env(config):
    
    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)

    gradle_dir = base_dir / "cache" / "gradle"
    gradle_dir.mkdir(parents=True, exist_ok=True)

    os.environ["APKD_BASE_PATH"] = str(base_dir)
    os.environ["ANDROID_HOME"] = str(sdk_dir)
    os.environ["JAVA_HOME"] = str(sdk_dir / "java17")
    os.environ["GRADLE_USER_HOME"] = str(gradle_dir)

    PATH = [
        os.path.expandvars("${JAVA_HOME}/bin"),
        os.path.expandvars("${ANDROID_HOME}/cmdline-tools/latest/bin"),
        os.path.expandvars("${ANDROID_HOME}/platform-tools"),
        os.path.expandvars("${ANDROID_HOME}/emulator"),
        os.path.expandvars("${ANDROID_HOME}/scrcpy"),
        os.path.expandvars("${ANDROID_HOME}/jadx/bin"),
        os.path.expandvars("${ANDROID_HOME}/misc-tools"),
    ]

    for bt in [item for item in config["downloads"]["sdkmanager"] if item.startswith("build-tools")]:
        PATH.append(os.path.expandvars(f"${{ANDROID_HOME}}/{bt}"))
    PATH.append(os.environ["PATH"])
    
    os.environ["PATH"] = os.path.expandvars(':'.join(PATH))


def apkd_print_env(config):

    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)
    gradle_dir = base_dir / "cache" / "gradle"

    print(f"export APKD_BASE_PATH=\"{str(base_dir)}\"")
    print(f"export ANDROID_HOME=\"{str(sdk_dir)}\"")
    print(f"export JAVA_HOME=\"{str(sdk_dir / "java17")}\"")
    print(f"export GRADLE_USER_HOME=\"{str(gradle_dir)}\"")
    print(f"export PATH=\"{os.environ["PATH"]}\"")
    print("# To Apply: (eval \"$(apkd sdk env)\" && bash)")
    
    # Only relevant if apkd_apply_env() hasn't been run.
    # PATH = [
    #     os.path.expandvars("${JAVA_HOME}/bin"),
    #     os.path.expandvars("${ANDROID_HOME}/cmdline-tools/latest/bin"),
    #     os.path.expandvars("${ANDROID_HOME}/platform-tools"),
    #     os.path.expandvars("${ANDROID_HOME}/emulator"),
    #     os.path.expandvars("${ANDROID_HOME}/scrcpy"),
    #     os.path.expandvars("${ANDROID_HOME}/jadx/bin"),
    #     os.path.expandvars("${ANDROID_HOME}/misc-tools"),
    #     "${PATH}",
    # ]
    # print(f"export PATH=\"{':'.join(PATH)}\"")