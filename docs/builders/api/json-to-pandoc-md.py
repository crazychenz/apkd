#!/usr/bin/env python3

import sys, json

from typing import Any, Optional

def md_table(rows: list[dict[str, Any]], columns: Optional[list[str]] = None) -> str:
    if not rows:
        return ""
    cols = columns or list(rows[0].keys())

    widths = {c: len(c) for c in cols}
    for row in rows:
        for c in cols:
            widths[c] = max(widths[c], len(str(row.get(c, ""))))

    def fmt_row(values: list[str]) -> str:
        return "| " + " | ".join(v.ljust(widths[c]) for c, v in zip(cols, values)) + " |"

    header = fmt_row(cols)
    separator = "| " + " | ".join("-" * widths[c] for c in cols) + " |"
    body = [fmt_row([str(row.get(c, "")) for c in cols]) for row in rows]

    return "\n".join(['::: {.lefttable}', header, separator] + body + [':::'])


def main():

    # ns_dict = json.load(sys.stdin)
    with open(sys.argv[1], "r") as fobj:
        ns_dict = json.load(fobj)

    for ns_name, ns in ns_dict.items():
        #print(f"<a id=\"{ns['fqn']}\"></a>\n")
        print(f"[]{{#{ns['fqn']}}}\n")
        print(":::: {.namespace-rule}\n::::\n")
        print(f"### {ns_name}\n")
        if 'signature' in ns:
            print(f"```python\n{ns['signature']}\n```\n")

        if 'docstring' in ns:
            # TODO: Handle docstrings.
            print(f"docstring will go here\n")
        
        if 'members' in ns:
            member_list = []
            for name, member in ns['members'].items():
                entry = { 'Name': f"[`{name}`](#{member['fqn']})", 'Summary': '' }
                if 'docstring' in member and 'summary' in member['docstring']:
                    entry['Summary'] = member['docstring']['summary']
                member_list.append(entry)
                
            print(f"{md_table(member_list, ['Name', 'Summary'])}\n")

        if 'members' in ns:
            for name, member in ns['members'].items():
                #print(f"<a id=\"{member['fqn']}\"></a>\n")
                if not member['is_namespace']:
                    print(f"[]{{#{member['fqn']}}}\n")
                print(":::: {.member-rule}\n::::\n")
                print(f"#### {name}\n")
                print(f"```text\n{member['fqn']}\n```\n")

                #print(member)

                if 'docstring' in member:
                    docstr = member['docstring']
                    if 'summary' in docstr:
                        print(f"{docstr['summary']}\n")

                    if 'description' in docstr:
                        print(f"{docstr['description']}\n")

                    if 'parameters' in docstr and len(docstr['parameters']) > 0:
                        print("**Parameters:**\n")
                        for name, desc in docstr['parameters'].items():
                            print(f"  - `{name}` - {desc['annotation']} - {desc['description']}")
                        print('')

                    if 'returns' in docstr and len(docstr['returns']) > 0:
                        print("**Returns:**\n")
                        for typ, desc in docstr['returns'].items():
                            print(f"  - `{typ}` - {desc}")
                        print('')

                    if 'raises' in docstr and len(docstr['raises']) > 0:
                        print("**Raises:**\n")
                        for name, desc in docstr['returns'].items():
                            print(f"  - `{name}` - {desc}")
                        print('')

                    if 'see_also' in docstr and len(docstr['see_also']) > 0:
                        print("**See Also:**\n")
                        for desc in docstr['see_also']:
                            print(f"  - {desc}")
                        print('')

                    #print(f"{member['docstring']}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        breakpoint()


