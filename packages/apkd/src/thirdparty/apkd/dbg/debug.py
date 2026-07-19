
import asyncio
from thirdparty.jdwp import Jdwp, Byte, Boolean, Int, String, ReferenceTypeID

from thirdparty.sandbox.repl import Repl
import thirdparty.debug.dalvik
from thirdparty.debug.dalvik.util.adb import AdbObject
from thirdparty.debug.dalvik.util.native import NativeObject
from thirdparty.debug.dalvik.util.breakpoint import parse_dex_header, parse_vregs
from thirdparty.debug.dalvik.info.breakpoint import instruction_str
from thirdparty.debug.dalvik.info.state import *

# Utility imports
import pdb
from fuzzyfinder import fuzzyfinder
from pprint import pprint

class BreakpointObject(): pass
bp = BreakpointObject()
jdwp = None
dbg = thirdparty.debug.dalvik.Debugger()
dbg_state = dbg.state


async def main():
    global dbg
    global jdwp
    global bp

    # Connect to application with our debugger.
    print("Connecting debugger to localhost:8700")
    await dbg.start('127.0.0.1', 8700)
    jdwp = dbg.jdwp
    dbg.print_summary()


    async def load_gadget_on_break(event, composite, args):
        bp_info, = args
        await bp_info.dbg.disable_breakpoint_event(event.requestID)
        print(f"Breakpoint hit on thread {event.thread}; injecting frida-gadget...")
        await bp_info.dbg.system_load_gadget("frida-gadget", thread_id=event.thread)
        print('frida-gadget injection returned; resuming VM.')
        await bp_info.dbg.resume_vm()

    loadGadget = dbg.create_breakpoint(**{
        'class_signature': 'Landroid/os/Handler;',
        'method_name': 'dispatchMessage',
        'method_signature': '(Landroid/os/Message;)V',
    }, callback=load_gadget_on_break)
    bp.loadGadget = loadGadget
    await loadGadget.set_breakpoint()

    await asyncio.get_running_loop().run_in_executor(None, input, "Press Enter to resume VM...\n")

    await dbg.resume_vm()

    try:
        print("Waiting for events... Ctrl-C to quit.")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        exit(0)


async def main_with_sandbox():
    socket_path = "/tmp/asyncrepl.sock"
    repl_coro = Repl(namespace=globals()).start_repl_server(socket_path=socket_path)
    repl_task = asyncio.create_task(repl_coro)
    main_task = asyncio.create_task(main())
    await asyncio.gather(repl_task, main_task)

