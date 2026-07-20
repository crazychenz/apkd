# Hard coded base line config, override from disk config, environment, and finally CLI.

import logging
log = logging.getLogger(__name__)

import argparse
import sys

import thirdparty.apkd.apk as apkd_apk
import thirdparty.apkd.util as apkd_util


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

from thirdparty.apkd.dbg.taskmgr import TaskRegistry


'''
- extract
  - depends_on: apk (arg), proj_name (arg)
- proj_dir
  - depends_on: extract
- patch:
  - depends_on: proj_dir
- pack:
  - depends_on: proj_dir
- debugify
  - depends_on: patch, pack
- emu_pull
  - depends_on: image (arg)
- emu_create
  - depends_on: avd (arg), emu_pull
- emu_start
  - depends_on: emu_create
  - provides: emu_gui too.
- adb_uninstall
  - depends_on: emu_start, debugify
- deploy
  - depends_on: debugify, emu_gui (implicitly emu_start)
- stage
  - depends_on: deploy
- debug
  - depends_on: stage
'''


@TaskRegistry.register(provides=["init_args", "apk_path", "proj_name", "image", "avd"])
def apkd_dbg_task_init_args(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["extract"], depends_on=["apk_path", "proj_name"])
def apkd_dbg_task_extract(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["proj_dir"], depends_on=["extract"])
def apkd_dbg_task_proj_dir(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["patch"], depends_on=["proj_dir"])
def apkd_dbg_task_patch(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["pack"], depends_on=["proj_dir"])
def apkd_dbg_task_pack(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["debugify"], depends_on=["patch", "pack"])
def apkd_dbg_task_debugify(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["emu_pull"], depends_on=["image"])
def apkd_dbg_task_emu_pull(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["emu_create"], depends_on=["avd", "emu_pull"])
def apkd_dbg_task_emu_create(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["emu_start"], depends_on=["emu_create"])
def apkd_dbg_task_emu_start(ctx):
    # TODO: Handle emu_gui
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["deploy"], depends_on=["emu_start", "debugify"])
def apkd_dbg_task_deploy(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["stage"], depends_on=["deploy"])
def apkd_dbg_task_stage(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


@TaskRegistry.register(provides=["debug"], depends_on=["stage"])
def apkd_dbg_task_debug(ctx):
    print(f"Running {sys._getframe().f_code.co_name}")


class ActiveConfig:
    def __init__(self, config, args, operation, proj_name):
        
        self._config = config
        self._args = args

        self.force_refresh = False
        self.force_download = False

        self.apk = None
        self.image = None
        self.avd = None
        self.gui = "scrcpy"

        # self.jdwp_port = None
        # self.frida_port = None
        # self.repl_sock = None
        # self.exec_sock = None
        # self.dict_sock = None
        
        self.base_dir = config.get("base_dir", self.base_dir)
        self.sdk_dir = config["sdk"].get("sdk_dir", self.sdk_dir)
        self.proj_dir = None

        # Always required.
        self.operation = operation
        self.proj_name = proj_name

        # Do configuration overrides
        self.apply_dbg_config_overrides(config["dbg"]["defaults"])
        if proj_name in config["projects"] and "dbg" in config["projects"][proj_name]:
            self.apply_dbg_config_overrides(config["projects"][proj_name]["dbg"])

        # Do environment overrides
        self.apply_env_overrides()

        # Do CLI overrides
        self.apply_cli_overrides(args)

    def apply_dbg_config_default_overrides(self, defaults):
        self.apk = defaults.get('apk', self.apk)
        self.image = defaults.get('image', self.image)
        self.avd = defaults.get('avd', self.avd)
        self.gui = defaults.get('gui', self.gui)
        # self.jdwp_port = defaults.get('jdwp_port', self.jdwp_port)
        # self.frida_port = defaults.get('frida_port', self.frida_port)
        # self.repl_sock = defaults.get('repl_sock', self.repl_sock)
        # self.exec_sock = defaults.get('exec_sock', self.exec_sock)
        # self.dict_sock = defaults.get('dict_sock', self.dict_sock)
        # self.proj_dir = defaults.get('proj_dir', self.proj_dir)

        # ** dbg defaults can not override these authoritative?
        # self.base_dir = defaults.get('base_dir', self.base_dir)
        # self.sdk_dir = defaults.get('sdk_dir', self.sdk_dir)


    def apply_env_overrides(self):
        self.apk = os.environ.get('APKD_DBG_APK', self.apk)
        self.image = os.environ.get('APKD_DBG_IMAGE', self.image)
        self.avd = os.environ.get('APKD_DBG_AVD', self.avd)
        self.gui = os.environ.get('APKD_DBG_GUI', self.gui)
        # self.jdwp_port = os.environ.get('APKD_DBG_JDWP_PORT', self.jdwp_port)
        # self.frida_port = os.environ.get('APKD_DBG_FRIDA_PORT', self.frida_port)
        # self.repl_sock = os.environ.get('APKD_DBG_REPL_SOCK', self.repl_sock)
        # self.exec_sock = os.environ.get('APKD_DBG_EXEC_SOCK', self.exec_sock)
        # self.dict_sock = os.environ.get('APKD_DBG_DICT_SOCK', self.dict_sock)
        # self.proj_dir = os.environ.get('APKD_DBG_PROJ_DIR', self.proj_dir)

        # ** config module overrides these for env
        # self.base_dir = os.environ.get('APKD_DBG_BASE_DIR', self.base_dir)
        # self.sdk_dir = os.environ.get('APKD_DBG_SDK_DIR', self.sdk_dir)


    def apply_cli_overrides(self, args):
        self.apk = args.apk if args.apk is not None else self.apk
        self.image = args.image if args.image is not None else self.image
        self.avd = args.avd if args.avd is not None else self.avd
        self.gui = args.gui if args.gui is not None else self.gui
        # self.jdwp_port = args.jdwp_port if args.jdwp_port is not None else self.jdwp_port
        # self.frida_port = args.frida_port if args.frida_port is not None else self.frida_port
        # self.repl_sock = args.repl_sock if args.repl_sock is not None else self.repl_sock
        # self.exec_sock = args.exec_sock if args.exec_sock is not None else self.exec_sock
        # self.dict_sock = args.dict_sock if args.dict_sock is not None else self.dict_sock
        # self.proj_dir = args.proj_dir if args.proj_dir is not None else self.proj_dir

        # ** CLI overrides config here.
        self.base_dir = args.base_dir if args.base_dir is not None else self.base_dir
        self.sdk_dir = args.sdk_dir if args.sdk_dir is not None else self.sdk_dir


def apkd_dbg_main_task(args, config):

    if apkd_util.has_path_delimiter(args.proj_name):
        print("proj_name must not have / or \\. Use --base-dir/--proj-dir to specify path.")
        exit(1)

    ctx = {"active": ActiveConfig(config, args, args.operation, args.proj_name)}
    TaskRegistry.run_one(args.operation, ctx)

    exit(0)

    

    # ** CLI arguments will override config going forward. **

    # if "dbg" not in config or "defaults" not in config["dbg"] or "projects" not in config["dbg"]:
    #     print("Invalid config, please reinitialize with 'apkd config init'.")
    if args.proj_name not in config["projects"]:
        config["projects"][args.proj_name] = {"dbg": {}}

    active = {**active, **config["dbg"]["defaults"]}
    active = {**active, **config["projects"][args.proj_name]["dbg"]}

    # TODO: Override any relevant config from environment variables here.

    # apkd config overrides here
    if args.base_dir:
        config["base_dir"] = args.base_dir
    if args.sdk_dir:
        config["sdk_dir"] = args.sdk_dir

    # apkd dbg specific overrides here.
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
    if args.proj_dir is not None:
        active["proj_dir"] = args.proj_dir

    # --------- Sanity Checks ---------
    # Note: Do not use args below this line.

    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)

    proj_dir = base_dir / "projects" / active["proj_name"]
    if active["proj_dir"]:
        proj_dir = Path(active["proj_dir"]).resolve()

    if not proj_dir.exists() and active["apk"] is None:
        print("There must already be an extracted project or apk specified.")
        exit(1)

    # TODO: If avd provided, check if its already created or if there is an image specified

    # if len(issues):
    #     print("Can not run command with given arguments.\n\nIssues:")
    #     for issue in issues:
    #         print(f"- {issue}")
    #     exit(1)

    # - avd requires image or avd
    # - jdwp/frida require proj
    # - use_case_name dependencies vary (implicit arguments in config?)
    #   - debugify
    #   - deploy - requires proj, emu
    #   - stage [--no-debugify] [--no-deploy] - requires proj, emu, jdwp/frida


    # ========= Start to do the things based on operation =========

    # Whether or not to re-extracted is a bit nuanced. The simple case is we have and 
    # apk but we have no proj_dir -> extract. If we've already extracted (there is a
    # proj_dir), we don't want to auto-extract unless instructed because we don't want
    # to clobber working/. If we get --apk argument, that is equivalent to saying
    # re-extract. If we get --force-refresh (without --apk), that is also equivalent to
    # saying re-extract (perhaps even with a rmtree to completely clear things out.)
    # Having active["apk"] not None does not implicitly mean extract.

    if active["operation"] in ['debugify', 'deploy', 'stage', 'debug']:
        if active["apk"] is None and not proj_dir.exists():
            print("No project folder and no apk to extract.")
            exit(1)

        if active["apk"] and args.apk or not proj_dir.exists() or args.force_refresh:
            # No project, do we have an apk?
            apkd_apk.do_extraction_process(config, args.apk, args.proj_name)
            apkd_apk.apkd_apk_patch_debuggable_manifest(config, args.proj_name)
            apkd_apk.patch_in_frida_gadget(config, args.proj_name, True, False) #not args.skip_gadget, not args.skip_smali_patch)
            apkd_apk.do_pack_process(config, args.proj_name)

    # TODO: image / avd / gui
    """
        image is the system-image specification
        avd is the name of the vm
        if we're given an image, verify the avd matches the image (mismatch throws error)
        if we're given an image and the avd does not exist, create it.
        if we have an avd (with a matching image), start it (if not already running)
    """

    # Get all avds
    import subprocess
    from thirdparty.apkd.emu.control import apkd_emu_start
    result = subprocess.run(["emulator", "-list-avds"], capture_output=True, text=True, check=True)
    avd_names = [avd_name for avd_name in result.stdout.splitlines() if avd_name.strip()]
    from thirdparty.apkd.emu.inspect import running_avd_names
    running = running_avd_names()
    from thirdparty.apkd.emu.inspect import parse_installed_system_images
    avail_images_list = parse_installed_system_images("system-images*")
    avail_images = [img["path"] for img in avail_images_list]

    # TODO: Untangle this mess.
    if active["image"] is not None:
        if active["avd"] is not None:
            if active["avd"] in avd_names:
                # If avd exists and does not match image, die.
                import json
                from thirdparty.apkd.emu.inspect import get_system_image_for_avd
                info = get_system_image_for_avd(active["avd"])
                """
                    {
                        "raw_sysdir": "system-images/android-33/default/x86_64/",
                        "package_id_slash": "system-images/android-33/default/x86_64",
                        "package_id_semicolon": "system-images;android-33;default;x86_64",
                        "api_level": "android-33",
                        "tag": "default",
                        "abi": "x86_64",
                        "target": "android-33",
                        "abi_type": "x86_64",
                        "tag_id": "default"
                    }
                """
                if active["image"] != info["package_id_slash"]:
                    print(f"Existing avd {active["avd"]} using image: {info["package_id_slash"]}")
                    print(f"  User requested mismatch: {active["image"]}")
                    print(f"  Remove the avd to recreate with new image.")
                    exit(1)
                else:
                    # avd exist and matches image, start if not running
                    if active["avd"] not in running:
                        if active["image"] not in avail_images:
                            subprocess.run(['android', 'sdk', 'install', active["image"]], check=True)
                        apkd_emu_start(config, active["avd"])
            else:
                # If avd does not exist, create it.
                cmd = ["avdmanager", "create", "avd", "--name", active["avd"], "--package", active["image"]]
                subprocess.run(cmd, input="no\n", text=True, check=True)
                if active["image"] not in avail_images:
                    subprocess.run(['android', 'sdk', 'install', active["image"]], check=True)
                apkd_emu_start(config, active["avd"])
    else:
        if active["avd"] is not None:
            if active["avd"] not in avd_names:
                print("avd does not exist and no image specified.")
                exit(1)

            if active["avd"] not in running:
                print(f"starting avd {active['avd']}.")
                apkd_emu_start(config, active["avd"])

        else:
            print("no avd set, nothing left to do.")
            exit(0)
    
    # --------- At this point we should have a running emu or exit ---------

    if active["gui"] == "scrcpy":
        from thirdparty.apkd.emu.control import apkd_emu_scrcpy
        apkd_emu_scrcpy(config, active["avd"])
    else:
        print(f"Unsupported gui option: {active['gui']}")
        exit(1)
    

    if active["operation"] in ['deploy', 'stage', 'debug']:
        # TODO: Requires APK
        # Do deploy
        from thirdparty.apkd.dbg.deploy import apkd_dbg_deploy
        print(f"Deploying {active['proj_name']} to {active['avd']}")
        apkd_dbg_deploy(config, active, proj_dir)
        

    if active["operation"] in ['stage', 'debug']:
        from thirdparty.apkd.dbg.stage import apkd_dbg_stage
        print(f"Staging {active['proj_name']} to {active['avd']}")
        apkd_dbg_stage(config, active, proj_dir)

    if active["operation"] in ['debug']:
        import asyncio
        from thirdparty.apkd.dbg.debug import main_with_sandbox
        asyncio.run(main_with_sandbox())