# thirdparty.android.sdk

## thirdparty.android.sdk.clitools

```python
def get_latest_cmdline_tools_url(platform: str = "linux",
                                  xml_url: str = REPO_XML_URL,
                                  base_url: str = BASE_URL)
```

Fetch the download URL for the android commandlinetools via the same XML repo manifest used by android and sdkmanager. Defaults usually work with internet access. Offline setups will override xml_url and base_url to point to internal resources.

## thirdparty.android.sdk.env

```python
def apply_env(base_dir, sdk_dir, installed_buildtools = [])
```

Given the base_dir, and sdk_dir, setup the environment variable for the python process. Optionally provide a list of (ANDROID_HOME) relative paths to buildtools to include in the PATH.

```python
def print_env(base_dir, sdk_dir)
```

Given base_dir and sdk_dir, print out a shell script to apply environment variable to local shell. For use with commands like: `eval "$(apkd sdk env)"` to apply the environment to the local shell. (Also similar to `source .env`).

## thirdparty.android.sdk.init

```python
def download_with_progress(url: str, dest_path: str, chunk_size: int = 8192, bar_width: int = 30)
```

Download target URL to target dest path in an incremental way (similar to curl).

```python
def download_dependencies(sdk_dir, download_dir, misc_downloads=[], no_cache=False)
```

Download a list of dependencies (tuple(upstream_url, cache_name)).


```python
def extract_openjdk(tar_gz_path: str, java_home: str)
```

Given tar.gz and JAVA_HOME, install OpenJDK

```python
def extract_scrcpy(tar_gz_path, android_home)
```

Given tar.gz and ANDROID_HOME, install scrcpy (i.e. screen copy)

```python
def setup_android_cmdline_tools(
    zip_path: str = "~/Downloads/commandlinetools-linux-13114758_latest.zip",
    android_home: str = "~/.android",
)
```

Given zip and ANDROID_HOME, install android commandlinetools
