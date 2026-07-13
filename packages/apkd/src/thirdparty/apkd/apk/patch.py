




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