import argparse
import sys

import argcomplete

def main():
    # --- apkd
    apkd_parser = argparse.ArgumentParser(prog="apkd")
    apkd_parser.add_argument("--config", dest="config", action="store", help="config.yaml")
    apkd_parser.add_argument("--breakpoint", dest="breakpoint", action="store_true", help="breakpoint() after operation")
    apkd_parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity")
    apkd_parser.add_argument(
        "--log-level",
        metavar="MODULE:LEVEL",
        action="append",
        default=[],
        help="Example: --log-level thirdparty.apkd:DEBUG",
    )
    apkd_subparsers = apkd_parser.add_subparsers(dest="category", required=True)

    # --- apkd apk
    apkd_apk_parser = subparsers.add_parser("apk", help="Static APK analysis")
    apkd_apk_subparsers = apkd_apk_parser.add_subparsers(dest="apk_command", required=True)

    # --- apkd apk ls
    apkd_apk_ls_parser = apkd_apk_subparsers.add_parser("ls")
    apkd_apk_ls_parser.add_argument("apk_path")
    apkd_apk_ls_parser.set_defaults(func=apkd_apk_ls_func)

    # --- apkd apk extract
    apkd_apk_extract_parser = apkd_apk_subparsers.add_parser("extract")
    apkd_apk_extract_parser.add_argument("apk_path")
    apkd_apk_extract_parser.add_argument("apk_content_path")
    apkd_apk_extract_parser.set_defaults(func=apkd_apk_extract_func)

    # --- apkd apk patch
    apkd_apk_patch_parser = apkd_apk_subparsers.add_parser("patch")
    apkd_apk_patch_subparsers = apkd_apk_parser.add_subparsers(dest="apk_patch_command", required=True)

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
    apkd_apk_pack_parser.add_argument("apk_content_path")
    apkd_apk_pack_parser.add_argument("new_apk_path")
    apkd_apk_pack_parser.set_defaults(func=apkd_apk_pack_func)

    # --- apkd apk debugify
    apkd_apk_debugify_parser = apkd_apk_subparsers.add_parser("debugify")
    apkd_apk_debugify_parser.add_argument("apk_path")
    apkd_apk_debugify_parser.add_argument("apk_content_path")
    apkd_apk_debugify_parser.add_argument("new_apk_path")
    apkd_apk_debugify_parser.set_defaults(func=apkd_apk_debugify_func)

    # --- apkd emu
    apkd_emu_parser = subparsers.add_parser("emu", help="Android emulator management")
    apkd_emu_subparsers = apkd_emu_parser.add_subparsers(dest="emu_command", required=True)

    # --- apkd emu get
    apkd_emu_get_parser = apkd_emu_parser.add_parser("get")
    apkd_emu_get_parser.add_argument("spec")
    apkd_emu_get_parser.set_defaults(func=apkd_emu_get_func)

    # --- apkd emu create
    apkd_emu_create_parser = apkd_emu_parser.add_parser("create")
    apkd_emu_create_parser.set_defaults(func=apkd_emu_create_func)

    # --- apkd emu start
    apkd_emu_start_parser = apkd_emu_parser.add_parser("start")
    apkd_emu_start_parser.set_defaults(func=apkd_emu_start_func)

    # --- apkd emu stop
    apkd_emu_stop_parser = apkd_emu_parser.add_parser("stop")
    apkd_emu_stop_parser.set_defaults(func=apkd_emu_stop_func)

    # --- apkd runtime
    apkd_runtime_parser = subparsers.add_parser("runtime", help="Android runtime management")
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

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args.func(args)


def apkd_apk_ls_func(args):
    print("apkd_apk_ls_func not implemented")


def apkd_apk_extract_func(args):
    print("apkd_apk_extract_func not implemented")


def apkd_apk_patch_debug_func(args):
    print("apkd_apk_patch_debug_func not implemented")


def apkd_apk_patch_frida_func(args):
    print("apkd_apk_patch_frida_func not implemented")


def apkd_apk_pack_func(args):
    print("apkd_apk_pack_func not implemented")


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