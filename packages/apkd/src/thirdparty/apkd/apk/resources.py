

def get_resources(apk_path, rsc_id=None):
    from androguard.core.apk import APK

    # TODO: Convert resource string to number.
    # if rsc_id:
    #     rsc_id_num = convert(rsc_id)
    #     return arsc.get_resource_xml_name(rsc_id_num)

    arsc = APK(apk_path).get_android_resources()
    return arsc.get_string_resources(arsc.get_packages_names()[0])



"""
Dump a parsed ARSC to a human-editable text file (protobuf text format),
allow manual edits on disk, then reload and pack() back to binary.

Usage:
    # Step 1: dump
    python arsc_textdump.py dump resources.arsc resources.textproto

    # ...edit resources.textproto by hand...

    # Step 2: reload + repack
    python arsc_textdump.py load resources.textproto resources_new.arsc
"""

import sys
import pyaxml



def resources_to_textproto(arsc_path: str, text_path: str) -> None:
    from google.protobuf import text_format

    with open(arsc_path, "rb") as f:
        data = f.read()

    arsc, _ = pyaxml.ARSC.from_axml(data)

    # arsc wraps an underlying protobuf message -- the exact attribute
    # name needs to be confirmed against your installed pyaxml version
    # (see note below). Common patterns in this library are `.proto`
    # or a `get_proto()` accessor.
    proto_msg = arsc.proto  # <-- verify this attribute exists (see below)

    text_repr = text_format.MessageToString(proto_msg)

    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text_repr)

    print(f"Dumped human-readable protobuf text to {text_path}")


def resources_from_textproto(text_path: str, out_arsc_path: str) -> None:
    from google.protobuf import text_format
    from pyaxml.proto import axml_pb2

    with open(text_path, "r", encoding="utf-8") as f:
        text_repr = f.read()

    # Parse the human-edited protobuf text back into an ARSC proto message.
    new_proto = axml_pb2.ARSC()
    text_format.Parse(text_repr, new_proto)

    # Rebuild an ARSC around the edited proto. compute() recalculates all
    # chunk-size header fields, which manual edits would otherwise leave stale.
    arsc = pyaxml.ARSC.from_proto(new_proto)
    arsc.compute(recursive=True)
    packed = arsc.pack()

    with open(out_arsc_path, "wb") as f:
        f.write(packed)

    print(f"Wrote rebuilt {out_arsc_path}")


# if __name__ == "__main__":
#     if len(sys.argv) < 4:
#         print("Usage:")
#         print("  python arsc_textdump.py dump <resources.arsc> <output.textproto>")
#         print("  python arsc_textdump.py load <input.textproto> <output_resources.arsc>")
#         sys.exit(1)

#     mode, in_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

#     if mode == "dump":
#         dump_to_text(in_path, out_path)
#     elif mode == "load":
#         load_from_text(in_path, out_path)
#     else:
#         print("mode must be 'dump' or 'load'")
#         sys.exit(1)