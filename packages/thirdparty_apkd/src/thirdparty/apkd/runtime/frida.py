#!/usr/bin/env python3


'''
Test Use Case:

Setup Debugger
Add breakpoint
On breakpoint:
  - Get the treadID
  - Dereference threadID to get nativePeer
  - Using nativePeer, fetch vregs from ShadowFrame (Given Android Version).
  - Using typeID of object in location from breakpoint:
  - Dereference class to fetch dexCache object
  - Using dexCache object, fetch location String (may lead to specific dex file)
  - CONSIDER: Can we read directly from the following in dexCache (via Frida):
    - resolvedFields, resolvedMethods, resolvedTypes, strings
  - Note: DexCache.java docs dexCache as "c array pointers as they become resolved."
      
'''

'''
await dbg.cli_frame(26092)
await dbg.cli_frame_values(26092, 131072)
await dbg.cli_object_values()
'''

import asyncio
from thirdparty.jdwp import Jdwp, Byte, Boolean, Int, String, ReferenceTypeID

from thirdparty.python.repl.repl import Repl
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


# We're keeping jdwp, dbg, and dbg_state in global scope so
# they remain accessible to REPL mechanisms.
adb = AdbObject()
native = NativeObject()
class BreakpointObject(): pass
bp = BreakpointObject()
jdwp = None
dbg = thirdparty.debug.dalvik.Debugger()
dbg_state = dbg.state


'''
Areas Of Instrumentation:

- Emulator with Kernel Output (Android 13)
- Frida Server Pushed To /data and made executable.
- Frida Server verifiably running

- APK File Marked Debuggable
- (Optionally) APK Analyzed by Androguard with content cached for later usage.
- APK File Installed As App

1. App Configured For JDWP Debug
2. App Launched and waiting for Debugger
3. App PID fetched.
4. App JDWP port forwarded to 8700.
5. Debugger attached to App via tcp:8700.
  - Standard Debugger initialization started.
  - Setup initial breakpoints.
  - Once JVM is waiting for events, continue to 6.
6. Connect/inject Frida into app via PID.

# On Breakpoint:

1. (Via Single Call) Get the vregs via the nativePeer of target threadID (using Frida connection).
2. (Via Single Call) Get the dexCache for *this* object and resolve relevant thing. 

'''

async def main():
    global dbg
    global jdwp
    global native
    global adb
    global bp

    # Start up the application in debug mode.
    # **Note: No need to start application because we've done this in a separate command.
    # adb.target('sh.kau.playground')

    # TODO: If we're using frida-server, this may work.
    # TODO: It we're using frida-gadget, we need to load the gadget from debugger.

    # Connect to application native access.
    # This is the frida entry point
    # **Note: No need to connect to frida first, we'll do it in debugger.
    #native.connect(adb)

    # **Note: No need to settle because we've done this in a separate command.
    # # Settle a bit.
    # settle_timeout = 3
    # print(f"Sleeping {settle_timeout} secs for system to settle.")
    # await asyncio.sleep(settle_timeout)

    # Connect to application with our debugger.
    print("Connecting debugger to localhost:8700")
    await dbg.start('127.0.0.1', 8700)
    jdwp = dbg.jdwp
    dbg.print_summary()

    # fetchQuote = dbg.create_breakpoint(**{
    #     'class_signature': 'Lsh/kau/playground/quoter/QuotesRepoImpl;',
    #     'method_name': 'fetchQuote',
    #     'method_signature': '(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;',
    # }, callback=None)
    # bp.fetchQuote = fetchQuote
    # await fetchQuote.set_breakpoint()

    # quoteForTheDay = dbg.create_breakpoint(**{
    #     'class_signature': 'Lsh/kau/playground/quoter/QuotesRepoImpl;',
    #     'method_name': 'quoteForTheDay',
    #     'method_signature': '(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;',
    # }, callback=None)
    # bp.quoteForTheDay = quoteForTheDay
    # #await quoteForTheDay.set_breakpoint()

    # ------------------------------------------------------------------
    # Breakpoint-driven frida-gadget injection (technique 3: framework method).
    #
    # We can't just call system_loadlibrary() up front: ART's
    # ClassType.InvokeMethod requires the target thread to be suspended by a
    # JDWP *event* in that thread (its ready_for_debug_invoke flag). A thread
    # that's only suspended by our initial VirtualMachine.Suspend() is not
    # valid and the invoke returns INVALID_THREAD.
    #
    # Instead of breaking on an app-specific method, we break on a *framework*
    # method that exists in every Android app and runs on the main looper
    # thread: android.os.Handler.dispatchMessage. The main thread services its
    # message queue almost immediately after resume, so this fires early and on
    # the main thread without any per-app knowledge.
    #
    # BreakpointInfo uses suspendPolicy=ALL, so when the breakpoint fires the
    # hitting thread is suspended *by the event* and is therefore a legal
    # target for InvokeMethod. We do the loadLibrary from inside the callback,
    # using event.thread, then resume the VM.
    #
    # (For a variant that needs no location at all, see
    #  dbg.method_entry_loadlibrary(), which breaks on the next method the main
    #  thread enters via a METHOD_ENTRY event.)
    # ------------------------------------------------------------------
    async def load_gadget_on_break(event, composite, args):
        bp_info, = args

        # Fire once: stop this breakpoint from triggering again.
        await bp_info.dbg.disable_breakpoint_event(event.requestID)

        print(f"Breakpoint hit on thread {event.thread}; injecting frida-gadget...")

        # event.thread was suspended by this breakpoint event, so it satisfies
        # ART's ready_for_debug_invoke requirement.
        #
        # Why system_load_gadget() and not system_loadlibrary():
        #   System.loadLibrary("frida-gadget") resolves the name through the
        #   *calling* class's ClassLoader search path. Under JDWP InvokeMethod the
        #   caller is java.lang.System (boot ClassLoader), whose search path does
        #   NOT include the app's nativeLibraryDir -- so it fails with
        #   'library "libfrida-gadget.so" not found' even though the .so is in the
        #   APK. system_load_gadget() asks the app's own ClassLoader for the
        #   current absolute path (via findLibrary) and System.load()s it, so it
        #   works regardless of the volatile /data/app/~~<hash> path and survives
        #   uninstall/reinstall between test runs.
        #
        # NOTE: with the default gadget config (on_load: wait) this InvokeMethod
        # BLOCKS until a frida client releases the gadget -- expect the app to
        # freeze here. That freeze is success:
        #   1. adb forward tcp:27042 tcp:27042
        #   2. frida: device.attach("Gadget"); load script
        #   3. frida: device.resume("Gadget")
        # Only then does load() return and this await complete.
        await bp_info.dbg.system_load_gadget("frida-gadget", thread_id=event.thread)

        print('frida-gadget injection returned; resuming VM.')

        # Let the app proceed past the breakpoint / wait-for-debugger point.
        await bp_info.dbg.resume_vm()

    # **ClassType.InvokeMethod - System.loadLibrary("frida-gadget")
    loadGadget = dbg.create_breakpoint(**{
        'class_signature': 'Landroid/os/Handler;',
        'method_name': 'dispatchMessage',
        'method_signature': '(Landroid/os/Message;)V',
    }, callback=load_gadget_on_break)
    bp.loadGadget = loadGadget
    await loadGadget.set_breakpoint()

    # TODO: Control this from command line
    await asyncio.get_running_loop().run_in_executor(None, input, "Press Enter to resume VM...\n")

    # Resume so the app can run up to the breakpoint above, which triggers the
    # injection. Do NOT block on input here; the callback drives everything.
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


if __name__ == "__main__":
    asyncio.run(main_with_sandbox())





