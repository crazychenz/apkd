import logging
log = logging.getLogger(__name__)


def create_folder_structure(apkalias_path):
    from pathlib import Path

    folders = {
        ".original": ["pkg", "apk"],
        "working": ["apk", "dex", "pkg", "elf"],
        ".build": ["pkg", "dex", "apk", "elf"],
    }

    for tlf in folders:
        for folder in folders[tlf]:
            fpath = apkalias_path / tlf / folder
            fpath.mkdir(parents=True, exist_ok=True)