import logging
log = logging.getLogger(__name__)


#!/usr/bin/env python3
"""
Create a keystore + signing key for apkd, fully unattended.

Reads passwords from environment variables (no hardcoded secrets):
    APKD_KEYSTORE_PASSWORD
    APKD_KEY_PASSWORD
"""

import os
import subprocess
import sys
from pathlib import Path


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


# if __name__ == "__main__":
#     keystore_password = os.environ.get("APKD_KEYSTORE_PASSWORD")
#     key_password = os.environ.get("APKD_KEY_PASSWORD")

#     if not keystore_password or not key_password:
#         print(
#             "Error: set APKD_KEYSTORE_PASSWORD and APKD_KEY_PASSWORD",
#             file=sys.stderr,
#         )
#         sys.exit(1)

#     create_keystore(
#         ks_prefix="./keystore",
#         keystore_password=keystore_password,
#         key_password=key_password,
#     )