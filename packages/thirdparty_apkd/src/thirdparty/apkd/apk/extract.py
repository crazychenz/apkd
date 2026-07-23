import logging
log = logging.getLogger(__name__)

import os
import shutil
from pathlib import Path
import thirdparty.apkd.util as apkd_util


def create_folder_structure(apkalias_path):
    from pathlib import Path

    folders = {
        ".original": ["pkg", "apk"],
        "working": ["apk", "dex", "pkg", "elf"],
        ".build": ["pkg", "dex", "apk", "elf"],
    }

    for tlf in folders:
        for folder in folders[tlf]:
            fpath = apkalias_path / tlf / folder
            fpath.mkdir(parents=True, exist_ok=True)


def do_extraction_process(config, apk_path, proj_name):

    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)

    from thirdparty.apkd.apk.extract import create_folder_structure
    proj_dir = Path(base_dir / "projects" / proj_name).resolve()
    extract_apk(apk_path, base_dir, sdk_dir, proj_dir, config)


def extract_apk(apk_path, base_dir, sdk_dir, proj_dir, config): # config only for sign_apk

    create_folder_structure(proj_dir)

    # Get our own copy of original apk
    original_sig_path = proj_dir / ".original" / "pkg" / "original-sig.apk"
    shutil.copy2(apk_path, str(original_sig_path))

    # Re-sign our copy of APK for a bit more consistency.
    original_resigned_path = proj_dir / ".original" / "pkg" / "original-resigned.apk"
    from thirdparty.apkd.apk.sign import sign_apk
    sign_apk(config, original_sig_path, original_resigned_path)

    # Extract content from original-resigned.apk
    original_apk_path = proj_dir / ".original" / "apk"
    apkd_util.extract_zip(str(original_resigned_path), str(original_apk_path))

    # Extract original to working
    working_apk_path = proj_dir / "working" / "apk"
    apkd_util.extract_zip(str(original_resigned_path), str(working_apk_path))

    # Decode manifest.
    original_manifest_path = original_apk_path / "AndroidManifest.xml"
    working_manifest_path = working_apk_path / "AndroidManifest.xml"
    from thirdparty.apkd.apk.manifest import androguard_decode_manifest
    androguard_decode_manifest(str(original_manifest_path), str(working_manifest_path))

    # Decode resources.
    # ! Encoding not working, disabling decoding for now.
    # original_resources_path = original_apk_path / "resources.arsc"
    # working_resources_path = working_apk_path / "resources.arsc"
    # from thirdparty.apkd.apk.resources import resources_to_textproto
    # resources_to_textproto(str(original_resources_path), str(working_resources_path))

    # Extract dex with baksmali and remove dex file.
    baksmali_jar = os.path.expandvars(config["sdk"]["jars"]["baksmali"])
    working_dex_prefix = proj_dir / "working" / "dex"
    from thirdparty.apkd.apk.dex import dex_disassemble_and_remove
    dex_disassemble_and_remove(str(working_apk_path), baksmali_jar, working_dex_prefix)