#!/usr/bin/env python3

'''
    We provide a list of all things to document (exports, explicit nodes). The same list will have a 
    reverse lookup from the simple member name. All of these are put in a flat dictionary of fqns. While 
    documenting classes, functions, or other members, if a member path matches an entry in the fqn 
    database, we add a hyperref as if there will be an anchor. Adding double backticks to a label will
    cause a reverse lookup and hyperref to the fqn anchor in the same way.
'''


from pprint import pprint

import griffe

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


def prototype(func) -> str:
    parts = []
    for p in func.parameters:
        if p.name == "self" or p.name == "cls":
            continue

        # prefix for *args and **kwargs
        if p.kind == griffe.ParameterKind.var_positional:
            name = f"*{p.name}"
        elif p.kind == griffe.ParameterKind.var_keyword:
            name = f"**{p.name}"
        elif p.kind == griffe.ParameterKind.keyword_only:
            name = p.name          # caller must add bare * separator
        else:
            name = p.name

        segment = name
        if p.annotation:
            segment += f": {p.annotation}"
            # TODO: Consider adding cross references to annotations that include registered classes
        if p.default:
            segment += f" = {p.default}"

        parts.append(segment)

    returns = f" -> {func.returns}" if func.returns else ""
    return f"def [`{func.name}`](#{func.path})``({', '.join(parts)}){returns}"


def clean_text(text: str, anchor_map: dict) -> str:
    import re

    def resolve(m):
        name = m.group(1)
        if name in anchor_map:
            return f"[`{name}`]({anchor_map[name]})"
        return f"`{name}`"   # fallback to plain code if not found

    text = re.sub(r'``(.+?)``', resolve, text)
    return text

def render_class(fqns, bigscope, restrictions, klass):
    # print(f"Class Name: {item['alias']}") # item_api.name
    # print(f"Class FQN: {item['fqn']}") # item_api.path

    klass_name = klass.name
    bases = ', '.join([base.name for base in klass.bases])
    decorators = [f"@{str(d.value)}" for d in klass.decorators]
    members = list(klass.members.keys())

    if klass.path in restrictions:
        restrict = restrictions[klass.path]
        if 'alias' in restrict:
            klass_name = restrict['alias']
        if 'allow_members' in restrict:
            members = restrict['allow_members']
        if 'deny_members' in restrict:
            for deny in restrict['deny_members']:
                if deny in members:
                    member.remove(deny)

    
    print(f'\n<a id="{klass.path}"></a>\n')
    #print("--------------------------------------------------------------")
    print("::: {.hrule}\n:::\n")
    print(f'[{klass_name}]{{.largetext}}\n')
    #print("--------------------------------------------------------------\n")

    if len(decorators) > 0:
        print("```python")
        for decorator in decorators:
            print(decorator)
        print(f"{klass.kind.value} {klass_name}({bases})")
        print("```")
    else:
        print(f"```python\n{klass.kind.value} {klass_name}({bases})\n```")
    

    # # Handle docstring
    # print("Class Documentation:")
    # for doc_item in item_api.docstring.parsed:
    #     if doc_item.kind.value == griffe.DocstringSectionKind.text:
    #         '''
    #             TODO: Track all double quotes as explicit references. Need to track this items's 
    #             path with the double back ticked reference for possible scoping resolution.
    #             For now, we can ease the implementation by making any conflicts in alias
    #             space an error and then only add the above resolution after we find a real
    #             world conflict.
    #         '''
    #         print(clean_text(doc_item.value, ()))
    #     else:
    #         breakpoint()
    
    # If first line of docstring is text, use as short description.
    # TODO: Probably will break if it includes anything special (class, function, etc)
    if len(klass.docstring.parsed) > 0 and klass.docstring.parsed[0].kind == griffe.DocstringSectionKind.text:
        print(klass.docstring.parsed[0].value)

    # Add member table.
    klass_funcs = []
    klass_funcs_api = []
    klass_attrs = []

    for member_name in members:
        member_api = klass.members[member_name]

        if member_api.kind == griffe.Kind.FUNCTION:
            klass_funcs.append({"Prototype": prototype(member_api)})
            klass_funcs_api.append((klass_funcs[-1], member_api))
        elif member_api.kind == griffe.Kind.ATTRIBUTE:
            klass_attrs.append({"Attribute": member_api.name, "Default": member_api.value})
        else:
            print(f"Unknown kind in member table: {member_api.path} {member_api.kind}")
            breakpoint()

    if len(klass_attrs) > 0:
        print("\n**Attributes**\n")
        print(md_table(klass_attrs))
    if len(klass_funcs) > 0:
        print("\n**Functions**\n")
        print(md_table(klass_funcs))

    

    # TODO: Display each attribute description
    # TODO: Display each function description.
    for method in klass_funcs_api:
        print("\n--------------------------------------------------------------\n")
        method_proto = method[0]["Prototype"]
        method_api = method[1]
        print(f'\n<a id="{klass.path}.{method_api.name}"></a>\n')
        # TODO: Add bound to this loop.
        while method_api.kind == griffe.Kind.ALIAS:
            method_api = method_api.target
        # TODO: Add decorators.
        if member_api.docstring is not None:
            print(f"**{method_proto}**\n")
            sections = member_api.docstring.parse("google")
            for section in sections:
                if section.kind == griffe.DocstringSectionKind.text:
                    # TODO: Parse the string for ``
                    print(section.value)
                elif section.kind == griffe.DocstringSectionKind.parameters:
                    print("\n- **Parameters:**")
                    for param_entry in section.value:
                        print(f"  - {param_entry.annotation} - {param_entry.description}")
                elif section.kind == griffe.DocstringSectionKind.returns:
                    print("\n- **Returns:**")
                    for ret_entry in section.value:
                        print(f"  - {ret_entry.annotation} - {ret_entry.description}")
                elif section.kind == griffe.DocstringSectionKind.raises:
                    print("\n- **Raises:**")
                    for exc_entry in section.value:
                        # TODO: Add link for annotation
                        print(f"  - {exc_entry.annotation} - {exc_entry.description}")
                else:
                    print(section.kind, section.value)
                    breakpoint()
        #breakpoint()


# --- Do a preliminary inspection of the all the top level things we want to document ---

def main():

    print("## 5.2 Test API")

    exports_to_load = [
        'thirdparty.pparse.lib'
    ]

    restrictions = {
        'thirdparty.pparse.lib.Node': {
            # Optionally we can replace item.name with explicit alias.?
            #'alias': 'Node',
            # The active entry we're restricting
            'fqn': 'thirdparty.pparse.lib.Node',
            
            # No need yet, but griffe can takes a search_paths
            # 'search_paths': [ { 'path': '.' }, ],

            # deny always wins
            'deny_members': [ '_ctx' ],
            # allow implies limited set
            'allow_members': [
                'clear_ctx',
                'ctx',
                'dump',
                'from_xml',
                'length',
                'load',
                'set_length',
                'tell',
                'unload',
                'value',
            ],
        }
    }

    fqns = {}
    bigscope = {}

    # Load exports
    for export_to_load in exports_to_load:
        fqns[export_to_load] = griffe.load(export_to_load)
        for export_name in fqns[export_to_load].exports:
            export = fqns[export_to_load].members[export_name]
            fqns[export.path] = export



    # Populate Reverse Lookup
    for fqn, member in fqns.items():
        if member.name in bigscope:
            raise Exception(f"Duplicate class name while populated rev lookup: {fqn}")
        bigscope[member.name] = fqn


    # Generate markdown with full anchor map
    for member in fqns.values():
        if member.kind == griffe.Kind.MODULE:
            # TODO: Organize things by module.
            continue
        elif member.kind == griffe.Kind.ATTRIBUTE:
            # TODO: This makes more sense in module context.
            print(f"Attribute: {member.name} = {member.value}")
        elif member.kind == griffe.Kind.CLASS:
            render_class(fqns, bigscope, restrictions, member)
        elif member.kind == griffe.Kind.ALIAS:
            print(f"<!-- ALIAS: {member.name} is {member.target_path} -->")
        else:
            print(f"Unknown kind: {member.kind.value}")
            breakpoint()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        breakpoint()


# to_document = [
#     {
#         'item': {
#             'alias': 'Node',
#             'fqn': 'thirdparty.pparse.lib.Node',
#             # 'search_paths': [ { 'path': '.' }, ],
#             'included_members': [
#                 { 'member': 'clear_ctx' },
#                 { 'member': 'ctx' },
#                 { 'member': 'dump' },
#                 { 'member': 'from_xml' },
#                 { 'member': 'length' },
#                 { 'member': 'load' },
#                 { 'member': 'set_length' },
#                 { 'member': 'tell' },
#                 { 'member': 'unload' },
#                 { 'member': 'value' },
#             ],
#         },
#     },
# ]

# for _item in to_document:
#     item = _item['item']
#     item_api = griffe.load(item['fqn'])

#     if item_api.is_class:
#         render_class(item, item_api)

#     breakpoint()

    