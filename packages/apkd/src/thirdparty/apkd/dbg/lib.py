import logging
log = logging.getLogger(__name__)

import os
import sys
from pathlib import Path

def resolve_base_dir(args):
    # Worst case, use local folder.
    base_dir = Path('.') / "apkd"
    
    # Best implicit case, use venv as base prefix.
    if sys.prefix != sys.base_prefix:
        # We're in a venv, use it.
        base_dir = Path(sys.prefix) / "apkd"

    # Allow environment override.
    base_dir = Path(os.environ.get("APKD_BASE_DIR", base_dir))

    # CLI override always wins.
    if args.base_dir:
        base_dir = Path(args.base_dir)
    return base_dir.resolve()