
import re

def parse_sdk_list(text: str):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        columns = re.split(r"\s{2,}", line)
        if len(columns) == 3:
            path, version, description = columns
            rows.append({
                "path": path,
                "version": version,
                "description": description,
            })
    return rows

def list_system_images(config, query="*"):
    import subprocess

    result = subprocess.run(
        ["android", "sdk", "list", "--all", "system-images*"],
        capture_output=True, text=True, check=True
    )
    rows = parse_sdk_list(result.stdout)

    import fnmatch

    def match_by_field(rows: list[dict], pattern: str, field: str = "path") -> list[dict]:
        return [row for row in rows if fnmatch.fnmatch(row.get(field, "").lower(), pattern.lower())]

    rows = match_by_field(rows, query)

    for row in rows:
        print(f"System Image: {row['path']}\n  Version: {row['version']}\n  Description: {row['description']}")
