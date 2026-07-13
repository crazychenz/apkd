#!/usr/bin/env python3
"""
For each .dex file in `dex_path`, disassemble it to smali using baksmali
(via subprocess), verify success, then remove the original .dex.

Requires:
    - Java on PATH
    - A baksmali fat jar (https://github.com/baksmali/smali or JesusFreke/smali releases)

Usage:
    python disassemble_and_remove.py /path/to/dex_dir /path/to/baksmali.jar [output_dir]
"""

import os
import sys
import glob
import subprocess


def disassemble_dex(dex_file: str, baksmali_jar: str, out_dir: str) -> bool:
    """Run baksmali on a single dex file. Returns True on success."""
    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        "java", "-jar", baksmali_jar,
        "disassemble",
        dex_file,
        "-o", out_dir,
    ]
    print(' '.join(cmd))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"  baksmali failed (exit {result.returncode})")
        if result.stdout:
            print(f"  stdout: {result.stdout.strip()}")
        if result.stderr:
            print(f"  stderr: {result.stderr.strip()}")
        return False

    return True


def dex_disassemble_and_remove(dex_path: str, baksmali_jar: str, output_prefix: str) -> None:
    os.makedirs(output_prefix, exist_ok=True)

    dex_files = glob.glob(os.path.join(dex_path, "*.dex"))
    if not dex_files:
        print(f"No .dex files found in {dex_path}")
        return

    for dex_file in dex_files:
        base_name = os.path.splitext(os.path.basename(dex_file))[0]
        out_subdir = os.path.join(output_prefix, base_name)

        print(f"Disassembling {dex_file} -> {out_subdir}")
        success = disassemble_dex(dex_file, baksmali_jar, out_subdir)

        if not success:
            print(f"  Skipping removal of {dex_file} (disassembly did not succeed)")
            continue

        # Sanity check: make sure baksmali actually produced output before deleting
        produced_files = glob.glob(os.path.join(out_subdir, "**", "*.smali"), recursive=True)
        if not produced_files:
            print(f"  Warning: no .smali files found in {out_subdir}, keeping {dex_file}")
            continue

        os.remove(dex_file)
        print(f"  OK: {len(produced_files)} smali files written, removed {dex_file}")


# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Usage: python disassemble_and_remove.py <dex_path> <baksmali_jar> [output_dir]")
#         sys.exit(1)

#     dex_path = sys.argv[1]
#     baksmali_jar = sys.argv[2]
#     output_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.join(dex_path, "smali_out")

#     dex_disassemble_and_remove(dex_path, baksmali_jar, output_dir)







"""
Given a root folder containing one subfolder per baksmali output tree,
reassemble each subfolder into a .dex file (via `smali assemble`), named
after the subfolder itself, and place the result in `output_dir`.

Example layout:
    smali_root/
        classes/       -> smali_root/classes/**/*.smali
        classes2/      -> smali_root/classes2/**/*.smali

Produces:
    output_dir/classes.dex
    output_dir/classes2.dex

Usage:
    python reassemble_smali.py /path/to/smali_root /path/to/smali.jar /path/to/output_dir
"""




def reassemble_folder(smali_dir: str, smali_jar: str, out_dex: str) -> bool:
    """Run `smali assemble` on a single smali directory. Returns True on success."""
    cmd = [
        "java", "-jar", smali_jar,
        "assemble",
        smali_dir,
        "-o", out_dex,
    ]
    print(' '.join(cmd))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"  smali assemble failed (exit {result.returncode})")
        if result.stdout:
            print(f"  stdout: {result.stdout.strip()}")
        if result.stderr:
            print(f"  stderr: {result.stderr.strip()}")
        return False

    return True


def dex_reassemble_all(smali_root: str, smali_jar: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    subfolders = [
        d for d in sorted(os.listdir(smali_root))
        if os.path.isdir(os.path.join(smali_root, d))
    ]

    if not subfolders:
        print(f"No subfolders found in {smali_root}")
        return

    for folder_name in subfolders:
        smali_dir = os.path.join(smali_root, folder_name)

        # Skip subfolders that don't actually contain any smali files
        has_smali = glob.glob(os.path.join(smali_dir, "**", "*.smali"), recursive=True)
        if not has_smali:
            print(f"Skipping {smali_dir} (no .smali files found)")
            continue

        out_dex = os.path.join(output_dir, f"{folder_name}.dex")

        print(f"Assembling {smali_dir} -> {out_dex}")
        success = reassemble_folder(smali_dir, smali_jar, out_dex)

        if success and os.path.isfile(out_dex):
            size = os.path.getsize(out_dex)
            print(f"  OK: wrote {out_dex} ({size} bytes)")
        else:
            print(f"  Failed to produce {out_dex}")


# if __name__ == "__main__":
#     if len(sys.argv) < 4:
#         print("Usage: python reassemble_smali.py <smali_root> <smali_jar> <output_dir>")
#         sys.exit(1)

#     smali_root = sys.argv[1]
#     smali_jar = sys.argv[2]
#     output_dir = sys.argv[3]

#     reassemble_all(smali_root, smali_jar, output_dir)