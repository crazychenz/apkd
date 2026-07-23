
# Declarative Operations

To simply the spaghetti code that is the `dbg` subcommand, we are organizing the code in a declarative manner. When the user passes an operation, the subcommand will topologically sort the code that is required to make that operation executable. Each task of the process will read its given context (including config and active arguments) and determine what it needs to do for its atomic part of the process.

Each tasks can implicitly decide whether it needs to run itself or simply return to the next task in the process. For example, extraction can be skipped if not APK was provided as a CLI argument and the project folder is already created.

If the argument `--force-all-tasks` or `--force-task <task-name>` is provided, the task should not implicitly skip itself.

If the argument `--start-from <operation>` .....

Planning to include a `--start-from <operation>` argument that will cause the topological sort to be started at a given point. Therefore we can skip things we know doesn't need doing.


- extract
  - depends_on: apk (arg), proj_name (arg)
- proj_dir
  - depends_on: extract
- patch:
  - depends_on: proj_dir
- pack:
  - depends_on: proj_dir
- debugify
  - depends_on: patch, pack
- emu_pull
  - depends_on: image (arg)
- emu_create
  - depends_on: avd (arg), emu_pull
- emu_start
  - depends_on: emu_create
  - provides: emu_gui too.
- adb_uninstall
  - depends_on: emu_start, debugify
- deploy
  - depends_on: debugify, emu_gui (implicitly emu_start)
- stage
  - depends_on: deploy
- debug
  - depends_on: stage


- logs
  - depends_on: emu_gui
- logcat
  - depends_on: debug
- watch
  - depends_on: debug
- memory
  - depends_on: debug
- repl
  - depends_on: debug
- disassembly
  - depends_on: debug
- registers
  - depends_on: debug

<!-- - deploy
  - debugify
  - emu
    - pull
    - create
    - start
  - gui
  - adb
    - uninstall
    - install
- stage
  - deploy
  - configure app state
  - start app with jdwp
- debug - Debug service
  - connect to jdwp, resume VM
  - load frida, resume from frida
  - break at user defined breakpoint -->

# Desired but Not Implemented

- debug clients:
  - logs - follow log tails for debug logger output
  - logcat - follow log tail for android logger output
  - watch - monitor registers of interest
  - memory - raw memory dump
  - repl - interactive user interface
  - disassembly - monitor disassembly
  - registers - monitor all current registers
