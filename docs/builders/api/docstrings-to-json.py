#!/usr/bin/env python3

'''
    We provide a list of all things to document (exports, explicit nodes). The same list will have a 
    reverse lookup from the simple member name. All of these are put in a flat dictionary of fqns. While 
    documenting classes, functions, or other members, if a member path matches an entry in the fqn 
    database, we add a hyperref as if there will be an anchor. Adding double backticks to a label will
    cause a reverse lookup and hyperref to the fqn anchor in the same way.
'''

import logging
log = logging.getLogger(__name__)
from pprint import pprint

import sys
import griffe
import json

from typing import Any, Optional

# --- Do a preliminary inspection of the all the top level things we want to document ---


'''
Three levels: module, namespace, member

Each module gets its own page.

We want the namespace list flat:
'''


def klass_signature(klass) -> str:
    klass_name = klass.name
    bases = ', '.join([base.name for base in klass.bases])
    decorators = [f"@{str(d.value)}" for d in klass.decorators]
    signature_list = []
    if len(decorators) > 0:
        for decorator in decorators:
            signature_list.append(decorator)
    signature_list.append(f"{klass.kind.value} {klass_name}({bases})")
    return '\n'.join(signature_list)


def func_signature(func) -> str:
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
    return f"def [`{func.name}`](#{func.path})({', '.join(parts)}){returns}"


def get_namespaces(ns_list = [], p_target = None, allowed_module=''):
    if p_target is None:
        return ns_list

    target = p_target
    if isinstance(target, str):
        #print(f"Skipping str {target}")
        return ns_list
    if isinstance(target, griffe.Alias):
        try:
            target.resolve_target()
        except Exception as exc:
            #print(f"Skipping alias {target.target_path}")
            return ns_list
        target = target.final_target

    if target.canonical_path == allowed_module:
        pass
    elif isinstance(target, griffe.Attribute) or isinstance(target, griffe.Module):
        return ns_list

    if isinstance(target, griffe.Class) or isinstance(target, griffe.Function) or isinstance(target, griffe.Module):
        if len(target.members) > 0:
            log.debug(f"Adding {target.canonical_path} {type(target)}")
            ns_list.append(target)
            for name, member in target.members.items():
                ns_list = get_namespaces(ns_list, member)
    else:
        log.debug(f"Found {type(target)}")
        breakpoint()

    return ns_list


def parse_list_admonition(admonition_text: str) -> list[tuple[Optional[str], str]]:
    """Split an admonition's raw text into (name, description) items.

    A new item starts at a line with no leading whitespace.
    Any line that starts with whitespace is a continuation of the previous item.
    """
    items: list[tuple[str | None, str]] = []
    current_lines: list[str] = []

    for line in admonition_text.split("\n"):
        if line and not line[0].isspace():
            # New item starts here.
            if current_lines:
                items.append(current_lines)
            current_lines = [line]
        else:
            # Continuation line: strip the common extra indent.
            current_lines.append(line.strip())

    if current_lines:
        items.append(current_lines)

    parsed_items = []
    for item_lines in items:
        if ":" in item_lines[0]:
            name, first_desc_line = item_lines[0].split(":", 1)
            name = name.strip()
            description = "\n".join([first_desc_line.strip(), *item_lines[1:]]).strip()
        else:
            name, description = None, "\n".join(item_lines).strip()
        parsed_items.append((name, description))

    return parsed_items


def process_docstring(docstring, member_dict):

    """
        Note: At the moment, this function only handles a small number of available sections.

        'Docstring',
        'DocstringDetectionMethod',
        'DocstringElement',
        'DocstringNamedElement',
        'DocstringSection',
        'DocstringSectionExamples',
        'DocstringSectionKind',
        'DocstringSectionOtherParameters',
        'DocstringStyle',
        'DocstringSectionText',

        'DocstringAdmonition',
        'DocstringAttribute',
        'DocstringClass',
        'DocstringDeprecated',
        'DocstringFunction',
        'DocstringModule',
        'DocstringOptions',
        'DocstringParameter',
        'DocstringRaise',
        'DocstringReceive',
        'DocstringReturn',
        'DocstringTypeAlias',
        'DocstringTypeParameter',
        'DocstringWarn',
        'DocstringYield',

        'DocstringSectionAdmonition',
        'DocstringSectionAttributes',
        'DocstringSectionClasses',
        'DocstringSectionDeprecated',
        'DocstringSectionFunctions',
        'DocstringSectionModules',
        'DocstringSectionParameters',
        'DocstringSectionRaises',
        'DocstringSectionReceives',
        'DocstringSectionReturns',
        'DocstringSectionTypeAliases',
        'DocstringSectionTypeParameters',
        'DocstringSectionWarns',
        'DocstringSectionYields',
    """


    description = []
    parameters = {}
    returns = {}
    raises = {}
    see_also = []

    sections = docstring.parse("google")
    summary = docstring.value.split("\n", 1)[0]

    #if member_dict['fqn'] == 'thirdparty.pparse.lib.node.RecursiveControl':
    #    breakpoint()

    for section in sections:
        try:
            if isinstance(section, griffe.DocstringSectionText): #section.kind == griffe.DocstringSectionKind.text:
                desc_part = section.value
                if len(description) == 0 and len(summary) > 0 and desc_part.startswith(summary):
                    desc_part = desc_part[len(summary):]
                description.append(desc_part)
            elif isinstance(section, griffe.DocstringSectionParameters): #section.kind == griffe.DocstringSectionKind.parameters:
                for param_entry in section.value:
                    parameters[str(param_entry.name)] = {
                        'annotation': str(param_entry.annotation),
                        'name': str(param_entry.name),
                        'description': str(param_entry.description),
                        'default': str(param_entry.default),
                    }
            elif isinstance(section, griffe.DocstringSectionReturns): #section.kind == griffe.DocstringSectionKind.returns:
                for ret_entry in section.value:
                    returns[str(ret_entry.annotation)] = ret_entry.description
            elif isinstance(section, griffe.DocstringSectionRaises): #section.kind == griffe.DocstringSectionKind.raises:
                for exc_entry in section.value:
                    raises[str(exc_entry.annotation)] = exc_entry.description
            elif isinstance(section, griffe.DocstringSectionAdmonition) and section.title == "See Also":
                for name, description in parse_list_admonition(section.value.description):
                    see_also.append({'name': name, 'description': description})
            else:
                log.debug(section.kind, section.value)
                breakpoint()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            log.debug(exc)
            breakpoint()
    
    member_dict['docstring'] = {
        'summary': summary,
        'description': ' '.join(description),
        'parameters': parameters,
        'returns': returns,
        'raises': raises,
        'see_also': see_also,
        # TODO: Add the others
    }


def main():

    fqns = {}
    griffe_exports = {}

    exports_list = sys.argv[1:] #['thirdparty.pparse.lib']
    exports_dict = {}

    # TODO: Consider adding filters or restrictions.

    for fq_export in exports_list:
        exports_dict[fq_export] = {'griffe': griffe.load(fq_export)}

        # Because we ignore modules, we must add explicit export manually.
        export_namespaces = [exports_dict[fq_export]['griffe']]
        #get_namespaces(export_namespaces, export_namespaces[0], fq_export)

        for name, g_member in exports_dict[fq_export]['griffe'].members.items():
            exports_dict[fq_export]['namespaces'] = get_namespaces(export_namespaces, g_member)

        log.debug("GOT NAMESPACES")

        ns_dict = {}
        for ns in exports_dict[fq_export]['namespaces']:

            log.debug(f"PROCESSING NAMESPACE {ns}")

            # Populate ns_dict for use as is_namespace lookup.
            ns_dict[ns.canonical_path] = {
                'fqn': ns.canonical_path,
            }

            if isinstance(ns, griffe.Class):
                ns_dict[ns.canonical_path]['signature'] = klass_signature(ns)

            if hasattr(ns, 'docstring') and ns.docstring is not None:
                process_docstring(ns.docstring, ns_dict[ns.canonical_path])

            # Intentionally added here to have member appear last
            ns_dict[ns.canonical_path]['members'] = {}
        
        # ! TODO: Consider the members that are namespaces. Do we duplicate, defer, skip?

        log.debug("PROCESSING ALL NAMESPACE MEMBERS")
        for ns in exports_dict[fq_export]['namespaces']:
            for name, p_member in ns.members.items():
                log.debug(f"PROCESSING NAMESPACE MEMBER {name}")
                fqn = f'{ns.canonical_path}.{name}'

                member = p_member
                if isinstance(member, griffe.Alias):
                    try:
                        member.resolve_target()
                    except Exception as exc:
                        log.debug(f"Skipping alias {fqn}")
                        continue
                    member = member.final_target

                # if fqn == 'thirdparty.pparse.lib.EndOfNodeException':
                #     breakpoint()

                ns_dict[ns.canonical_path]['members'][name] = {
                    'fqn': fqn,
                    'is_namespace': fqn in ns_dict,
                    'is_attribute': isinstance(member, griffe.Attribute),
                    'is_exception': False,
                }

                member_entry = ns_dict[ns.canonical_path]['members'][name]

                if hasattr(member, 'bases'):
                    member_entry['is_exception'] = 'Exception' in [str(base) for base in member.bases]

                if isinstance(member, griffe.Function):
                    member_entry['signature'] = func_signature(member)

                try:
                    # Parse docstring.
                    if hasattr(member, 'docstring') and member.docstring is not None:
                        process_docstring(member.docstring, ns_dict[ns.canonical_path]['members'][name])
                except Exception as exc:
                    # NOTE: logging throws this, not sure why.
                    #import traceback
                    #traceback.print_exc()
                    #print(exc)
                    continue
                

        # ** At this point ns_dict should be complete an ready for json to markdown conversion.

        log.debug("SAVING TO JSON")

        # TODO: Control the output path.
        #with open(f'{fq_export}-api.json', 'w') as fobj:
        #    import json
        #    fobj.write(json.dumps(ns_dict))
        print(json.dumps(ns_dict))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        breakpoint()


