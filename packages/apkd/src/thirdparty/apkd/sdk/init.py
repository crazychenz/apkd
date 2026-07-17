
import os
import subprocess
from pathlib import Path

import thirdparty.apkd.util as apkd_util
from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir


def apkd_sdk_download_dependencies(base_dir, sdk_dir, download_dir, config=None, no_cache=False):
    download_dir.mkdir(parents=True, exist_ok=True)
    sdk_dir.mkdir(parents=True, exist_ok=True)

    # TODO: Make the platform more dynamic.
    sdk_urls = config["downloads"]["android-sdk-clitools"]["linux"]
    repo_xml_url = sdk_urls["repo-xml-url"]
    clitools_base_url = sdk_urls["base-url"]

    # Seed the Android SDK
    download_dest = download_dir / sdk_urls["cache"]
    if not download_dest.exists():
        from thirdparty.apkd.sdk.clitools import get_latest_cmdline_tools_url
        clitools_url = get_latest_cmdline_tools_url(platform="linux", xml_url=repo_xml_url, base_url=clitools_base_url)
        print(f"Downloading package:\n  URL: {clitools_url}\n  Path: {download_dest}")
        apkd_util.download_with_progress(clitools_url, download_dest)
    else:
        print(f"Skipping {download_dest} downloads. File exists.")

    # Setup Java, Scrcpy, and others.
    # TODO: Make the platform more dynamic.
    for download in config["downloads"]["linux-x64"].values():
        download_dest = download_dir / download["cache"]
        if not download_dest.exists():
            print(f"Downloading package:\n  URL: {download['upstream']}\n  Path: {download_dest}")
            apkd_util.download_with_progress(download['upstream'], download_dest)
        else:
            print(f"Skipping {download_dest} downloads. File exists.")

    # Setup jars
    for download in config["downloads"]["java"].values():
        download_dest = download_dir / download["cache"]
        if not download_dest.exists():
            print(f"Downloading jar:\n  URL: {download['upstream']}\n  Path: {download_dest}")
            apkd_util.download_with_progress(download['upstream'], download_dest)
        else:
            print(f"Skipping {download_dest} downloads. File exists.")

    # Setup frida gadgets
    for download in config["downloads"]["frida"]["gadget"].values():
        download_dest = download_dir / download["cache"]
        if not download_dest.exists():
            print(f"Downloading frida gadget:\n  URL: {download['upstream']}\n  Path: {download_dest}")
            apkd_util.download_with_progress(download['upstream'], download_dest)
        else:
            print(f"Skipping {download_dest} downloads. File exists.")

    # Setup frida servers
    for download in config["downloads"]["frida"]["server"].values():
        download_dest = download_dir / download["cache"]
        if not download_dest.exists():
            print(f"Downloading frida server:\n  URL: {download['upstream']}\n  Path: {download_dest}")
            apkd_util.download_with_progress(download['upstream'], download_dest)
        else:
            print(f"Skipping {download_dest} downloads. File exists.")


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


def extract_scrcpy(tar_gz_path, android_home):
    import subprocess
    from pathlib import Path

    dest = Path(android_home) / "scrcpy"
    dest.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "tar",
            "-xf", tar_gz_path,
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
    if Path(latest_dir).exists():
        shutil.rmtree(latest_dir)
    latest_dir.mkdir(parents=True, exist_ok=True)

    # mv * ./latest/  -- move everything in cmdline-tools/ into latest/,
    # except the 'latest' directory itself
    for item in cmdline_tools_dir.iterdir():
        if item.name == "latest":
            continue
        dest = latest_dir / item.name
        shutil.move(str(item), str(dest))

    print(f"cmdline-tools installed at {latest_dir}")


def apkd_sdk_init(config=None, no_cache=False):

    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)
    download_dir = base_dir / "downloads"

    apkd_sdk_download_dependencies(base_dir, sdk_dir, download_dir, config=config, no_cache=no_cache)

    clitools_path = download_dir / config["downloads"]["android-sdk-clitools"]["linux"]["cache"]
    setup_android_cmdline_tools(zip_path=str(clitools_path), android_home=str(sdk_dir))

    java_tar_gz = download_dir / config["downloads"]["linux-x64"]["java17"]["cache"]
    extract_openjdk(str(java_tar_gz), str(sdk_dir / "java17"))

    scrcpy_tar_gz = download_dir / config["downloads"]["linux-x64"]["scrcpy"]["cache"]
    extract_scrcpy(str(scrcpy_tar_gz), sdk_dir)

    print("Extracting frida artifacts.")
    # Extract frida gadgets
    for download in config["downloads"]["frida"]["gadget"].values():
        download_dest = download_dir / download["cache"]
        subprocess.run(['unxz', '-k', '-f', str(download_dest)], check=True)

    # Extract frida servers
    for download in config["downloads"]["frida"]["server"].values():
        download_dest = download_dir / download["cache"]
        subprocess.run(['unxz', '-k', '-f', str(download_dest)], check=True)
    
    # Install sdkmanager dependencies
    for pkg in config["downloads"]["sdkmanager"]:
        print(f"Installing {pkg}.")
        subprocess.run(f"yes | android sdk install \"{pkg}\"", shell=True, check=True)




