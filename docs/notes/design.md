# Design Notes

Over all, we're looking at 4 categories:

- apk - APK patching
- emulator - Android emulator management
- adb - Runtime application management
- debug - Runtime debugging

To efficiently manage all of the states, emulator, adb, and debug all start an apkd service. The emulator, adb, and debug then become merely clients to the running server. In reality, using adb and emulator start their own services and jwdp and frida start their own on device services, therefore running apkd can potentially run 5 different services at once.

## apkd config

- `apkd config init <config.yaml>`
  - Generate a new config file.

## apkd apk

- `apkd apk ls <apk_path>`
  - Display all the files without extraction.

- `apkd [--config <config_yaml>] apk extract <apk_path> <apk_content_path>`
  - Extract the APK into file system
  - Decoded AndroidManifest.xml

- `apkd [--config <config_yaml>] apk patch debug <apk_content_path>`
  - Add debug flag to manifest.

- `apkd [--config <config_yaml>] apk patch frida <apk_content_path>`
  - Patch package with manifest.

- `apkd [--config <config_yaml>] apk pack <apk_content_path> <new_apk_path>`
  - Encode AndroidManifest.xml
  - Zip the content path.
  - Zip align file.
  - Sign package.

- `apkd [--config <config_yaml>] apk prepare <apk_content_path> <new_apk_path>`
  - Do all the things required for dynamic access.

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

- `apkd [--config <config_yaml>] adb [--device <device>] install <application>`
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