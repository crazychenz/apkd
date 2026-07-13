import logging
log = logging.getLogger(__name__)


def sign_apk(config, src_apk, dst_apk):
    from pathlib import Path
    import os
    import subprocess

    config_dir = Path(os.environ["HOME"]) / ".config" / "apkd"

    apksigner_path = config["jars"]["apksigner"]
    java_path = config["binaries"]["java"]

    ks_name = config["default_keystore"]
    ks_prefix = config_dir / "keystores"
    ks_config = config["keystores"][ks_name]
    key_alias = config["default_keyalias"]
    key_config = ks_config["keys"][key_alias]
    ks_pass = ks_config["kspass"]
    key_pass = key_config["keypass"]
    dname = key_config["dn"]

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