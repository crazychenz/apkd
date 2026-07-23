import logging
log = logging.getLogger(__name__)

import os
import subprocess
from pathlib import Path


def sign_apk(config, src_apk, dst_apk):
    
    # TODO: Put in config.py
    def get_kspass(keystores, ks_name):
        try:
            return keystores[ks_name]["kspass"]
        except KeyError:
            return None
    
    # TODO: Put in config.py
    def get_keypass(keystores, ks_name, key_alias):
        try:
            return keystores[ks_name]["keys"][key_alias]["keypass"]
        except KeyError:
            return None

    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)

    ks_name = config["apk"]["sign"]["default_keystore"]
    ks_prefix = base_dir / "keystores"
    key_alias = config["apk"]["sign"]["default_keyalias"]
    keystores = config["apk"]["sign"]["keystores"]
    ks_pass = os.environ.get("APKD_KSPASS", get_kspass(keystores, ks_name))
    key_pass = os.environ.get("APKD_KEYPASS", get_keypass(keystores, ks_name, key_alias))
    dname = keystores[ks_name]["keys"][key_alias]["dn"]

    # Ensure the keystore is created.
    from thirdparty.apkd.config import create_keystore
    create_keystore(str(ks_prefix), ks_pass, key_pass, keystore_name=ks_name, key_alias=key_alias, dname=dname)

    apksigner_path = os.path.expandvars(config["sdk"]["jars"]["apksigner"])
    java_path = os.path.expandvars(config["sdk"]["commands"]["java"])

    cmd = [
        java_path, '-jar', apksigner_path, 'sign',
        '--ks', str(ks_prefix / ks_name),
        '--ks-key-alias', key_alias,
        '--ks-pass', f'pass:{ks_pass}',
        '--key-pass', f'pass:{key_pass}',
        '--out', str(dst_apk),
        str(src_apk),
    ]
    print(' '.join(cmd))
    subprocess.run(cmd, check=True)