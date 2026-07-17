
import os


# TODO: Make sure this only runs once per run.
def apkd_apply_env(config):
    
    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)

    os.environ["BASE_PATH"] = str(base_dir)
    os.environ["ANDROID_HOME"] = str(sdk_dir)
    os.environ["JAVA_HOME"] = str(sdk_dir / "java17")
    PATH = [
        os.path.expandvars("${JAVA_HOME}/bin"),
        os.path.expandvars("${ANDROID_HOME}/cmdline-tools/latest/bin"),
        os.path.expandvars("${ANDROID_HOME}/platform-tools"),
        os.path.expandvars("${ANDROID_HOME}/emulator"),
        os.path.expandvars("${ANDROID_HOME}/scrcpy"),
        os.path.expandvars("${ANDROID_HOME}/jadx/bin"),
        os.path.expandvars("${ANDROID_HOME}/misc-tools"),
        os.environ["PATH"]
    ]
    os.environ["PATH"] = os.path.expandvars(':'.join(PATH))


def apkd_print_env(config):

    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)

    print(f"export BASE_PATH=\"{str(base_dir)}\"")
    print(f"export ANDROID_HOME=\"{str(sdk_dir)}\"")
    print(f"export JAVA_HOME=\"{str(sdk_dir / "java17")}\"")
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