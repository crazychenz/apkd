

def get_manifest(apk_path, xpath=None):
    from androguard.core.apk import APK
    import lxml.etree as etree

    manifest = APK(apk_path).get_android_manifest_xml()

    # TODO: Implement xpath of manifest for specific queries.
    # if xpath:
    #     return xpath_query(manifest, xpath)

    # Return XML as string.
    return etree.tostring(manifest, pretty_print=True).decode()


def decode_manifest(input_path, output_path):
    import pyaxml
    from pathlib import Path

    input_path = Path(input_path)
    output_path = Path(output_path)

    with open(input_path, "rb") as f:
        axml = pyaxml.AXML.from_axml(f.read())

    xml_tree = axml.to_xml()  # returns an lxml/ElementTree Element

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ElementTree write needs the tree, not just the root element
    from xml.etree import ElementTree as ET
    ET.ElementTree(xml_tree).write(output_path, encoding="utf-8", xml_declaration=True)


def encode_manifest(input_xml_path, output_axml_path):
    import pyaxml
    from pathlib import Path
    from xml.etree import ElementTree as ET

    input_xml_path = Path(input_xml_path)
    output_axml_path = Path(output_axml_path)

    # Parse the plain-text XML into an ElementTree
    tree = ET.parse(input_xml_path)
    xml_root = tree.getroot()

    # Encode it into AXML
    axml_object = pyaxml.AXML()
    axml_object.from_xml(xml_root)

    output_axml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_axml_path, "wb") as f:
        f.write(axml_object.pack())