# APKD

Umbrella project for several packages:

- **thirdparty.apkd** - Primary CLI and interface for driving all android debugging.
  - Depends on:
    - argcomplete
    - thirdparty.android.sdk
    - thirdparty.android.apk
    - thirdparty.android.emu
    - thirdparty.android.debug

- **thirdparty.android.sdk** - Android SDK management.

- **thirdparty.android.apk** - APK inspection and patching.
  - Depends on: androguard, pyyaml, protobuf, thirdparty.android.sdk

- **thirdparty.android.emu** - Android emulator management.
  - Depends on: thirdparty.android.sdk

- **thirdparty.android.debug** - Debugger implementation
  - Depends on:
    - ppadb
    - frida
    - frida-tools
    - thirdparty.jdwp
    - thirdparty.dalvik
    - thirdparty.python.repl
  - Uses JDWP for low level control of VM.
  - Uses Frida for inspection of process memory space.
  - Uses thirdparty.python.repl for IPC of debugging session.

- **thirdparty.jdwp** - For encoding, decoding, and communicating with JVM Debug Wire Protocol.
- **thirdparty.dalvik** - For disassembling dalvik bytecode.
- **thirdparty.python.repl** - Monitoring and inspect python process state in a pythonic manner.
  - Provides a IPC for REPL-ish, DB-ish, and RPC-ish like behaviors.
