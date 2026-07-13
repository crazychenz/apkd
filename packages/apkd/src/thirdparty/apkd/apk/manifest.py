import logging
log = logging.getLogger(__name__)


def get_manifest(apk_path):
    """Dump manifest without extraction"""
    from androguard.core.apk import APK
    import lxml.etree as etree

    manifest = APK(apk_path).get_android_manifest_xml()

    # Return XML as string.
    return etree.tostring(manifest, pretty_print=True).decode()


def androguard_decode_manifest(input_path, output_path):
    """Decode manifest from extraction"""
    from androguard.core.axml import AXMLPrinter

    with open(input_path, "rb") as f:
        printer = AXMLPrinter(f.read())

    decoded_bytes = printer.get_xml(pretty=True)

    with open(output_path, "wb") as f:
        f.write(decoded_bytes)


def encode_manifest(input_xml_path, output_axml_path):
    """Encode extracted manifest"""
    import pyaxml
    from pathlib import Path
    from xml.etree import ElementTree as ET

    # Parse the plain-text XML into an ElementTree
    tree = ET.parse(Path(input_xml_path))
    xml_root = tree.getroot()

    # Encode it into AXML
    axml_object = pyaxml.AXML()
    axml_object.from_xml(xml_root)

    output_axml_path = Path(output_axml_path)
    output_axml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_axml_path, "wb") as f:
        f.write(axml_object.pack())

















# def pyaxml_decode_manifest(input_path, output_path):
#     import pyaxml
#     from pathlib import Path

#     input_path = Path(input_path)
#     output_path = Path(output_path)

#     with open(input_path, "rb") as f:
#         axml = pyaxml.AXML.from_axml(f.read())

#     xml_tree = fix_namespaces(axml.to_xml())  # returns an lxml/ElementTree Element

#     output_path.parent.mkdir(parents=True, exist_ok=True)

#     # ElementTree write needs the tree, not just the root element
#     #from xml.etree import ElementTree as ET
#     #ET.ElementTree(xml_tree).write(output_path, encoding="utf-8", xml_declaration=True)

#     import lxml.etree as etree
#     with open(output_path, "wb") as f:
#         f.write(etree.tostring(xml_tree, xml_declaration=True, encoding="utf-8"))


# KNOWN_PREFIXES = {
#     "http://schemas.android.com/apk/res/android": "android",
#     "http://schemas.android.com/apk/res-auto": "app",
#     "http://schemas.android.com/tools": "tools",
# }


# def _split_clark(tag: str):
#     if tag.startswith("{"):
#         uri, local = tag[1:].split("}", 1)
#         return uri, local
#     return None, tag


# def _collect_namespace_uris(elem, uris=None) -> set:
#     if uris is None:
#         uris = set()
#     uri, _ = _split_clark(elem.tag)
#     if uri:
#         uris.add(uri)
#     for key in elem.attrib:
#         uri, _ = _split_clark(key)
#         if uri:
#             uris.add(uri)
#     for child in elem:
#         _collect_namespace_uris(child, uris)
#     return uris


# def _clone_element(elem):
#     import lxml.etree as etree
#     new_elem = etree.Element(elem.tag)
#     for key, value in elem.attrib.items():
#         new_elem.set(key, value)
#     new_elem.text = elem.text
#     new_elem.tail = elem.tail
#     for child in elem:
#         new_elem.append(_clone_element(child))
#     return new_elem


# def fix_namespaces(to_xml_result):
#     """
#     Take whatever pyaxml's to_xml() returned (str, bytes, Element, or
#     ElementTree) and return the same XML with canonical namespace
#     prefixes (android/app/tools) instead of auto-generated ns0/ns1/etc.

#     Returns bytes (matching the most common to_xml() return type).
#     """
#     import lxml.etree as etree
#     # Normalize input into a root Element regardless of what came in
#     if isinstance(to_xml_result, bytes):
#         root = etree.fromstring(to_xml_result)
#     elif isinstance(to_xml_result, str):
#         root = etree.fromstring(to_xml_result.encode("utf-8"))
#     elif isinstance(to_xml_result, etree._ElementTree):
#         root = to_xml_result.getroot()
#     elif isinstance(to_xml_result, etree._Element):
#         root = to_xml_result
#     else:
#         raise TypeError(f"Unexpected to_xml() return type: {type(to_xml_result)}")

#     uris = _collect_namespace_uris(root)

#     next_auto = 0
#     prefix_map = {}
#     for uri in sorted(uris):
#         if uri in KNOWN_PREFIXES:
#             prefix_map[uri] = KNOWN_PREFIXES[uri]
#         else:
#             prefix_map[uri] = f"ns{next_auto}"
#             next_auto += 1

#     nsmap = {prefix: uri for uri, prefix in prefix_map.items()}

#     new_root = etree.Element(root.tag, nsmap=nsmap)
#     for key, value in root.attrib.items():
#         new_root.set(key, value)
#     new_root.text = root.text
#     for child in root:
#         new_root.append(_clone_element(child))

#     return new_root
#     #return etree.tostring(new_root, xml_declaration=True, encoding="utf-8")