import logging
log = logging.getLogger(__name__)

import os
import sys

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




