# Hard coded base line config, override from disk config, environment, and finally CLI.

import logging
log = logging.getLogger(__name__)

import argparse
import sys
import os
from pathlib import Path

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


@TaskRegistry.register(provides=["extract"])
def apkd_dbg_task_extract(ctx):
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    args = ctx["args"]
    config = ctx["config"]
    active = ctx["active"]

    if args.apk is not None:
        apkd_apk.extract_apk(active.apk, active.base_dir, active.sdk_dir, active.proj_dir, config)

    if active.apk is not None:
        if active.proj_dir.exists():
            print(f"We have apk, but {args.proj_name} already extracted, do nothing.")

            return
        else:
            apkd_apk.extract_apk(active.apk, active.base_dir, active.sdk_dir, active.proj_dir, config)
    else:
        if active.proj_dir.exists():
            print(f"We have no apk and {args.proj_name} already extracted, do nothing.")
            return
        else:
            print("Requested extraction without apk path. Exiting.")
            exit(1)


@TaskRegistry.register(provides=["patch"], depends_on=["extract"])
def apkd_dbg_task_patch(ctx):
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    """
        Assuming all patching is idempotent

        TODO: run through the bool flags for types of patches to apply.
    """

    active = ctx["active"]

    print("Patching manifest")
    manifest_path = active.proj_dir / "working" / "apk" / "AndroidManifest.xml"
    apkd_apk.set_debuggable(str(manifest_path))
    apkd_apk.set_extract_native_libs(str(manifest_path))

    print("Injecting gadget")
    apkd_apk.patch_frida_gadget(active.proj_dir, active.base_dir, ctx["config"], inject_gadget = True, patch_smali = False)


@TaskRegistry.register(provides=["pack"], depends_on=["extract", "patch"])
def apkd_dbg_task_pack(ctx):
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    """
    Repacking assumed to always be unconditional.
    """

    apkd_apk.pack_apk(ctx["active"].proj_dir, ctx["config"])


@TaskRegistry.register(provides=["debugify"], depends_on=["patch", "pack"])
def apkd_dbg_task_debugify(ctx):
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    """
    Let the dependencies do their thing.
    """


@TaskRegistry.register(provides=["emu_pull"])
def apkd_dbg_task_emu_pull(ctx):
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    '''
    if we're here, we have avd. Does the avd exist? Does the avd match image?


    if active.avd is None:
        must provide avd to compare against, exit
    else:
        if active.avd exists:
            if active.image is None:
                do nothing, return
            if active.avd matches active.image:
                we happy, return
            else:
                error, avd must be removed first
        else:
            if image not installed:
                install image
            else:
                we happy, return
    '''

    active = ctx["active"]

    if active.avd is None:
        print("Must provide avd to continue.")
        exit(1)
    else:
        from thirdparty.apkd.emu.inspect import all_avd_names, get_system_image_for_avd
        if active.avd in all_avd_names():
            if active.image is None:
                # AVD exists and no image, nothing to do.
                print(f"AVD {active.avd} exists and no image, nothing to do.")
                return
            avd_image = get_system_image_for_avd(active.avd).get("package_id_slash", '')
            if avd_image == active.image:
                # AVD exists and image matches AVD, nothing to do.
                return
            else:
                print(f"Image mismatch.\nRequested Image: {active.image}\n Existing AVD {active.avd} image: {avd_image}.")
                print("Remove AVD before continuing.")
                exit(1)
        else:
            if active.image is None:
                print("AVD does not exist and no image to pull. Exiting.")
                exit(1)
            if active.image in parse_installed_system_images():
                # This task only for pulling.
                return
            else:
                # Pull it.
                print(f"Pulling {active.image}")
                result = subprocess.run(['android', 'sdk', 'install', active.image], check=True)



@TaskRegistry.register(provides=["emu_create"], depends_on=["emu_pull"])
def apkd_dbg_task_emu_create(ctx):
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    """
    we assume we have image and avd is defined here

    if active.avd exists:
        if active.avd matches active.image:
            we happy, return
        else:
            error, avd must be removed first
    else:
        create avd
    """

    active = ctx["active"]

    from thirdparty.apkd.emu.inspect import all_avd_names
    if active.avd in all_avd_names():
        print(f"AVD {active.avd} already exist. Do nothing.")
        # avd created, nothing to do.
        return
    else:
        from thirdparty.apkd.emu.avdmgr import create_avd
        print(f"Creating AVD {active.avd}.")
        create_avd(args.name, args.package)


@TaskRegistry.register(provides=["emu_start"], depends_on=["emu_create"])
def apkd_dbg_task_emu_start(ctx):
    # TODO: Handle emu_gui
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    """
    we assume that the avd exists and matches image here

    if active.avd running:
        avd running, return
    else:
        start avd
    """

    active = ctx["active"]

    from thirdparty.apkd.emu.inspect import running_avd_names
    if active.avd in running_avd_names():
        print(f"AVD {active.avd} already running. Do nothing.")
        # avd already running
        return
    else:
        from thirdparty.apkd.emu.control import apkd_emu_start
        print(f"Starting AVD {active.avd}.")
        apkd_emu_start(active.base_dir, active.avd)


@TaskRegistry.register(provides=["deploy"], depends_on=["emu_start", "debugify"])
def apkd_dbg_task_deploy(ctx):
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    """
    Deployment assumed to always be unconditional.

    TODO: Consider no deployment if dest apk matches source apk?
    """

    config = ctx["config"]
    active = ctx["active"]

    from thirdparty.apkd.dbg.deploy import deploy_proj
    print(f"Deploying {active.proj_name} to AVD {active.avd}.")
    deploy_proj(active.proj_dir, active.avd, config)



@TaskRegistry.register(provides=["stage"], depends_on=["deploy"])
def apkd_dbg_task_stage(ctx):
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    """
    Staging assumed to always be unconditional.

    TODO: Check for existing stages? Kill any existing staging?
    """

    config = ctx["config"]
    active = ctx["active"]

    from thirdparty.apkd.dbg.stage import stage_proj
    print(f"Staging {active.proj_name} on AVD {active.avd}.")
    stage_proj(active.proj_dir, active.avd, config)


@TaskRegistry.register(provides=["debug"], depends_on=["stage"])
def apkd_dbg_task_debug(ctx):
    log.debug(f"Inside {sys._getframe().f_code.co_name}")

    """
    New debug session assumed to always be unconditional.

    TODO: Reuse existing sessions? Kill any existing sessions?
    """

    import asyncio
    from thirdparty.apkd.dbg.debug import main_with_sandbox
    try:
        asyncio.run(main_with_sandbox())
    except KeyboardInterrupt:
        print("\nExiting debug session.")


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
        
        self.base_dir = config.get("base_dir", None)
        self.sdk_dir = config["sdk"].get("sdk_dir", None)
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

        # Convert string paths to pathlib Paths
        from thirdparty.apkd.config import implicit_sdk_dir, implicit_base_dir, implicit_proj_dir
        if self.base_dir is None:
            self.base_dir = implicit_base_dir()
        self.base_dir = Path(self.base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

        if self.sdk_dir is None:
            self.sdk_dir = implicit_sdk_dir()
        self.sdk_dir = Path(self.sdk_dir).resolve()
        self.sdk_dir.mkdir(parents=True, exist_ok=True)

        if self.proj_dir is None:
            self.proj_dir = implicit_proj_dir(self.proj_name)
        self.proj_dir = Path(self.proj_dir).resolve()
        self.proj_dir.mkdir(parents=True, exist_ok=True)


    def apply_dbg_config_overrides(self, defaults):
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

    ctx = {
        "args": args,
        "config": config,
        "active": ActiveConfig(config, args, args.operation, args.proj_name)
    }
    TaskRegistry.run_one(args.operation, ctx)

    exit(0)

    # # if len(issues):
    # #     print("Can not run command with given arguments.\n\nIssues:")
    # #     for issue in issues:
    # #         print(f"- {issue}")
    # #     exit(1)

    # # - avd requires image or avd
    # # - jdwp/frida require proj
    # # - use_case_name dependencies vary (implicit arguments in config?)
    # #   - debugify
    # #   - deploy - requires proj, emu
    # #   - stage [--no-debugify] [--no-deploy] - requires proj, emu, jdwp/frida


    # # ========= Start to do the things based on operation =========

    # # Whether or not to re-extracted is a bit nuanced. The simple case is we have and 
    # # apk but we have no proj_dir -> extract. If we've already extracted (there is a
    # # proj_dir), we don't want to auto-extract unless instructed because we don't want
    # # to clobber working/. If we get --apk argument, that is equivalent to saying
    # # re-extract. If we get --force-refresh (without --apk), that is also equivalent to
    # # saying re-extract (perhaps even with a rmtree to completely clear things out.)
    # # Having active["apk"] not None does not implicitly mean extract.

    # if active["operation"] in ['debugify', 'deploy', 'stage', 'debug']:
    #     if active["apk"] is None and not proj_dir.exists():
    #         print("No project folder and no apk to extract.")
    #         exit(1)

    #     if active["apk"] and args.apk or not proj_dir.exists() or args.force_refresh:
    #         # No project, do we have an apk?
    #         apkd_apk.do_extraction_process(config, args.apk, args.proj_name)
    #         apkd_apk.apkd_apk_patch_debuggable_manifest(config, args.proj_name)
    #         apkd_apk.patch_in_frida_gadget(config, args.proj_name, True, False) #not args.skip_gadget, not args.skip_smali_patch)
    #         apkd_apk.do_pack_process(config, args.proj_name)

    # # TODO: image / avd / gui
    # """
    #     image is the system-image specification
    #     avd is the name of the vm
    #     if we're given an image, verify the avd matches the image (mismatch throws error)
    #     if we're given an image and the avd does not exist, create it.
    #     if we have an avd (with a matching image), start it (if not already running)
    # """

    # # Get all avds
    # import subprocess
    # from thirdparty.apkd.emu.control import apkd_emu_start
    # result = subprocess.run(["emulator", "-list-avds"], capture_output=True, text=True, check=True)
    # avd_names = [avd_name for avd_name in result.stdout.splitlines() if avd_name.strip()]
    # from thirdparty.apkd.emu.inspect import running_avd_names
    # running = running_avd_names()
    # from thirdparty.apkd.emu.inspect import parse_installed_system_images
    # avail_images_list = parse_installed_system_images("system-images*")
    # avail_images = [img["path"] for img in avail_images_list]

    # # TODO: Untangle this mess.
    # if active["image"] is not None:
    #     if active["avd"] is not None:
    #         if active["avd"] in avd_names:
    #             # If avd exists and does not match image, die.
    #             import json
    #             from thirdparty.apkd.emu.inspect import get_system_image_for_avd
    #             info = get_system_image_for_avd(active["avd"])
    #             """
    #                 {
    #                     "raw_sysdir": "system-images/android-33/default/x86_64/",
    #                     "package_id_slash": "system-images/android-33/default/x86_64",
    #                     "package_id_semicolon": "system-images;android-33;default;x86_64",
    #                     "api_level": "android-33",
    #                     "tag": "default",
    #                     "abi": "x86_64",
    #                     "target": "android-33",
    #                     "abi_type": "x86_64",
    #                     "tag_id": "default"
    #                 }
    #             """
    #             if active["image"] != info["package_id_slash"]:
    #                 print(f"Existing avd {active["avd"]} using image: {info["package_id_slash"]}")
    #                 print(f"  User requested mismatch: {active["image"]}")
    #                 print(f"  Remove the avd to recreate with new image.")
    #                 exit(1)
    #             else:
    #                 # avd exist and matches image, start if not running
    #                 if active["avd"] not in running:
    #                     if active["image"] not in avail_images:
    #                         subprocess.run(['android', 'sdk', 'install', active["image"]], check=True)
    #                     apkd_emu_start(config, active["avd"])
    #         else:
    #             # If avd does not exist, create it.
    #             cmd = ["avdmanager", "create", "avd", "--name", active["avd"], "--package", active["image"]]
    #             subprocess.run(cmd, input="no\n", text=True, check=True)
    #             if active["image"] not in avail_images:
    #                 subprocess.run(['android', 'sdk', 'install', active["image"]], check=True)
    #             apkd_emu_start(config, active["avd"])
    # else:
    #     if active["avd"] is not None:
    #         if active["avd"] not in avd_names:
    #             print("avd does not exist and no image specified.")
    #             exit(1)

    #         if active["avd"] not in running:
    #             print(f"starting avd {active['avd']}.")
    #             apkd_emu_start(config, active["avd"])

    #     else:
    #         print("no avd set, nothing left to do.")
    #         exit(0)
    
    # # --------- At this point we should have a running emu or exit ---------

    # if active["gui"] == "scrcpy":
    #     from thirdparty.apkd.emu.control import apkd_emu_scrcpy
    #     apkd_emu_scrcpy(config, active["avd"])
    # else:
    #     print(f"Unsupported gui option: {active['gui']}")
    #     exit(1)
    

    # if active["operation"] in ['deploy', 'stage', 'debug']:
    #     # TODO: Requires APK
    #     # Do deploy
    #     from thirdparty.apkd.dbg.deploy import apkd_dbg_deploy
    #     print(f"Deploying {active['proj_name']} to {active['avd']}")
    #     apkd_dbg_deploy(config, active, proj_dir)
        

    # if active["operation"] in ['stage', 'debug']:
    #     from thirdparty.apkd.dbg.stage import apkd_dbg_stage
    #     print(f"Staging {active['proj_name']} to {active['avd']}")
    #     apkd_dbg_stage(config, active, proj_dir)

    # if active["operation"] in ['debug']:
    #     import asyncio
    #     from thirdparty.apkd.dbg.debug import main_with_sandbox
    #     asyncio.run(main_with_sandbox())