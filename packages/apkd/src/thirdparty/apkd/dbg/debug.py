
import logging
log = logging.getLogger(__name__)

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


# ** Keeping these in global scope for proof of concept. **
# TODO: These need to move to a class instance.
native_device = None
native_session = None
native_script = None
native_rpc = None


def native_connect(self, proc_pid, frida_port='127.0.0.1:27042'):
    import frida
    from thirdparty.apkd.dbg.native import RPC_SCRIPT

    global native_device
    global native_session
    global native_script
    global native_rpc

    native_device = frida.get_device_manager().add_remote_device(frida_port)
    #native_device = frida.get_usb_device()

    native_session = device.attach(proc_pid)    
    if native_session:
        # Add utility function.
        native_script = native_session.create_script(RPC_SCRIPT)
        native_script.on("message", lambda msg, data: print("FRIDA MESSAGE:", msg, data))
        native_script.load()
        native_rpc = native_script.exports_sync
        print("native_rpc is set.")
        #print("ping -> ", self.rpc.ping())



async def main(ctx):
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
        # Need to run this somewhere: native_connect(ctx["proc_pid"])
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


async def main_with_sandbox(ctx):
    socket_path = "/tmp/asyncrepl.sock"
    repl_coro = Repl(namespace=globals()).start_repl_server(socket_path=socket_path)
    repl_task = asyncio.create_task(repl_coro)
    main_task = asyncio.create_task(main(ctx))
    await asyncio.gather(repl_task, main_task)

