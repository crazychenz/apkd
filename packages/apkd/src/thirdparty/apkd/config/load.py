import logging
log = logging.getLogger(__name__)


def load_apkd_config():
    import os
    import yaml
    from pathlib import Path

    config_dir = Path(os.environ["HOME"]) / ".config" / "apkd"

    with open(str(config_dir / "config.yaml")) as f:
        return yaml.safe_load(f)