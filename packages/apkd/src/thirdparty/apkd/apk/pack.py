import logging
log = logging.getLogger(__name__)

import os
import sys
import shutil
from pathlib import Path
import thirdparty.apkd.util as apkd_util

def should_store_uncompressed(arcname: str) -> bool:
    if arcname == "resources.arsc":
        return True
    if arcname.startswith("lib/") and arcname.endswith(".so"):
        return True
    return False


def build_apk_zip(src_dir: str, out_zip: str, use_compression:bool=False) -> None:
    import zipfile
    with zipfile.ZipFile(out_zip, "w") as zf:
        for root, _dirs, files in os.walk(src_dir):
            for fname in files:
                full_path = os.path.join(root, fname)
                arcname = os.path.relpath(full_path, src_dir).replace(os.sep, "/")

                if use_compression:
                    compress_type = (
                        zipfile.ZIP_STORED
                        if should_store_uncompressed(arcname)
                        else zipfile.ZIP_DEFLATED
                    )

                    zf.write(full_path, arcname, compress_type=compress_type)
                else:
                    # Things are more simple if we do not use compression.
                    zf.write(full_path, arcname, compress_type=zipfile.ZIP_STORED)

    print(f"Wrote {out_zip}")


def detect_zipalign_args(apk_path, zipalign_path="zipalign", candidates=(4, 8, 16)):
    import zipfile
    import subprocess
    import struct
    """Return the zipalign args (e.g. ['-p', '4']) that reproduce apk_path's alignment."""
    align = next(
        (c for c in candidates
         if subprocess.run([zipalign_path, '-c', '-v', str(c), apk_path],
                            capture_output=True).returncode == 0),
        4,
    )

    page_aligned = False
    with zipfile.ZipFile(apk_path) as zf, open(apk_path, 'rb') as f:
        for info in zf.infolist():
            if info.filename.endswith('.so') and info.compress_type == zipfile.ZIP_STORED:
                f.seek(info.header_offset)
                name_len, extra_len = struct.unpack('<HH', f.read(30)[26:30])
                data_offset = info.header_offset + 30 + name_len + extra_len
                page_aligned = data_offset % 4096 == 0
                break

    return (['-p', str(align)] if page_aligned else [str(align)])


def apply_source_alignment(src_apk, dst_apk, out_apk, zipalign_path="zipalign"):
    import subprocess
    import shutil
    if shutil.which(zipalign_path) is None:
        raise FileNotFoundError("zipalign not found on PATH — check your Android SDK build-tools installation")

    args = detect_zipalign_args(src_apk, zipalign_path=zipalign_path)
    subprocess.run([zipalign_path, '-f', *args, dst_apk, out_apk], check=True)


def do_pack_process(config, proj_name):

    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)

    apkalias_path = Path(base_dir / "projects" / proj_name).resolve()
    working_apk_path = apkalias_path / "working" / "apk"

    # Initially copy working/apk to .build/apk
    build_apk_path = apkalias_path / ".build" / "apk"
    shutil.copytree(str(working_apk_path), str(build_apk_path), symlinks=True, dirs_exist_ok=True)

    # Encode AndroidManifest.xml
    working_manifest_path = working_apk_path / "AndroidManifest.xml"
    build_resources_path = build_apk_path / "AndroidManifest.xml"
    from thirdparty.apkd.apk.manifest import encode_manifest
    encode_manifest(str(working_manifest_path), str(build_resources_path))

    # Encode resource.arsc
    # ! Encoding not working, disabling.
    # build_resources_path = build_apk_path / "resources.arsc"
    # working_resources_path = working_apk_path / "resources.arsc"
    # from thirdparty.apkd.apk.resources import resources_from_textproto
    # resources_from_textproto(str(working_resources_path), str(build_resources_path))

    # Reconstruct all dex files
    smali_jar = os.path.expandvars(config["sdk"]["jars"]["smali"])
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
    zipalign_path = config["sdk"]["commands"]["zipalign"]
    original_resigned_path = apkalias_path / ".original" / "pkg" / "original-resigned.apk"
    apply_source_alignment(str(original_resigned_path), str(build_unaligned_apk_path), str(build_unsigned_apk_path), zipalign_path=zipalign_path)

    # Sign apk
    working_pkg_path = apkalias_path / "working" / "pkg" / "working.apk"
    from thirdparty.apkd.apk.sign import sign_apk
    sign_apk(config, str(build_unsigned_apk_path), str(working_pkg_path))


