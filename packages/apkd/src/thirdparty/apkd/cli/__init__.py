
import logging
log = logging.getLogger(__name__)

import loguru
loguru.logger.disable("androguard")
# Optionally change the log level of androguard with remove/add.
#logger.remove()
#logger.add(sys.stderr, level="WARNING")

import argparse
import sys
import argcomplete

import thirdparty.apkd.apk as apkd_apk
import thirdparty.apkd.util as apkd_util


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

    # --- apkd emu search
    apkd_emu_search_parser = apkd_emu_subparsers.add_parser("search")
    apkd_emu_search_parser.add_argument("query", default="*")
    apkd_emu_search_parser.set_defaults(func=apkd_emu_search_func)

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
    apkd_emu_ps_parser.add_argument('-a', required=False, default=False, dest="all_avds", action="store_true")
    apkd_emu_ps_parser.set_defaults(func=apkd_emu_ps_func)

    # --- apkd emu start
    apkd_emu_start_parser = apkd_emu_subparsers.add_parser("start")
    apkd_emu_start_parser.add_argument("name")
    apkd_emu_start_parser.set_defaults(func=apkd_emu_start_func)

    # --- apkd emu gui
    apkd_emu_gui_parser = apkd_emu_subparsers.add_parser("gui")
    apkd_emu_gui_parser.add_argument("name")
    apkd_emu_gui_parser.set_defaults(func=apkd_emu_gui_func)

    # --- apkd emu logs
    apkd_emu_logs_parser = apkd_emu_subparsers.add_parser("logs")
    apkd_emu_logs_parser.add_argument("name")
    apkd_emu_logs_parser.set_defaults(func=apkd_emu_logs_func)

    # --- apkd emu stop
    apkd_emu_stop_parser = apkd_emu_subparsers.add_parser("stop")
    apkd_emu_stop_parser.add_argument("name")
    apkd_emu_stop_parser.set_defaults(func=apkd_emu_stop_func)





    # # --- apkd runtime
    # apkd_runtime_parser = apkd_subparsers.add_parser("runtime", help="Android runtime management")
    # apkd_runtime_subparsers = apkd_runtime_parser.add_subparsers(dest="runtime_command", required=True)

    # # --- apkd runtime deploy
    # apkd_runtime_deploy_parser = apkd_runtime_subparsers.add_parser("deploy")
    # apkd_runtime_deploy_parser.add_argument("--as-apk", action="store_true", default=False, required=False)
    # apkd_runtime_deploy_parser.add_argument("application")
    # apkd_runtime_deploy_parser.set_defaults(func=apkd_runtime_deploy_func)

    # # --- apkd runtime stage
    # apkd_runtime_stage_parser = apkd_runtime_subparsers.add_parser("stage")
    # apkd_runtime_stage_parser.add_argument("--as-pkgname", action="store_true", default=False, required=False)
    # apkd_runtime_stage_parser.add_argument("application")
    # apkd_runtime_stage_parser.set_defaults(func=apkd_runtime_stage_func)

    # # --- apkd runtime connect
    # apkd_runtime_connect_parser = apkd_runtime_subparsers.add_parser("connect")
    # apkd_runtime_connect_parser.add_argument("application")
    # apkd_runtime_connect_parser.set_defaults(func=apkd_runtime_connect_func)

    # # --- apkd runtime easy_debug
    # apkd_runtime_easy_debug_parser = apkd_runtime_subparsers.add_parser("easy_debug")
    # apkd_runtime_easy_debug_parser.add_argument("application")
    # apkd_runtime_easy_debug_parser.set_defaults(func=apkd_runtime_easy_debug_func)




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

    # Default config
    config = baseline_empty_config()
    # Default config path
    config_path = apkd_util.xdg_config_home() / "apkd" / "config.yaml"
    if args.config:
        config_path = Path(args.config)
    if config_path.exists():
        config = load_apkd_config(config_path=config_path)
    else:
        print(f"Config not found at: {config_path}, using defaults.")
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

def apkd_emu_search_func(args, config):
    from thirdparty.apkd.emu.sysimgs import list_system_images
    list_system_images(config, args.query)


# Old Way: apkd emu pull "system-images;android-33;default;x86_64"
# New Way: apkd emu pull system-images/android-33/default/x86_64
def apkd_emu_pull_func(args, config):
    import subprocess
    print(f"Pulling {args.spec}")
    result = subprocess.run(['android', 'sdk', 'install', args.spec], check=True)


def apkd_emu_images_func(args, config):
    import subprocess
    result = subprocess.run(['android', 'sdk', 'list', "system-images*"], check=True)


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
    from thirdparty.apkd.emu.inspect import running_avd_names

    # Get all avds
    result = subprocess.run(["emulator", "-list-avds"], capture_output=True, text=True, check=True)
    #subprocess.run(["avdmanager", "list", "avds"], check=True) # this has more complex output
    avd_names = [avd_name for avd_name in result.stdout.splitlines() if avd_name.strip()]

    # Get running avds
    running = running_avd_names()

    if args.all_avds:
        for avd_name in avd_names:
            if avd_name in running:
                print(f"{avd_name} / {running[avd_name]}")
            else:
                print(f"{avd_name}")
    else:
        for avd_name in running:
            print(f"{avd_name} / {running[avd_name]}")



# ! TODO: Consider adb root, adb remount

def apkd_emu_start_func(args, config):
    from thirdparty.apkd.emu.control import apkd_emu_start
    apkd_emu_start(config, args.name)


def apkd_emu_logs_func(args, config):
    # TODO: Add follow and line count.
    try:
        from thirdparty.apkd.emu.logs import find_latest_log, tail_f_simple
        log_path = find_latest_log(config, args.name)
        if log_path is None:
            print(f"Not log file found for {args.name}.")
            exit(1)
        for line in tail_f_simple(log_path):
            print(line, end="")
    except KeyboardInterrupt:
        exit(0)


def apkd_emu_gui_func(args, config):
    from thirdparty.apkd.emu.control import apkd_emu_scrcpy
    apkd_emu_scrcpy(config, args.name)


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


# def apkd_runtime_stage_func(args, config):
#     # TODO: Do deploy
#     # TODO: Tag application as "wait for debugger"
#     # TODO: Make the application start but wait for debugger to attach
#     print("apkd_runtime_stage_func not implemented")

#     # TODO: If we're missing the config, must quit.
#     from thirdparty.apkd.config.load import load_apkd_config
#     config = load_apkd_config()
    
#     adb_host = config["adb"]["default"]["host"]
#     adb_port = int(config["adb"]["default"]["port"])
#     device_name = config["adb"]["default"]["device"]

#     # Package name of working.apk is the target.
#     from pathlib import Path
#     package_name = args.application
#     if not args.as_pkgname:
#         apk_path = Path(args.application).resolve() / "working" / "pkg" / "working.apk"
#         from androguard.core.apk import APK
#         package_name = APK(str(apk_path)).get_package()

#     from ppadb.client import Client as AdbClient
#     client = AdbClient(host=adb_host, port=adb_port)

#     # Connection sanity.
#     print(f'ADB Client Version: {client.version()}')
#     device = client.device(device_name)
#     if device is None:
#         raise RuntimeError(f"No device found with serial '{device_serial}'")

#     # ===== wait for debugging, start app, and listen to jwdp =====

#     # Configure the package_name to wait for debugger on start.
#     cmd = f'am set-debug-app -w {package_name}'
#     print(cmd)
#     print(device.shell(cmd))

#     # Get the main activity name. (Note: This is a bit wonky.)
#     # TODO: Make this more versatile
#     cmd = f'cmd package resolve-activity -c android.intent.category.LAUNCHER {package_name}'
#     print(cmd)
#     pkg_act_info = device.shell(cmd)

#     import re
#     # Get text following "name=" until end of line.
#     pattern = re.compile(r'(?<=name=)\S+')
#     matches = []
#     for line in pkg_act_info.split('\n'):
#         found = pattern.findall(line)
#         matches.extend(found)
#     #print(matches)
        
#     pkg_main_act = matches[0].replace(package_name, f'{package_name}/')
#     print(pkg_main_act)

#     # Start the package_name's main activity.
#     cmd = f'am start -n {pkg_main_act}'
#     print(cmd)
#     device.shell(cmd)

#     import time
#     time.sleep(0.5)

#     # --- Assuming the application is waiting ---

#     # Get the process id (PID) of the running package_name.
#     adb_procs = device.shell(f'ps -A')
#     proc_pid = None
#     for proc in adb_procs.split('\n'):
#         if proc.find(package_name) < 0:
#             continue
#         proc_pid = int(proc.split()[1])
#         break
#     if not proc_pid:
#         print("Target process not found.")
#         exit(1)
        
#     # Port forward internal JDWP port (same as PID) to localhost:8700
#     cmd = f'adb forward tcp:8700 jdwp:{proc_pid}'
#     print(cmd)
#     device.forward('tcp:8700', f'jdwp:{proc_pid}')

#     import time
#     time.sleep(3)

#     # --- Assuming JDWP is now available, we'll use it to start frida ---




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











def apkd_dbg_func(args, config):
    from thirdparty.apkd.dbg.tasks import apkd_dbg_main_task
    apkd_dbg_main_task(args, config)

if __name__ == "__main__":
    main()