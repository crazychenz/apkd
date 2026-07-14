


def extract_openjdk(tar_gz_path: str, java_home: str) -> None:
    """
    Extract an OpenJDK tar.gz archive into java_home, stripping the
    top-level directory the archive typically ships with (e.g.
    "jdk-21.0.2/") so that java_home/bin, java_home/lib, etc. exist
    directly rather than nested one level deeper.
    """

    import subprocess
    from pathlib import Path

    dest = Path(java_home)
    dest.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "tar",
            "-xzf", tar_gz_path,
            "-C", str(dest),
            "--strip-components=1",
        ],
        check=True,
    )






def setup_android_cmdline_tools(
    zip_path: str = "~/Downloads/commandlinetools-linux-13114758_latest.zip",
    android_home: str = "~/.android",
) -> None:

    import shutil
    import zipfile
    from pathlib import Path
    import os

    def extract_zip_preserving_permissions(zip_path: Path, dest_dir: Path) -> None:
        with zipfile.ZipFile(zip_path) as zf:
            for info in zf.infolist():
                extracted_path = zf.extract(info, path=dest_dir)

                # Unix permission bits live in the top 16 bits of external_attr
                unix_mode = info.external_attr >> 16
                if unix_mode:
                    os.chmod(extracted_path, unix_mode)

    android_home = Path(android_home).expanduser().resolve()
    zip_path = Path(zip_path).expanduser().resolve()

    android_home.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            extracted_path = zf.extract(info, path=android_home)
            unix_mode = info.external_attr >> 16
            if unix_mode:
                os.chmod(extracted_path, unix_mode)

    # # unzip ~/Downloads/commandlinetools-....zip   (extracted into ~/.android)
    # with zipfile.ZipFile(zip_path) as zf:
    #     zf.extractall(android_home)

    cmdline_tools_dir = android_home / "cmdline-tools"
    latest_dir = cmdline_tools_dir / "latest"
    latest_dir.mkdir(parents=True, exist_ok=True)

    # mv * ./latest/  -- move everything in cmdline-tools/ into latest/,
    # except the 'latest' directory itself
    for item in cmdline_tools_dir.iterdir():
        if item.name == "latest":
            continue
        dest = latest_dir / item.name
        shutil.move(str(item), str(dest))

    print(f"cmdline-tools installed at {latest_dir}")


