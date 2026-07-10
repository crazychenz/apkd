import re, os, glob

# Make headings deeper.
new_lines = []
with open('manual/5-api-reference/5.x-python-api.md', 'r') as fobj:
    for line in fobj.readlines():
        if line.startswith('#'):
            new_lines.append(f"##{line}")
        else:
            new_lines.append(line)
with open('manual/5-api-reference/5.x-python-api.md', 'w') as fobj:
    fobj.write(''.join(new_lines))

# Make the anchors work with markdown.
anchor_map = {}
#for path in glob.glob("docs/api/**/*.md", recursive=True):
for path in ['manual/5-api-reference/5.x-python-api.md']:
    with open(path) as f:
        for line in f:
            m = re.match(r'<a id="([^"]+)"></a>', line)
            if m:
                fqn = m.group(1)                    # my_framework.parse.tokenizer.TokenStream
                short = fqn.rsplit(".", 1)[-1]       # TokenStream
                #anchor_map[short] = f"{path}#{fqn}"
                anchor_map[short] = f"#{fqn}"

# Then in each .md file, replace bare backtick names with links
BACKTICK = re.compile(r'``([A-Z][A-Za-z0-9_]+)``')   # crude: capitalised names only

#for path in glob.glob("docs/api/**/*.md", recursive=True):
for path in ['manual/5-api-reference/5.x-python-api.md']:
    text = open(path).read()
    def replace(m):
        name = m.group(1)
        if name in anchor_map:
            return f"[{name}]({anchor_map[name]})"
        return m.group(0)
    open(path, "w").write(BACKTICK.sub(replace, text))