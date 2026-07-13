import logging
log = logging.getLogger(__name__)


def do_extraction_process(config, apk_path, apk_content_path):
    # TODO: If we're missing the config, must quit.
    

    from thirdparty.apkd.apk.extract import create_folder_structure
    from pathlib import Path
    apkalias_path = Path(apk_content_path)
    apkalias_path.resolve()
    create_folder_structure(apkalias_path)

    # Get our own copy of original apk
    original_sig_path = apkalias_path / ".original" / "pkg" / "original-sig.apk"
    import shutil
    shutil.copy2(apk_path, str(original_sig_path))

    # Re-sign our copy of APK for a bit more consistency.
    original_resigned_path = apkalias_path / ".original" / "pkg" / "original-resigned.apk"
    from thirdparty.apkd.apk.sign import sign_apk
    sign_apk(config, original_sig_path, original_resigned_path)

    # Extract content from original-resigned.apk
    original_apk_path = apkalias_path / ".original" / "apk"
    from thirdparty.apkd.apk.extract import extract_zip
    extract_zip(str(original_resigned_path), str(original_apk_path))

    # Extract original to working
    working_apk_path = apkalias_path / "working" / "apk"
    from thirdparty.apkd.apk.extract import extract_zip
    extract_zip(str(original_resigned_path), str(working_apk_path))

    # Decode manifest.
    original_manifest_path = original_apk_path / "AndroidManifest.xml"
    working_manifest_path = working_apk_path / "AndroidManifest.xml"
    from thirdparty.apkd.apk.manifest import androguard_decode_manifest
    androguard_decode_manifest(str(original_manifest_path), str(working_manifest_path))

    # Decode resources.
    original_resources_path = original_apk_path / "resources.arsc"
    working_resources_path = working_apk_path / "resources.arsc"
    from thirdparty.apkd.apk.resources import resources_to_textproto
    resources_to_textproto(str(original_resources_path), str(working_resources_path))

    # Extract dex with baksmali and remove dex file.
    baksmali_jar = config["jars"]["baksmali"]
    working_dex_prefix = apkalias_path / "working" / "dex"
    from thirdparty.apkd.apk.dex import dex_disassemble_and_remove
    dex_disassemble_and_remove(str(working_apk_path), baksmali_jar, working_dex_prefix)


def do_pack_process(config, apk_content_path):
    from thirdparty.apkd.config.load import load_apkd_config
    config = load_apkd_config()
    
    from pathlib import Path
    apkalias_path = Path(apk_content_path)
    apkalias_path.resolve()
    working_apk_path = apkalias_path / "working" / "apk"

    # Initially copy working/apk to .build/apk
    build_apk_path = apkalias_path / ".build" / "apk"
    import shutil
    shutil.copytree(str(working_apk_path), str(build_apk_path), symlinks=True, dirs_exist_ok=True)

    # Encode AndroidManifest.xml
    working_manifest_path = working_apk_path / "AndroidManifest.xml"
    build_resources_path = build_apk_path / "AndroidManifest.xml"
    from thirdparty.apkd.apk.manifest import encode_manifest
    encode_manifest(str(working_manifest_path), str(build_resources_path))

    # Encode resource.arsc
    build_resources_path = build_apk_path / "resources.arsc"
    working_resources_path = working_apk_path / "resources.arsc"
    from thirdparty.apkd.apk.resources import resources_from_textproto
    resources_from_textproto(str(working_resources_path), str(build_resources_path))

    # Reconstruct all dex files
    smali_jar = config["jars"]["smali"]
    working_dex_prefix = apkalias_path / "working" / "dex"
    from thirdparty.apkd.apk.dex import dex_reassemble_all
    dex_reassemble_all(working_dex_prefix, smali_jar, build_apk_path)

    # Build unaligned APK
    build_unaligned_apk_path = apkalias_path / ".build" / "pkg" / "unaligned.apk"
    build_unsigned_apk_path = apkalias_path / ".build" / "pkg" / "unsigned.apk"
    from thirdparty.apkd.apk.pack import build_apk_zip
    build_apk_zip(build_apk_path, build_unaligned_apk_path)

    # Build unsigned (i.e. aligned) apk
    from thirdparty.apkd.apk.pack import apply_source_alignment
    zipalign_path = config["binaries"]["zipalign"]
    original_resigned_path = apkalias_path / ".original" / "pkg" / "original-resigned.apk"
    apply_source_alignment(str(original_resigned_path), str(build_unaligned_apk_path), str(build_unsigned_apk_path), zipalign_path=zipalign_path)

    # Sign apk
    working_pkg_path = apkalias_path / "working" / "pkg" / "working.apk"
    from thirdparty.apkd.apk.sign import sign_apk
    sign_apk(config, str(build_unsigned_apk_path), str(working_pkg_path))