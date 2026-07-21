import logging
log = logging.getLogger(__name__)

import os
import subprocess
import sys
from pathlib import Path


def baseline_empty_config():
    return {
        # Consider having a "dotenv" for credentials.
        # APKD_BASE_DIR
        "base_dir": None,
        "sdk": {
            # APKD_SDK_DIR
            "sdk_dir": None,
            "commands": {
                "tar": "tar",
                "unxz": "unxz",
                # APKD_JAVA
                "java": "java",
                # APKD_KEYTOOL
                "keytool": "keytool",
                # APKD_ZIPALIGN
                "zipalign": "zipalign",
                # APKD_SDKMANAGER
                "sdkmanager": "sdkmanager",
                # APKD_EMULATOR
                "emulator": "emulator",
                # Note: We don't use adb CLI
            },
            "jars": {
                # APKD_APKSIGNER_JAR
                "apksigner": "${ANDROID_HOME}/build-tools/33.0.3/lib/apksigner.jar",
                # APKD_BAKSMALI_JAR
                "baksmali": "${APKD_BASE_PATH}/downloads/baksmali-3.0.9-fat.jar",
                # APKD_SMALI_JAR
                "smali": "${APKD_BASE_PATH}/downloads/smali-3.0.9-fat.jar",
                # APKD_APKTOOL_JAR
                "apktool": "${APKD_BASE_PATH}/downloads/apktool_3.0.2.jar",
            },
        },
        "adb": {
            "default": {
                "host": "127.0.0.1",
                "port": "5037",
            },
        },
        "downloads": {
            "android-sdk-clitools": {
                "linux": {
                    "repo-xml-url": "https://dl.google.com/android/repository/repository2-3.xml",
                    "base-url": "https://dl.google.com/android/repository/",
                    "cache": "commandlinetools-linux_latest.zip",
                },
            },
            "linux-x64": {
                "java17": {
                    "upstream": "https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz",
                    "cache": "openjdk-17.0.2_linux-x64_bin.tar.gz",
                },
                # "commandlinetools": {
                #     "action": "scrape-google",
                #     "upstream": "https://dl.google.com/android/repository/commandlinetools-linux_latest.zip",
                #     "cache": "commandlinetools-linux_latest.zip",
                # },
                "scrcpy": {
                    "upstream": "https://github.com/Genymobile/scrcpy/releases/download/v4.1/scrcpy-linux-x86_64-v4.1.tar.gz",
                    "cache": "scrcpy-linux-x86_64-v4.1.tar.gz"
                }
            },
            "java": {
                "baksmali": {
                    "upstream": "https://github.com/baksmali/smali/releases/download/3.0.9/baksmali-3.0.9-fat.jar",
                    "cache": "baksmali-3.0.9-fat.jar",
                },
                "smali": {
                    "upstream": "https://github.com/baksmali/smali/releases/download/3.0.9/smali-3.0.9-fat.jar",
                    "cache": "smali-3.0.9-fat.jar",
                },
                "apktool": {
                    "upstream": "https://github.com/iBotPeaches/Apktool/releases/download/v3.0.2/apktool_3.0.2.jar",
                    "cache": "apktool_3.0.2.jar",
                },
            },
            "sdkmanager": [
                "platform-tools",
                "build-tools/33.0.3",
                "emulator",
                "system-images;android-33;default;x86_64",
            ],
            "frida": {  
                "gadget": {
                    "armeabi-v7a": {
                        "upstream": "https://github.com/frida/frida/releases/download/17.15.5/frida-gadget-17.15.5-android-arm.so.xz",
                        "cache": "frida-gadget-17.15.5-android-arm.so.xz",
                        "filename": "frida-gadget-17.15.5-android-arm.so",
                    },
                    "arm64-v8a": {
                        "upstream": "https://github.com/frida/frida/releases/download/17.15.5/frida-gadget-17.15.5-android-arm64.so.xz",
                        "cache": "frida-gadget-17.15.5-android-arm64.so.xz",
                        "filename": "frida-gadget-17.15.5-android-arm64.so",
                    },
                    "x86": {
                        "upstream": "https://github.com/frida/frida/releases/download/17.15.5/frida-gadget-17.15.5-android-x86.so.xz",
                        "cache": "frida-gadget-17.15.5-android-x86.so.xz",
                        "filename": "frida-gadget-17.15.5-android-x86.so",
                    },
                    "x86_64": {
                        "upstream": "https://github.com/frida/frida/releases/download/17.15.5/frida-gadget-17.15.5-android-x86_64.so.xz",
                        "cache": "frida-gadget-17.15.5-android-x86_64.so.xz",
                        "filename": "frida-gadget-17.15.5-android-x86_64.so",
                    },
                },
                "server": {
                    "armeabi-v7a": {
                        "upstream": "https://github.com/frida/frida/releases/download/17.15.5/frida-server-17.15.5-android-arm.xz",
                        "cache": "frida-server-17.15.5-android-arm.xz",
                        "filename": "frida-server-17.15.5-android-arm",
                    },
                    "arm64-v8a": {
                        "upstream": "https://github.com/frida/frida/releases/download/17.15.5/frida-server-17.15.5-android-arm64.xz",
                        "cache": "frida-server-17.15.5-android-arm64.xz",
                        "filename": "frida-server-17.15.5-android-arm64",
                    },
                    "x86": {
                        "upstream": "https://github.com/frida/frida/releases/download/17.15.5/frida-server-17.15.5-android-x86.xz",
                        "cache": "frida-server-17.15.5-android-x86.xz",
                        "filename": "frida-server-17.15.5-android-x86",
                    },
                    "x86_64": {
                        "upstream": "https://github.com/frida/frida/releases/download/17.15.5/frida-server-17.15.5-android-x86_64.xz",
                        "cache": "frida-server-17.15.5-android-x86_64.xz",
                        "filename": "frida-server-17.15.5-android-x86_64",
                    },
                },
            },
        },
        "apk": {
            "sign": {
                # APKD_KEYSTORE
                "default_keystore": "default",
                # APKD_KEYALIAS
                "default_keyalias": "default",
                # Note: We should share keystores across projects.
                "keystores": {
                    "default": {
                        # APKD_KSPASS
                        "kspass": "default",
                        "keys": {
                            "default": {
                                # APKD_KEYPASS
                                "keypass": "default",
                                "dn": "CN=apkd, OU=apkd, O=apkd, L=Unknown, ST=Unknown, C=US",
                            },
                        },
                    },
                },
            },
            "debugify": {
                # default debugify behaviors
            }
        },
        "dbg": {
            "defaults": {
                "force_refresh": False,
                "apk": None,
                "force_download": False,
                "image": "system-images;android-33;default;x86_64",
                "avd": "android13",
                "gui": "scrcpy",
                "jdwp_port": "127.0.0.1:8700",
                "frida_port": "127.0.0.1:27042",
                "repl_sock": "/tmp/repl.sock",
                "exec_sock": "/tmp/exec.sock",
                "dict_sock": "/tmp/dict.sock",
                # Uses config["base_dir"] as config value.
                "proj_dir": None, # if none, defaults to base_dir/projects
                "sdk_dir": None, # if none, defaults to base_dir/sdk

                #"base_dir": None, # always overwritten (uses config["base_dir"])
                #"operation": None, # always overwritten
                #"proj_name": None, # always overwritten
            },
        },
        "projects": {
            "default": {
                "apk": None,
                "keystore": None,
                "keyalias": None,
                "dbg": {
                    # fields here overwrite ["dbg"]["defaults"]
                },
            },
        },
    }


# TODO: Create "apkd keystore" sub-command.
def create_keystore(
    ks_prefix: str,
    keystore_password: str,
    key_password: str,
    keystore_name: str = "default.keystore",
    key_alias: str = "default",
    dname: str = "CN=apkd, OU=apkd, O=apkd, L=Unknown, ST=Unknown, C=US",
) -> Path:
    """
    Create ks_prefix/keystore_name with a signing key named key_alias,
    if ks_prefix does not already exist. Returns the keystore path.
    """
    ks_dir = Path(ks_prefix)
    keystore_path = ks_dir / keystore_name

    if ks_dir.exists():
        print(f"Keystore directory {ks_dir} already exists, skipping.")
        return keystore_path

    print("Making keystore and signing key.")
    ks_dir.mkdir(parents=True)

    cmd = [
        "keytool", "-genkey", "-v",
        "-keystore", str(keystore_path),
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-alias", key_alias,
        "-storepass", keystore_password,
        "-keypass", key_password,
        "-dname", dname,
        "-noprompt",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("Error: 'keytool' not found on PATH. Is a JDK installed?", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"keytool failed (exit {result.returncode})", file=sys.stderr)
        if result.stdout:
            print(f"stdout: {result.stdout.strip()}", file=sys.stderr)
        if result.stderr:
            print(f"stderr: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    print(f"Created {keystore_path}")
    return keystore_path


def load_apkd_config(config:dict={}, config_path=None):
    import yaml
    import thirdparty.apkd.util as apkd_util

    if config_path is None:
        config_path = apkd_util.xdg_config_home() / "apkd" / "config.yaml"

    config_path = config_path.resolve()

    if not config_path.exists():
        print(f"ERROR: {config_path} configuration does not exist.")
        exit(1)

    # Always start with baseline.
    config = apkd_util.deep_merge(baseline_empty_config(), config)

    with open(str(config_path)) as f:
        config = apkd_util.deep_merge(config, yaml.safe_load(f))
    
    # --- Apply environment overrides ---

    config["base_dir"] = os.environ.get("APKD_BASE_DIR", config["base_dir"])
    config["sdk_dir"] = os.environ.get("APKD_SDK_DIR", config["sdk"]["sdk_dir"])

    commands = config["sdk"]["commands"]
    commands["java"] = os.environ.get("APKD_JAVA", commands["java"])
    commands["keytool"] = os.environ.get("APKD_KEYTOOL", commands["keytool"])
    commands["zipalign"] = os.environ.get("APKD_ZIPALIGN", commands["zipalign"])
    #commands["apksigner"] = os.environ.get("APKD_APKSIGNER", commands["apksigner"])
    commands["sdkmanager"] = os.environ.get("APKD_SDKMANAGER", commands["sdkmanager"])
    commands["emulator"] = os.environ.get("APKD_EMULATOR", commands["emulator"])

    jars = config["sdk"]["jars"]
    jars["apksigner"] = os.environ.get("APKD_APKSIGNER_JAR", jars["apksigner"])
    jars["baksmali"] = os.environ.get("APKD_BAKSMALI_JAR", jars["baksmali"])
    jars["smali"] = os.environ.get("APKD_SMALI_JAR", jars["smali"])
    jars["apktool"] = os.environ.get("APKD_APKTOOL_JAR", jars["apktool"])

    apk_sign = config["apk"]["sign"]
    apk_sign["default_keystore"] = os.environ.get("APKD_KEYSTORE", apk_sign["default_keystore"])
    apk_sign["default_keyalias"] = os.environ.get("APKD_KEYALIAS", apk_sign["default_keyalias"])

    keystore = config["apk"]["sign"]["keystores"][config["apk"]["sign"]["default_keystore"]]
    keystore["kspass"] = os.environ.get("APKD_KSPASS", keystore["kspass"])
    key = keystore["keys"][config["apk"]["sign"]["default_keyalias"]]
    key["keypass"] = os.environ.get("APKD_KEYPASS", key["keypass"])

    return config


def save_apkd_config(config:dict={}, config_path=None, force:bool=False):
    import yaml
    import thirdparty.apkd.util as apkd_util

    if config_path is None:
        config_path = apkd_util.xdg_config_home() / "apkd" / "config.yaml"
    config_path = config_path.resolve()

    if config_path.exists() and not force:
        print(f"ERROR: {config_path} config.yaml file exists. Remove or force to save.")
        exit(1)

    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(str(config_path), "w") as f:
        yaml.dump(apkd_util.deep_merge(baseline_empty_config(), config), f, sort_keys=False)


def implicit_base_dir():
    # Worst case, use local folder.
    base_dir = Path('.') / "apkd"
    
    # Best implicit case, use venv as base prefix.
    if sys.prefix != sys.base_prefix:
        # We're in a venv, use it.
        base_dir = Path(sys.prefix) / "apkd"

    return base_dir.resolve()


def implicit_sdk_dir():
    return implicit_base_dir() / "sdk"


def resolve_base_dir(config=None):
    # Assumes config already loaded.
    if "base_dir" in config and config["base_dir"] is not None:
        return resolve_base_dir(config["base_dir"])

    return implicit_base_dir()


def resolve_sdk_dir(config=None):
    if "sdk" in config and isinstance(config["sdk"], dict):
        if "sdk_dir" in config["sdk"] and config["sdk"]["sdk_dir"] is not None:
            return Path(config["sdk"]["sdk_dir"]).resolve()

    return implicit_sdk_dir()



def implicit_proj_dir(proj_name):
    return implicit_base_dir() / "projects" / proj_name




    # ks_name = config["default_keystore"]
    # ks_prefix = config_dir / "keystores"
    # ks_config = config["keystores"][ks_name]
    # key_alias = config["default_keyalias"]
    # key_config = ks_config["keys"][key_alias]
    # ks_pass = ks_config["kspass"]
    # key_pass = key_config["keypass"]
    # dname = key_config["dn"]

    # create_keystore(str(ks_prefix), ks_pass, key_pass, keystore_name=ks_name, key_alias=key_alias, dname=dname)





"""
def baseline_empty_config_old():
    return {
        # TODO: Consider keeping these in ["sdk"] (along with all required tools).
        # TODO: Consider replacing with values that get added to base_dir and generated at runtime.
        "envs": {
            "default": {
                "BASE_PATH": "cache/envs/default/",
                "ANDROID_HOME": "${BASE_PATH}android/",
                "JAVA_HOME": "${BASE_PATH}java17/",
                "PATH": [
                    "${JAVA_HOME}bin",
                    "${ANDROID_HOME}cmdline-tools/latest/bin",
                    "${ANDROID_HOME}platform-tools",
                    "${ANDROID_HOME}emulator",
                    "${ANDROID_HOME}scrcpy",
                    "${ANDROID_HOME}jadx/bin",
                    "${ANDROID_HOME}misc-tools",
                ],
            },
        },
        "adb": {
            "default": {
                "host": "127.0.0.1",
                "port": "5037",
                "device": "emulator-5554",
            },
        },
        "binaries": {
            "java": "java",
            "keytool": "keytool",
            "zipalign": "zipalign",
            "apksigner": "apksigner",
        },
        "jars": {
            "apksigner": "apksigner.jar",
            "baksmali": "baksmali.jar",
            "smali": "smali.jar",
            "apktool": "apktool.jar",
        },
        "frida": {
            "gadget": {
                "armeabi-v7a": "frida-gadget-17.15.5-android-arm.so",
                "arm64-v8a": "frida-gadget-17.15.5-android-arm64.so",
                "x86": "frida-gadget-17.15.5-android-x86.so",
                "x86_64": "frida-gadget-17.15.5-android-x86_64.so",
            },
            "server": {
                "armeabi-v7a": "frida-server-17.15.5-android-arm",
                "arm64-v8a": "frida-server-17.15.5-android-arm64",
                "x86": "frida-server-17.15.5-android-x86",
                "x86_64": "frida-server-17.15.5-android-x86_64",
            },
        },
        # TODO: Good, but consider tags for each upstream/cache pair.
        "downloads": {
            "java": {
                "linux-x64": {
                    "upstream": "https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz",
                    "cache": "openjdk-17.0.2_linux-x64_bin.tar.gz",
                },
            },
            "commandlinetools": {
                "linux-x64": {
                    "upstream": "unset",
                    "cache": "commandlinetools-linux-14742923_latest.zip",
                },
            },
            "scrcpy": {
                "linux-x64": {
                    "upstream": "https://github.com/Genymobile/scrcpy/releases/download/v4.1/scrcpy-linux-x86_64-v4.1.tar.gz",
                    "cache": "scrcpy-linux-x86_64-v4.1.tar.gz"
                }
            }
        },
        # TODO: Consider putting these under ["apk"]["sign"]
        "default_keystore": "default",
        "default_keyalias": "default",
        "keystores": {
            "default": {
                "kspass": "default",
                "keys": {
                    "default": {
                        "keypass": "default",
                        "dn": "CN=apkd, OU=apkd, O=apkd, L=Unknown, ST=Unknown, C=US",
                    },
                },
            },
        },
        "dbg": {
            "projects": {
                "default": {
                }
            },
            "defaults": {
                "force_refresh": False,
                "apk": None,
                "force_download": False,
                "image": None,
                "avd": None,
                "gui": "scrcpy",
                "jdwp_port": None,
                "frida_port": None,
                "repl_sock": None,
                "exec_sock": None,
                "dict_sock": None,
                "base_dir": None,
                "proj_dir": None,
                "sdk_dir": None,
                "proj_dir": None,
                "operation": None,
                "proj_name": None,
            }
        }
    }


def init_apkd_config_dir_old(config_dir=None):
    import os
    import yaml
    from pathlib import Path

    if config_dir is None:
        config_dir = Path(os.environ["HOME"]) / ".config" / "apkd"

    if config_dir.exists():
        print(f"Error: {config_dir} configuration folder exists. Remove and retry to initialize.", file=sys.stderr)
        sys.exit(1)

    config_dir.mkdir(parents=True)

    config = baseline_empty_config()

    with open(str(config_dir / "config.yaml"), "w") as f:
        yaml.dump(config, f)
    
    from thirdparty.apkd.config.init import create_keystore
    
    ks_name = config["default_keystore"]
    ks_prefix = config_dir / "keystores"
    ks_config = config["keystores"][ks_name]
    key_alias = config["default_keyalias"]
    key_config = ks_config["keys"][key_alias]
    ks_pass = ks_config["kspass"]
    key_pass = key_config["keypass"]
    dname = key_config["dn"]

    create_keystore(str(ks_prefix), ks_pass, key_pass, keystore_name=ks_name, key_alias=key_alias, dname=dname)
"""



