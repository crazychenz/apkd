import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

REPO_XML_URL = "https://dl.google.com/android/repository/repository2-3.xml"
BASE_URL = "https://dl.google.com/android/repository/"


def get_cmdline_tools_packages(xml_url: str = REPO_XML_URL, base_url: str = BASE_URL, timeout: int = 30):
    """
    Fetch and parse Google's Android SDK repository XML manifest,
    returning all 'cmdline-tools;*' packages with their per-OS download URLs.

    Returns a list of dicts like:
    {
        "path": "cmdline-tools;19.0",
        "revision": "19.0",
        "archives": {
            "linux":   {"url": "...", "size": 123, "sha1": "..."},
            "macosx":  {"url": "...", "size": 123, "sha1": "..."},
            "windows": {"url": "...", "size": 123, "sha1": "..."},
        }
    }
    """

    def _local_tag(elem):
        """Strip XML namespace prefix, e.g. '{...}remotePackage' -> 'remotePackage'."""
        return elem.tag.split("}", 1)[-1] if "}" in elem.tag else elem.tag

    resp = requests.get(
        xml_url,
        timeout=timeout,
        headers={"User-Agent": "Mozilla/5.0 (compatible; sdk-tools-fetch/1.0)"},
    )
    resp.raise_for_status()

    root = ET.fromstring(resp.content)

    packages = []

    # remotePackage elements can appear anywhere in the tree, namespaced.
    for pkg in root.iter():
        if _local_tag(pkg) != "remotePackage":
            continue

        path = pkg.get("path", "")
        if not path.startswith("cmdline-tools"):
            continue

        # revision: <revision><major>X</major><minor>Y</minor><micro>Z</micro></revision>
        revision = None
        for child in pkg:
            if _local_tag(child) == "revision":
                parts = []
                for part in ("major", "minor", "micro"):
                    for sub in child:
                        if _local_tag(sub) == part:
                            parts.append(sub.text)
                revision = ".".join(p for p in parts if p is not None)

        archives = {}
        for archives_el in pkg:
            if _local_tag(archives_el) != "archives":
                continue
            for archive_el in archives_el:
                if _local_tag(archive_el) != "archive":
                    continue

                host_os = None
                url = None
                size = None
                sha1 = None

                for a_child in archive_el:
                    tag = _local_tag(a_child)
                    if tag == "host-os":
                        host_os = a_child.text
                    elif tag == "complete":
                        for c in a_child:
                            ctag = _local_tag(c)
                            if ctag == "url":
                                url = urljoin(BASE_URL, c.text)
                            elif ctag == "size":
                                size = int(c.text) if c.text else None
                            elif ctag == "checksum":
                                sha1 = c.text

                # Packages with no <host-os> apply to all platforms
                key = host_os or "all"
                archives[key] = {"url": url, "size": size, "sha1": sha1}

        packages.append({
            "path": path,
            "revision": revision,
            "archives": archives,
        })

    return packages


def get_latest_cmdline_tools_url(platform: str = "linux",
                                  xml_url: str = REPO_XML_URL,
                                  base_url: str = BASE_URL):
    """
    Convenience wrapper: returns the download URL for the highest-numbered
    cmdline-tools revision for the given platform ('linux', 'macosx', 'windows').
    """
    packages = get_cmdline_tools_packages(xml_url=xml_url, base_url=base_url)
    if not packages:
        raise RuntimeError("No cmdline-tools packages found in manifest")

    def sort_key(pkg):
        try:
            return tuple(int(x) for x in (pkg["revision"] or "0").split("."))
        except ValueError:
            return (0,)

    packages.sort(key=sort_key, reverse=True)

    for pkg in packages:
        archive = pkg["archives"].get(platform)
        if archive and archive.get("url"):
            return archive["url"]

    raise RuntimeError(f"No archive found for platform '{platform}'")


# if __name__ == "__main__":
#     for pkg in get_cmdline_tools_packages():
#         print(pkg["path"], "rev", pkg["revision"], "->", list(pkg["archives"].keys()))

#     print("\nLatest linux download:")
#     print(get_latest_cmdline_tools_url("linux"))