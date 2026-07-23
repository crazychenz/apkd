import logging
log = logging.getLogger(__name__)

import shutil
from pathlib import Path

def set_debuggable(manifest_path: str) -> None:
    """
    Idempotently set android:debuggable="true" on the <application> element
    of a decoded AndroidManifest.xml.
    """

    import lxml.etree as etree
    tree = etree.parse(manifest_path)
    root = tree.getroot()

    application = root.find("application")
    if application is None:
        raise ValueError(f"No <application> element found in {manifest_path}")

    ANDROID_NS = "http://schemas.android.com/apk/res/android"
    debuggable_attr = f"{{{ANDROID_NS}}}debuggable"
    application.set(debuggable_attr, "true")

    tree.write(
        manifest_path,
        xml_declaration=True,
        encoding="utf-8",
        pretty_print=True,
    )


def set_extract_native_libs(manifest_path: str) -> None:
    """
    Idempotently set android:extractNativeLibs="true" on the <application> element
    of a decoded AndroidManifest.xml.

    - If the attribute is missing, it is added with value "true".
    - If the attribute exists and is "false" (or anything other than "true"), it is set to "true".
    - If the attribute already exists and is "true", the file is left untouched (no write).
    """

    import lxml.etree as etree
    tree = etree.parse(manifest_path)
    root = tree.getroot()

    application = root.find("application")
    if application is None:
        raise ValueError(f"No <application> element found in {manifest_path}")

    ANDROID_NS = "http://schemas.android.com/apk/res/android"
    extract_native_libs_attr = f"{{{ANDROID_NS}}}extractNativeLibs"

    current_value = application.get(extract_native_libs_attr)
    if current_value == "true":
        return  # already set correctly, no-op

    application.set(extract_native_libs_attr, "true")

    tree.write(
        manifest_path,
        xml_declaration=True,
        encoding="utf-8",
        pretty_print=True,
    )


def apkd_apk_patch_debuggable_manifest(config, proj_name):
    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    sdk_dir = resolve_sdk_dir(config)

    proj_dir = Path(base_dir / "projects" / proj_name)
    #from thirdparty.apkd.apk.patch import set_debuggable, set_extract_native_libs
    manifest_path = proj_dir / "working" / "apk" / "AndroidManifest.xml"

    set_debuggable(str(manifest_path))
    set_extract_native_libs(str(manifest_path))


def find_main_activity(manifest_path: str) -> str | None:
    """
    Parse AndroidManifest.xml and return the fully-qualified class name of the
    activity (or activity-alias target) that declares:
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>

    Returns None if no such activity is found.
    """

    import xml.etree.ElementTree as ET
    ANDROID_NS = "http://schemas.android.com/apk/res/android"
    NS = {"android": ANDROID_NS}

    tree = ET.parse(manifest_path)
    root = tree.getroot()

    package = root.get("package", "")
    application = root.find("application")
    if application is None:
        return None

    def _name_attr(elem):
        return elem.get(f"{{{ANDROID_NS}}}name")

    def has_launcher_intent_filter(component) -> bool:
        for intent_filter in component.findall("intent-filter"):
            actions = {_name_attr(a) for a in intent_filter.findall("action")}
            categories = {_name_attr(c) for c in intent_filter.findall("category")}
            if "android.intent.action.MAIN" in actions \
                and "android.intent.category.LAUNCHER" in categories:
                return True
        return False

    def _resolve_name(name: str, package: str) -> str:
        """Resolve a possibly-relative component name (e.g. '.MainActivity')
        against the manifest's package attribute."""
        if not name:
            return name
        if name.startswith("."):
            return package + name
        if "." not in name:
            # Bare class name with no package qualifier at all
            return f"{package}.{name}"
        return name

    # Check plain <activity> elements first
    for activity in application.findall("activity"):
        if has_launcher_intent_filter(activity):
            name = _name_attr(activity)
            return _resolve_name(name, package)

    # Some apps expose the launcher via <activity-alias android:targetActivity="...">
    for alias in application.findall("activity-alias"):
        if has_launcher_intent_filter(alias):
            target = alias.get(f"{{{ANDROID_NS}}}targetActivity")
            return _resolve_name(target, package)

    return None


def find_smali_file(class_name: str, dex_base: str = "dex") -> str:
    """
    Locate the smali file for a fully-qualified class name (dot notation,
    e.g. "com.example.app.MainActivity") within a baksmali extraction.

    Returns the first matching path found or None if no match found.
    """

    import os

    # Convert dots to slashes to match folder structure.
    relative_path = class_name.replace(".", "/") + ".smali"

    if not os.path.isdir(dex_base):
        print(f"Invalid dex_base: {dex_base}")

    candidates = []
    for entry in sorted(os.listdir(dex_base)):
        dex_subdir = os.path.join(dex_base, entry)
        if not os.path.isdir(dex_subdir):
            continue
        candidate = os.path.join(dex_subdir, relative_path)
        candidates.append(candidate)
        if os.path.isfile(candidate):
            return candidate

    return None


def patch_smali_with_gadget(
    smali_path: str,
    lib_name: str = "frida-gadget",
    out_path: str | None = None,
) -> bool:
    """
    Patch a smali file so the class loads `lib<lib_name>.so` via
    System.loadLibrary() as the first instruction of its <clinit>.

    If the class has no <clinit>, one is created and marked static
    in the method's access flags implicitly (constructor <clinit> is
    always static by spec, no separate 'static' flag needed).

    lib_name should be WITHOUT the 'lib' prefix / '.so' suffix, matching
    what you'd pass to System.loadLibrary(), e.g. "frida-gadget" to load
    lib/<abi>/libfrida-gadget.so.

    Idempotent: if this smali file has already been patched for the given
    lib_name, this is a no-op and returns False. Returns True if a patch
    was actually applied.
    """

    import re

    out_path = out_path or smali_path

    with open(smali_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # --- Idempotency guard -------------------------------------------------
    # Marker comment lets us detect our own prior patch even if someone
    # hand-edits whitespace around it. We also fall back to matching the
    # actual loadLibrary call + string literal, in case the marker line
    # itself was stripped by some other tool.
    marker = f"# frida-gadget-patch: {lib_name}\n"
    loadlibrary_re = re.compile(
        r'invoke-static\s*\{v\d+\},\s*Ljava/lang/System;->loadLibrary\(Ljava/lang/String;\)V'
    )
    conststring_re = re.compile(
        r'const-string\s+v\d+,\s*"' + re.escape(lib_name) + r'"'
    )

    already_patched = False
    for i, line in enumerate(lines):
        if line == marker:
            already_patched = True
            break
        if loadlibrary_re.search(line):
            # A loadLibrary call exists — confirm it's loading THIS lib_name
            # by checking the preceding const-string line(s) nearby.
            window = lines[max(0, i - 3):i]
            if any(conststring_re.search(w) for w in window):
                already_patched = True
                break

    if already_patched:
        # Nothing to do. If out_path differs from smali_path, still mirror
        # the file so callers relying on out_path existing don't break.
        if out_path != smali_path:
            with open(out_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
        return False
    # ------------------------------------------------------------------------

    injected_body = [
        marker,
        f'    const-string v0, "{lib_name}"\n',
        "\n",
        "    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n",
        "\n",
    ]

    clinit_start_re = re.compile(
        r"^\.method\s+.*constructor\s+<clinit>\(\)V\s*$"
    )
    locals_re = re.compile(r"^(\s*)\.locals\s+(\d+)\s*$")
    registers_re = re.compile(r"^(\s*)\.registers\s+(\d+)\s*$")

    clinit_idx = None
    for i, line in enumerate(lines):
        if clinit_start_re.match(line.rstrip("\n")):
            clinit_idx = i
            break

    if clinit_idx is not None:
        # --- Existing <clinit>: bump/verify register count, then inject ---
        j = clinit_idx + 1
        reg_line_idx = None
        is_locals = True
        min_needed = 1  # we only ever touch v0

        while j < len(lines):
            m_locals = locals_re.match(lines[j])
            m_regs = registers_re.match(lines[j])
            if m_locals:
                reg_line_idx = j
                is_locals = True
                current = int(m_locals.group(2))
                break
            if m_regs:
                reg_line_idx = j
                is_locals = False
                current = int(m_regs.group(2))
                break
            if lines[j].strip().startswith(".end method"):
                break
            j += 1

        if reg_line_idx is None:
            print(f"Found <clinit> in {smali_path} but no .locals/.registers directive")
            exit(1)

        if is_locals:
            if current < min_needed:
                indent = locals_re.match(lines[reg_line_idx]).group(1)
                lines[reg_line_idx] = f"{indent}.locals {min_needed}\n"
        else:
            if current < min_needed:
                indent = registers_re.match(lines[reg_line_idx]).group(1)
                lines[reg_line_idx] = f"{indent}.registers {min_needed}\n"

        insert_at = reg_line_idx + 1
        lines[insert_at:insert_at] = injected_body

    else:
        # --- No <clinit>: synthesize one and insert it into the class body ---
        new_method = (
            [".method static constructor <clinit>()V\n", "    .locals 1\n", "\n"]
            + injected_body
            + ["    return-void\n", ".end method\n", "\n"]
        )

        insert_idx = None

        for i, line in enumerate(lines):
            if line.strip() == "# direct methods":
                insert_idx = i + 1
                break

        if insert_idx is None:
            for i, line in enumerate(lines):
                if line.lstrip().startswith(".method"):
                    insert_idx = i
                    break

        if insert_idx is None:
            last_field_end = None
            for i, line in enumerate(lines):
                if line.strip() == ".end field":
                    last_field_end = i
            insert_idx = (last_field_end + 1) if last_field_end is not None else len(lines)

        lines[insert_idx:insert_idx] = new_method

    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return True


def patch_in_frida_gadget(config, proj_name, inject_gadget = False, patch_smali = False):

    from thirdparty.apkd.config import resolve_sdk_dir, resolve_base_dir
    base_dir = resolve_base_dir(config)
    #sdk_dir = resolve_sdk_dir(config)

    proj_dir = Path(base_dir / "projects" / proj_name).resolve()

    patch_frida_gadget(proj_dir, base_dir, config, inject_gadget, patch_smali)


def patch_frida_gadget(proj_dir, base_dir, config, inject_gadget = False, patch_smali = False):

    if patch_smali:

        working_manifest_path = proj_dir / "working" / "apk" / "AndroidManifest.xml"
        from thirdparty.apkd.apk.patch import find_main_activity
        main_activity = find_main_activity(working_manifest_path)

        if not main_activity:
            print("No main activity found.")
            exit(1)
        
        print(f"Found main activity at: {main_activity}")

        from thirdparty.apkd.apk.patch import find_smali_file
        smali_path = find_smali_file(main_activity, str(proj_dir / "working" / "dex"))

        if not smali_path:
            print(f"Could not find smali for {main_activity}")
            exit(1)

        print(f"Found smali at: {smali_path}")

        from thirdparty.apkd.apk.patch import patch_smali_with_gadget
        patch_smali_with_gadget(smali_path)
        print(f"Patched {smali_path}")

    if inject_gadget:

        # Copy gadgets to native folder
        working_lib_path = proj_dir / "working" / "apk" / "lib"
        working_lib_path.mkdir(parents=True, exist_ok=True)
        #for subdir in [d for d in working_lib_path.iterdir() if d.is_dir()]:
        for subdir in config["downloads"]["frida"]["gadget"]:
            gadget_src_path = base_dir / "downloads" / config["downloads"]["frida"]["gadget"][subdir]["filename"]
            if not gadget_src_path.exists():
                print(f"Gadget {gadget_src_path.name} not found, skipping for arch: {subdir}")
                continue
            gadget_dst_path = working_lib_path / subdir / "libfrida-gadget.so"
            gadget_dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(gadget_src_path), str(gadget_dst_path))












# def patch_smali_with_gadget(
#     smali_path: str,
#     lib_name: str = "frida-gadget",
#     out_path: str | None = None,
# ) -> None:
#     """
#     Patch a smali file so the class loads `lib<lib_name>.so` via
#     System.loadLibrary() as the first instruction of its <clinit>.

#     If the class has no <clinit>, one is created and marked static
#     in the method's access flags implicitly (constructor <clinit> is
#     always static by spec, no separate 'static' flag needed).

#     lib_name should be WITHOUT the 'lib' prefix / '.so' suffix, matching
#     what you'd pass to System.loadLibrary(), e.g. "frida-gadget" to load
#     lib/<abi>/libfrida-gadget.so.
#     """

#     import re

#     out_path = out_path or smali_path

#     with open(smali_path, "r", encoding="utf-8") as f:
#         lines = f.readlines()

#     injected_body = [
#         f'    const-string v0, "{lib_name}"\n',
#         "\n",
#         "    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n",
#         "\n",
#     ]

#     clinit_start_re = re.compile(
#         r"^\.method\s+.*constructor\s+<clinit>\(\)V\s*$"
#     )
#     locals_re = re.compile(r"^(\s*)\.locals\s+(\d+)\s*$")
#     registers_re = re.compile(r"^(\s*)\.registers\s+(\d+)\s*$")

#     clinit_idx = None
#     for i, line in enumerate(lines):
#         if clinit_start_re.match(line.strip("\n") if False else line):
#             pass
#         if clinit_start_re.match(line.rstrip("\n")):
#             clinit_idx = i
#             break

#     if clinit_idx is not None:
#         # --- Existing <clinit>: bump/verify register count, then inject ---
#         j = clinit_idx + 1
#         reg_line_idx = None
#         is_locals = True
#         min_needed = 1  # we only ever touch v0

#         while j < len(lines):
#             m_locals = locals_re.match(lines[j])
#             m_regs = registers_re.match(lines[j])
#             if m_locals:
#                 reg_line_idx = j
#                 is_locals = True
#                 current = int(m_locals.group(2))
#                 break
#             if m_regs:
#                 reg_line_idx = j
#                 is_locals = False
#                 current = int(m_regs.group(2))
#                 break
#             if lines[j].strip().startswith(".end method"):
#                 break
#             j += 1

#         if reg_line_idx is None:
#             print(f"Found <clinit> in {smali_path} but no .locals/.registers directive")
#             exit(1)

#         if is_locals:
#             # .locals counts only local (non-parameter) registers; clinit has
#             # no parameters, so .locals == .registers here. Bump if needed.
#             if current < min_needed:
#                 indent = locals_re.match(lines[reg_line_idx]).group(1)
#                 lines[reg_line_idx] = f"{indent}.locals {min_needed}\n"
#         else:
#             if current < min_needed:
#                 indent = registers_re.match(lines[reg_line_idx]).group(1)
#                 lines[reg_line_idx] = f"{indent}.registers {min_needed}\n"

#         # Insert immediately after the .locals/.registers directive.
#         insert_at = reg_line_idx + 1
#         lines[insert_at:insert_at] = injected_body

#     else:
#         # --- No <clinit>: synthesize one and insert it into the class body ---
#         new_method = (
#             [".method static constructor <clinit>()V\n","    .locals 1\n", "\n"]
#             + injected_body
#             + ["    return-void\n", ".end method\n", "\n"]
#         )

#         # Prefer inserting right after the "# direct methods" marker baksmali
#         # emits, or otherwise right before the first .method, or otherwise
#         # right after the last .field, or otherwise at end of file.
#         insert_idx = None

#         for i, line in enumerate(lines):
#             if line.strip() == "# direct methods":
#                 insert_idx = i + 1
#                 break

#         if insert_idx is None:
#             for i, line in enumerate(lines):
#                 if line.lstrip().startswith(".method"):
#                     insert_idx = i
#                     break

#         if insert_idx is None:
#             last_field_end = None
#             for i, line in enumerate(lines):
#                 if line.strip() == ".end field":
#                     last_field_end = i
#             insert_idx = (last_field_end + 1) if last_field_end is not None else len(lines)

#         lines[insert_idx:insert_idx] = new_method

#     with open(out_path, "w", encoding="utf-8") as f:
#         f.writelines(lines)