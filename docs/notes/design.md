# Design Notes

Over all, we're looking at 4 categories:

- apk - APK patching
- emulator - Android emulator management
- adb - Runtime application management
- debug - Runtime debugging

To efficiently manage all of the states, emulator, adb, and debug all start an apkd service. The emulator, adb, and debug then become merely clients to the running server. In reality, using adb and emulator start their own services and jwdp and frida start their own on device services, therefore running apkd can potentially run 5 different services at once.

## apkd Folders

- Configuration
  - `~/.config/apkd/config.yaml`
  - `~/.config/apkd/keystore/default.keystore`
- Original Artifacts for forensic analysis
  - `<apkalias>/.original/files/original-sig.apk` - The original APK with original signature
  - `<apkalias>/.original/files/original-resigned.apk` - The original APK with new signature.
  - `<apkalias>/.original/apk/` - Unzipped `original.apk` ... no decoding or dex extraction.
- Working Artifacts for alterations and instrumentation.
  - `<apkalias>/working/apk/` - Decoded axml and arsc **with dex removed**.
  - `<apkalias>/working/dex/<dexname>` - Extracted dex file content
  - `<apkalias>/working/output/working.apk` - Altered APK (signed and to be installed in emulator).
- Build Artifacts for temporally assembling patched apk.
  - `<apkalias>/.build/dex/<dexname>.dex` - Built dex from `<apkalias>/working/dex/<dexname>`
  - `<apkalias>/.build/apk/` - Encoded axml, arsc.
  - `<apkalias>/.build/pkg/unaligned.apk` - Initial unaligned packaged apk.
  - `<apkalias>/.build/pkg/unsigned.apk` - Aligned, but unsigned apk.

## apkd config

- `apkd config init [<config_path>`
  - Generate a new config file and keystore.

## apkd apk

- `apkd apk ls <apk_path>`
  - Display all the files without extraction.

- `apkd apk manifest <apk_path> [<resource>]`
  - same as `androguard axml <apk_path>` (no extraction)

- `apkd apk resources <apk_path> [<resource>]`
  - same as `androguard arsc <apk_path>` (no extraction)

- `apkd [--config <config_yaml>] apk extract [-f] <apk_path> [<apk_content_path>]`
  - `-f` - Force (i.e. delete apk_content_path before we begin.)
  - Default: no path means it'll use the file part of the apk to generate a folder (if one does not exist)
  - Note: If `apk_content_path` does not start with `/` or `.` or `~`, we assume its _apkalias_.
  - Extract APK and immediately build APK to verify full pipeline works.
    - Decoded AndroidManifest.xml, resources.arsc, dex (if baksmali available)

- `apkd [--config <config_yaml>] apk patch debug <apk_content_path>`
  - Add debug flag to manifest in working copy. (Does full build.)

- `apkd [--config <config_yaml>] apk patch frida <apk_content_path>`
  - Patch package with manifest in working copy. (Does full build.)

- `apkd [--config <config_yaml>] apk pack <apk_content_path> [<new_apk_path>]`
  - Do full build with updates in working structure:
    - Encode AndroidManifest.xml / resources.arsc
    - Build smali into dex
    - Zip the content path.
    - Zip align file.
    - Sign package.

- `apkd [--config <config_yaml>] apk prepare <apk_content_path> [<new_apk_path>]`
  - Make debuggable and patch in Frida gadget in one step.
  - Optionally use adb to dynamically detect where to patch frida.

### apkd apk Parameters

- `<new_apk_path>` - Where apkd will manage the extracted APK
  - Special folder structure specific to apkd

- `--config config.yaml` - Default commands, paths, etc
- `--ks` - keystore
- `--kspass` - keystore password
- `--keyname` - key name
- `--keypass` - key password

## apkd emulator

- `apkd [--config <config_yaml>] emulator get`
  - sdkmanager install
- `apkd [--config <config_yaml>] emulator create`
  - avdmanager create avd
- `apkd [--config <config_yaml>] emulator start`
  - emulator
- `apkd [--config <config_yaml>] emulator stop`
  - pskill emulator

### apkd emulator Parameters

- `--sdk <path>` - Android SDK Path

## apkd adb

- `apkd [--config <config_yaml>] adb [--device <device>] deploy <application>`
  - uninstall apk
  - install apk

- `apkd [--config <config_yaml>] adb [--device <device>] wait <application>`
  - Do `apkd adb install`
  - Enable Developer Tools, Indicate "Wait For Debugger", Add target application.

- `apkd [--config <config_yaml>] adb [--device <device>] start <application>`
  - Start the application from emulator.

- `apkd [--config <config_yaml>] adb [--device <device>] jdwp [--port <port>] <application>`
  - Start jdwp
  - Forward port

- `apkd [--config <config_yaml>] adb [--device <device>] debug [--port <port>] <application>`
  - Attach to JDB with apkd JWDP handler.

- `apkd [--config <config_yaml>] adb [--device <device>] easy-debug [--port <port>] <application>`
  - apkd adb install
  - apkd adb wait
  - apkd adb start
  - apkd adb jdwp
  - apkd adb debug
