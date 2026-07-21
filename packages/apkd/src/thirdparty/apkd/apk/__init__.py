import logging
log = logging.getLogger(__name__)

import os
import shutil
from pathlib import Path
import thirdparty.apkd.util as apkd_util

__all__ = []


from .dex import (
    dex_disassemble_and_remove,
    dex_reassemble_all,
)

__all__ += [
    'dex_disassemble_and_remove',
    'dex_reassemble_all',
]

from .extract import (
    do_extraction_process, # ! deprecated
    extract_apk,
    create_folder_structure,
)

__all__ += [
    'do_extraction_process',
    'create_folder_structure',
]

from .ls import (
    list_zip_like_ls,
)

__all__ += [
    'list_zip_like_ls',
]

from .manifest import (
    get_manifest,
    androguard_decode_manifest,
    encode_manifest,
)

__all__ += [
    'get_manifest',
    'androguard_decode_manifest',
    'encode_manifest',
]

from .pack import (
    pack_apk,
    do_pack_process, # ! deprecated
)

__all__ += [
    'do_pack_process',
]

from .patch import (
    apkd_apk_patch_debuggable_manifest, # ! deprecated
    patch_in_frida_gadget, # ! deprecated
    patch_frida_gadget,
    set_debuggable,
)

__all__ += [
    'apkd_apk_patch_debuggable_manifest',
    'patch_in_frida_gadget',
]

from .resources import (
    get_resources,
)

__all__ += [
    'get_resources',
]

from .sign import (
    sign_apk,
)

__all__ += [
    'sign_apk',
]