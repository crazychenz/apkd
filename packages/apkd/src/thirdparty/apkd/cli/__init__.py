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
    apkd_apk_parser = apkd_subparsers.add_parser("apk", help="Static APK analysis")
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

    argcomplete.autocomplete(apkd_parser)
    args = apkd_parser.parse_args()
    args.func(args)


def apkd_apk_ls_func(args):
    from thirdparty.apkd.apk.ls import list_zip_like_ls
    list_zip_like_ls(args.apk_path)


def apkd_apk_extract_func(args):
    from pathlib import Path
    import shutil

    # Do we have config and key?
    # - No? ... tell user to config init and bail.

    folders = {
        ".original": ["pkg", "apk"],
        "working": ["apk", "dex", "pkg", "elf"],
        ".build": ["pkg", "dex", "apk", "elf"],
    }

    apkalias_path = Path(args.apk_content_path)
    apkalias_path.resolve()
    for tlf in folders:
        for folder in folders[tlf]:
            fpath = apkalias_path / tlf / folder
            fpath.mkdir(parents=True, exist_ok=True)

    # Get our own copy of original apk
    original_sig_path = apkalias_path / ".original" / "pkg" / "original-sig.apk"
    shutil.copy2(args.apk_path, str(original_sig_path))

    # Re-sign our copy of APK for a bit more consistency.
    original_resigned_path = apkalias_path / ".original" / "pkg" / "original-resigned.apk"
    # ! TODO: Do the re-sign
    # **Temporarily copy original sig as resigned.
    shutil.copy2(args.apk_path, str(original_resigned_path))

    # Extract content from original-resigned.apk
    original_apk_path = apkalias_path / ".original" / "apk"
    from thirdparty.apkd.apk.extract import extract_zip
    extract_zip(str(original_resigned_path), str(original_apk_path))

    # Extract original to working
    working_apk_path = apkalias_path / "working" / "apk"
    from thirdparty.apkd.apk.extract import extract_zip
    extract_zip(str(original_resigned_path), str(working_apk_path))
    #

    # Decode manifest.
    original_manifest_path = original_apk_path / "AndroidManifest.xml"
    working_manifest_path = working_apk_path / "AndroidManifest.xml"
    from thirdparty.apkd.apk.manifest import decode_manifest
    decode_manifest(str(original_manifest_path), str(working_manifest_path))

    # Decode resources.
    original_resources_path = original_apk_path / "resources.arsc"
    working_resources_path = working_apk_path / "resources.arsc"
    from thirdparty.apkd.apk.resources import resources_to_textproto
    resources_to_textproto(str(original_resources_path), str(working_resources_path))

    # Extract dex and remove
    # TODO: Fetch baksmali_jar from config
    baksmali_jar = "./cache/baksmali-3.0.9-fat.jar"
    working_dex_prefix = apkalias_path / "working" / "dex"
    from thirdparty.apkd.apk.dex import dex_disassemble_and_remove
    dex_disassemble_and_remove(str(working_apk_path), baksmali_jar, working_dex_prefix)

    # --- Rebuild everything ---

    # Initially copy working/apk to .build/apk
    build_apk_path = apkalias_path / ".build" / "apk"
    shutil.copytree(str(working_apk_path), str(build_apk_path), symlinks=True, dirs_exist_ok=True)

    # Encode AndroidManifest.xml
    build_resources_path = build_apk_path / "AndroidManifest.xml"
    from thirdparty.apkd.apk.manifest import encode_manifest
    encode_manifest(str(working_manifest_path), str(build_resources_path))

    # Encode resource.arsc
    build_resources_path = build_apk_path / "resources.arsc"
    from thirdparty.apkd.apk.resources import resources_from_textproto
    resources_from_textproto(str(working_resources_path), str(build_resources_path))

    # Reconstruct all dex files
    from thirdparty.apkd.apk.dex import dex_reassemble_all
    dex_reassemble_all(working_dex_prefix, baksmali_jar, build_apk_path)

    # Build unaligned APK
    build_unaligned_apk_path = apkalias_path / ".build" / "pkg" / "unaligned.apk"
    build_unsigned_apk_path = apkalias_path / ".build" / "pkg" / "unsigned.apk"
    working_pkg_path = apkalias_path / "working" / "pkg"
    working_apk_path = working_pkg_path / "working.apk"
    from thirdparty.apkd.apk.pack import build_apk_zip
    build_apk_zip(build_apk_path, build_unaligned_apk_path)

    # Build unsigned (i.e. aligned) apk
    from thirdparty.apkd.apk.pack import apply_source_alignment
    apply_source_alignment(str(original_resigned_path), str(build_unaligned_apk_path), str(build_unsigned_apk_path))

    # TODO: Sign apk
    # cmd = [
    #     'apksigner', 'sign',
    #     '--ks', args.keystore,
    #     '--ks-key-alias', args.keyname,
    #     '--ks-pass', f'pass:{args.kspass}',
    #     '--key-pass', f'pass:{args.keypass}',
    #     '--out', str(working_apk_path),
    #     str(unsigned_apk_path),
    # ]
    # subprocess.run(cmd, check=True)


def apkd_apk_patch_debug_func(args):
    print("apkd_apk_patch_debug_func not implemented")


def apkd_apk_patch_frida_func(args):
    print("apkd_apk_patch_frida_func not implemented")


def apkd_apk_pack_func(args):
    from thirdparty.apkd.apk.pack import encode_manifest, apply_source_alignment
    from pathlib import Path
    import shutil
    import subprocess

    original_apk_path = Path(args.apk_content_path) / "original.apk"
    original_apk_path.resolve()
    unaligned_apk_path = Path(args.apk_content_path) / "unaligned.apk"
    unaligned_apk_path.resolve()
    unsigned_apk_path = Path(args.apk_content_path) / "unsigned.apk"
    unsigned_apk_path.resolve()
    working_apk_path = Path(args.apk_content_path) / "working.apk"
    working_apk_path.resolve()

    apk_working_path = Path(args.apk_content_path) / "working"
    apk_working_path.resolve()
    apk_build_path = Path(args.apk_content_path) / "build"
    apk_build_path.resolve()

    # Mirror working into build
    shutil.rmtree(str(apk_build_path))
    shutil.copytree(str(apk_working_path), str(apk_build_path), symlinks=True, dirs_exist_ok=True)

    # Encode apk
    working_manifest_path = apk_working_path / "AndroidManifest.xml"
    build_manifest_path = apk_build_path / "AndroidManifest.xml"
    encode_manifest(str(working_manifest_path), str(build_manifest_path))

    # Build unaligned apk
    # ! TODO: We must use apktool to extract to use it for building. It needs a yml metadata file.
    apktool_cmd = 'java -jar ./cache/tools/apktool_2.12.0.jar'
    cmd = [*apktool_cmd.split(), 'b', '-o', str(unaligned_apk_path), str(apk_build_path)]
    print(' '.join(cmd))
    subprocess.run(cmd, check=True)

    # Build unsigned apk
    apply_source_alignment(str(original_apk_path), str(unaligned_apk_path), str(unsigned_apk_path))
    
    # apksigner sign
    # cmd = [
    #     'apksigner', 'sign',
    #     '--ks', args.keystore,
    #     '--ks-key-alias', args.keyname,
    #     '--ks-pass', f'pass:{args.kspass}',
    #     '--key-pass', f'pass:{args.keypass}',
    #     '--out', str(working_apk_path),
    #     str(unsigned_apk_path),
    # ]
    # subprocess.run(cmd, check=True)


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