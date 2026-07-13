
import logging
log = logging.getLogger(__name__)


import argparse
import sys
import argcomplete


def init_argparse():
    # --- apkd
    apkd_parser = argparse.ArgumentParser(prog="apkd")
    #apkd_parser.add_argument("--config", dest="config", action="store", help="config.yaml")
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
    # TODO: Allow a config path.
    #apkd_config_init_parser.add_argument("config_path")
    apkd_config_init_parser.set_defaults(func=apkd_config_init_func)

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
    apkd_apk_extract_parser.add_argument("apk_content_path")
    apkd_apk_extract_parser.set_defaults(func=apkd_apk_extract_func)

    # --- apkd apk patch
    apkd_apk_patch_parser = apkd_apk_subparsers.add_parser("patch")
    apkd_apk_patch_subparsers = apkd_apk_patch_parser.add_subparsers(dest="apk_patch_command", required=True)

    # --- apkd apk patch debug
    apkd_apk_patch_debug_parser = apkd_apk_patch_subparsers.add_parser("debug")
    apkd_apk_patch_debug_parser.add_argument("apk_content_path")
    apkd_apk_patch_debug_parser.set_defaults(func=apkd_apk_patch_debug_func)

    # --- apkd apk patch frida
    apkd_apk_patch_frida_parser = apkd_apk_patch_subparsers.add_parser("frida")
    apkd_apk_patch_frida_parser.add_argument("apk_content_path")
    apkd_apk_patch_frida_parser.set_defaults(func=apkd_apk_patch_frida_func)

    # --- apkd apk pack
    apkd_apk_pack_parser = apkd_apk_subparsers.add_parser("pack")
    apkd_apk_pack_parser.add_argument('--ks', dest="keystore")
    apkd_apk_pack_parser.add_argument('--kspass', dest="kspass")
    apkd_apk_pack_parser.add_argument('--key', dest="keyname")
    apkd_apk_pack_parser.add_argument('--keypass', dest="keypass")
    apkd_apk_pack_parser.add_argument("apk_content_path")
    #apkd_apk_pack_parser.add_argument("new_apk_path")
    apkd_apk_pack_parser.set_defaults(func=apkd_apk_pack_func)

    # --- apkd apk debugify
    apkd_apk_debugify_parser = apkd_apk_subparsers.add_parser("debugify")
    apkd_apk_debugify_parser.add_argument("apk_path")
    apkd_apk_debugify_parser.add_argument("apk_content_path")
    apkd_apk_debugify_parser.add_argument("new_apk_path")
    apkd_apk_debugify_parser.set_defaults(func=apkd_apk_debugify_func)

    # --- apkd emu
    apkd_emu_parser = apkd_subparsers.add_parser("emu", help="Android emulator management")
    apkd_emu_subparsers = apkd_emu_parser.add_subparsers(dest="emu_command", required=True)

    # --- apkd emu get
    apkd_emu_get_parser = apkd_emu_subparsers.add_parser("get")
    apkd_emu_get_parser.add_argument("spec")
    apkd_emu_get_parser.set_defaults(func=apkd_emu_get_func)

    # --- apkd emu create
    apkd_emu_create_parser = apkd_emu_subparsers.add_parser("create")
    apkd_emu_create_parser.set_defaults(func=apkd_emu_create_func)

    # --- apkd emu start
    apkd_emu_start_parser = apkd_emu_subparsers.add_parser("start")
    apkd_emu_start_parser.set_defaults(func=apkd_emu_start_func)

    # --- apkd emu stop
    apkd_emu_stop_parser = apkd_emu_subparsers.add_parser("stop")
    apkd_emu_stop_parser.set_defaults(func=apkd_emu_stop_func)

    # --- apkd runtime
    apkd_runtime_parser = apkd_subparsers.add_parser("runtime", help="Android runtime management")
    apkd_runtime_subparsers = apkd_runtime_parser.add_subparsers(dest="runtime_command", required=True)

    # --- apkd runtime deploy
    apkd_runtime_deploy_parser = apkd_runtime_subparsers.add_parser("deploy")
    apkd_runtime_deploy_parser.add_argument("application")
    apkd_runtime_deploy_parser.set_defaults(func=apkd_runtime_deploy_func)

    # --- apkd runtime stage
    apkd_runtime_stage_parser = apkd_runtime_subparsers.add_parser("stage")
    apkd_runtime_stage_parser.add_argument("application")
    apkd_runtime_stage_parser.set_defaults(func=apkd_runtime_stage_func)

    # --- apkd runtime listen
    apkd_runtime_listen_parser = apkd_runtime_subparsers.add_parser("listen")
    apkd_runtime_listen_parser.add_argument("application")
    apkd_runtime_listen_parser.set_defaults(func=apkd_runtime_listen_func)

    # --- apkd runtime connect
    apkd_runtime_connect_parser = apkd_runtime_subparsers.add_parser("connect")
    apkd_runtime_connect_parser.add_argument("application")
    apkd_runtime_connect_parser.set_defaults(func=apkd_runtime_connect_func)

    # --- apkd runtime easy_debug
    apkd_runtime_easy_debug_parser = apkd_runtime_subparsers.add_parser("easy_debug")
    apkd_runtime_easy_debug_parser.add_argument("application")
    apkd_runtime_easy_debug_parser.set_defaults(func=apkd_runtime_easy_debug_func)

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

    args.func(args)


def apkd_config_init_func(args):
    import os
    import yaml
    from pathlib import Path

    config_dir = Path(os.environ["HOME"]) / ".config" / "apkd"

    if config_dir.exists():
        print(f"Error: {config_dir} configuration folder exists. Remove and retry to initialize.", file=sys.stderr)
        sys.exit(1)

    config_dir.mkdir(parents=True)

    config = {
        "binaries": {
            "java": "java",
            "keytool": "keytool",
            "zipalign": "zipalign",
            "apksigner": "apksigner",
        },
        "jars": {
            "apksigner": "apksigner.jar",
            "baksmali": "baksmali.jar",
            "smali": "smali.jar",
            "apktool": "apktool.jar",
        },
        "default_keystore": "default",
        "default_keyalias": "default",
        "keystores": {
            "default": {
                "kspass": "default",
                "keys": {
                    "default": {
                        "keypass": "default",
                        "dn": "CN=apkd, OU=apkd, O=apkd, L=Unknown, ST=Unknown, C=US",
                    },
                },
            },
        },
    }

    with open(str(config_dir / "config.yaml"), "w") as f:
        yaml.dump(config, f)
    
    from thirdparty.apkd.config.init import create_keystore
    
    ks_name = config["default_keystore"]
    ks_prefix = config_dir / "keystores"
    ks_config = config["keystores"][ks_name]
    key_alias = config["default_keyalias"]
    key_config = ks_config["keys"][key_alias]
    ks_pass = ks_config["kspass"]
    key_pass = key_config["keypass"]
    dname = key_config["dn"]

    create_keystore(str(ks_prefix), ks_pass, key_pass, keystore_name=ks_name, key_alias=key_alias, dname=dname)


def apkd_apk_ls_func(args):
    from thirdparty.apkd.apk.ls import list_zip_like_ls
    list_zip_like_ls(args.apk_path)


def apkd_apk_manifest_func(args):
    from thirdparty.apkd.apk.manifest import get_manifest
    print(get_manifest(args.apk_path))


def apkd_apk_resources_func(args):
    print("apkd_apk_resources_func not implemented")


def apkd_apk_extract_func(args):

    # TODO: If we're missing the config, must quit.
    from thirdparty.apkd.config.load import load_apkd_config
    config = load_apkd_config()

    # Extract everything.
    from thirdparty.apkd.apk.lib import do_extraction_process
    do_extraction_process(config, args.apk_path, args.apk_content_path)

    # Rebuild everything.
    from thirdparty.apkd.apk.lib import do_pack_process
    do_pack_process(config, args.apk_content_path)


def apkd_apk_patch_debug_func(args):
    from pathlib import Path
    apkalias_path = Path(args.apk_content_path)
    apkalias_path.resolve()
    working_manifest_path = apkalias_path / "working" / "apk" / "AndroidManifest.xml"
    from thirdparty.apkd.apk.patch import set_debuggable
    set_debuggable(str(working_manifest_path))


def apkd_apk_patch_frida_func(args):
    print("apkd_apk_patch_frida_func not implemented")


def apkd_apk_pack_func(args):

    # TODO: If we're missing the config, must quit.
    from thirdparty.apkd.config.load import load_apkd_config
    config = load_apkd_config()

    # Rebuild everything.
    from thirdparty.apkd.apk.lib import do_pack_process
    do_pack_process(config, args.apk_content_path)


def apkd_apk_debugify_func(args):
    print("apkd_apk_debugify_func not implemented")


def apkd_emu_get_func(args):
    print("apkd_emu_get_func not implemented")


def apkd_emu_create_func(args):
    print("apkd_emu_create_func not implemented")


def apkd_emu_start_func(args):
    print("apkd_emu_start_func not implemented")


def apkd_emu_stop_func(args):
    print("apkd_emu_stop_func not implemented")


def apkd_runtime_deploy_func(args):
    print("apkd_runtime_deploy_func not implemented")


def apkd_runtime_stage_func(args):
    print("apkd_runtime_stage_func not implemented")


def apkd_runtime_listen_func(args):
    print("apkd_runtime_listen_func not implemented")


def apkd_runtime_connect_func(args):
    print("apkd_runtime_connect_func not implemented")


def apkd_runtime_easy_debug_func(args):
    print("apkd_runtime_easy_debug_func not implemented")


if __name__ == "__main__":
    main()