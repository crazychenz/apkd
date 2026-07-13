import zipfile
import stat
from datetime import datetime


def permissions_string(external_attr):
    mode = external_attr >> 16
    if mode == 0:
        return "(none stored)"
    return stat.filemode(mode)


def list_zip_like_ls(path):
    with zipfile.ZipFile(path, "r") as z:
        for info in z.infolist():
            perms = permissions_string(info.external_attr)
            dt = datetime(*info.date_time)
            size = info.file_size
            print(f"{perms:12} {size:>10}  {dt:%Y-%m-%d %H:%M}  {info.filename}")
