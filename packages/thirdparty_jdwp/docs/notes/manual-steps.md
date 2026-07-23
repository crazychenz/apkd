# Manual Steps

```sh

apkd apk debugify --skip-smali-patch ./tests/labs/ignored/process/input/app-release-unsigned.apk here

# If root, may server or gadget
# If no root, gadget.
# If gadget, may patch smali (persist) or JDWP (no persist)
#   If smali patch, try manifest, or dynamically detect
#   If JDWP, may choose breakpoint, use framework breakpoint, or use METHOD_NEXT.
# Check for an array of frida and JDWP blocker fix ups

# Note: Detect root with adb? (Preference welcome)
# Note: Detect main activity with adb? (Preference welcome, manifest probable)
# Note: Develop precedence for loading? (Preference welcome.)

# --- At this point we should have frida loaded and available ---

# apkd apk debugify
# apkd apk [command]

# apkd sdk init
# apkd sdk search
# apkd sdk update
# apkd sdk install
# apkd sdk remove
# apkd sdk show

# apkd emu search <term1> <term2> <term3>
# apkd emu pull <package>
# apkd emu create <package> <avd-name>
# apkd emu start <avd-name>
# apkd emu run [--gui] <package> <avd-name> (does create and start)
# apkd emu stop <avd-name>
# apkd emu rm <avd-name>
# apkd emu rmi <package>
# apkd emu logs -f <avd-name>
# apkd emu ps (running avd)
# apkd emu ps -a (all avd)
# apkd emu images (all system image packages)
# apkd emu list shorthand (list short hand names for system-images)

# The process is:
# - debugify
#   - apk as proj
#   - proj
# - emulate
#   - package as avd
#   - avd
#   - (optional) --with-gui
# - deploy/stage
#   - jdwp-port / frida-port
# - debugger
#   - apkd
#   - jadx
#   - jdb
#   - frida

# apkd dbg [--config config_path] [--force-refresh] [--apk apk_path] \
#          [--force-download] [--image system_image] [--avd avd_name] [--with-ui|--with-gui] \
#          [--jdwp-port host:device] [--frida-port host:device] \
#          [--repl-sock host:port|path] [--exec-sock host:port|path] [--dict-sock host:port|path] \
#          [use_case_name] [proj_name]
# - proj requires apk or folder
# - avd requires image or avd
# - jdwp/frida require proj
# - use_case_name dependencies vary (implicit arguments in config?)
#   - debugify
#   - deploy - requires proj, emu
#   - stage [--no-debugify] [--no-deploy] - requires proj, emu, jdwp/frida

# python3 -m venv apkd && ./apkd/bin/python -m pip install thirdparty-apkd
# (eval "$(./apkd/bin/apkd sdk init --source)" && bash)
# Without config:
# - apkd dbg --apk `apk` --avd 'android13' --with-ui stage here
# With config:
# - apkd dbg stage here

# Panes:
# - apkd dbg logs here
# - apkd dbg logcat here
# - apkd dbg watch here
# - apkd dbg bytecode here
# - apkd dbg repl here
# - apkd dbg disassembly here
# - apkd dbg registers here

# Note: when our application crashes, we don't want to rerun all the things, they should periodically look for a new connection and refresh when one is found. This is possible because we recycle frida, jdwp, and repl sockets.

# TODO: Monitor log for triggers to perform follow on tasks and make log available via command.
# apkd emu logs --list
# TODO: How do I signature an instance of an application safely?
# apkd emu logs -f 

apkd emu stop android13 && sleep 2 && apkd emu start android13 && sleep 30 && apkd emu gui android13

apkd runtime deploy here && apkd runtime stage here && ./jdwp/entry_new.py

apkd runtime deploy --as-apk ./here/.original/pkg/original-resigned.apk && \
  apkd runtime stage --as-pkgname sh.kau.playground && sleep 2 && ./jdwp/entry_new.py


./entry_new.py
```

```sh
debugify apk as alias

debug `apk` as `alias` on `android13` emulator
```

```sh
python3 -m venv apkd && ./apkd/bin/python -m pip install thirdparty-apkd
(eval "$(./apkd/bin/apkd sdk init --source)" && bash)

apkd dbg start --foreground --log [logfile] here
```
