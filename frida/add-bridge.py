
# https://github.com/frida/frida/issues/3460

def load_bridge(lang):
	import os
	import importlib.util

	# Calculate frida-tools module path without loading it (we don't need to)
	frida_tools_path = os.path.dirname(importlib.util.find_spec('frida_tools').origin)

	# Calculate the bridge location and load it
	bridge_file = os.path.join(frida_tools_path, 'bridges', f'{lang.lower()}.js')
	with open(bridge_file, 'r', encoding='utf-8') as f:
		bridge_src = f.read()

	# Wrap with the setter and return
	return '(function() { ' + bridge_src + '; Object.defineProperty(globalThis, "' + lang + '", { value: bridge }); })();\n'

# Load as usual
with open('script.js') as f:
	source = f.read()

# Prepend the Java bridge - note the bridge language is CASE SENSITIVE!
source = load_bridge('Java') + source

print(source)