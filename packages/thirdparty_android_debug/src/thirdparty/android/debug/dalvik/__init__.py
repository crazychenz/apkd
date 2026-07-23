'''
Copyright (c) 2025 Vincent Agriesti

This file is part of the thirdparty JDWP project.
Licensed under the MIT License. See the LICENSE file in the project root
for full license text.
'''

import asyncio
from thirdparty.jdwp import (
    Jdwp, Byte, Boolean, Int, String, ReferenceTypeID, Location, 
    Long, ClassID, ObjectID, FrameID, MethodID, Value, Tag)

from thirdparty.dalvik.dex import disassemble
from thirdparty.debug.dalvik.info.state import *
from thirdparty.debug.dalvik.info.breakpoint import BreakpointInfo
from thirdparty.debug.dalvik.info.thread import ThreadInfo
from thirdparty.debug.dalvik.info.object import ObjectInfo

import thirdparty.python.repl as __sandbox__
import typing

from pydantic import BaseModel
from typing import Optional, List, Tuple

import code

# Utility imports
import multiprocessing
import pdb
import threading
from fuzzyfinder import fuzzyfinder
from pprint import pprint


'''
    The TODO List:

    # Get list of ThreadInfo references
    await dbg.threads() -> List[ThreadInfo]

    # ThreadInfo - threadID, name?

    # Get number of stack frames (not cached).
    # Call this once and use "frames" as the local-only cache.
    # Store thread id in frameobject so you don't have to remember.
    frames = await dbg.frames(thread: ThreadInfo) -> FrameInfo

    # FrameInfo - threadID, frameID, location, values

    # Create ObjectInfo instance and gets fields and values.
    # Also has references to ClassInfo.MethodInfo for methods.

    objref = await dbg.deref(object_id) -> ObjectInfo

    # Used to show object fields and their values.
    # Note: If the value is an object, it'll be a 
    #       reference to another ObjectInfo
    await dbg.fields(obj: ObjectInfo)

    # ObjectInfo.getattr 
    await objref.field_one.field_two -> ObjectInfo

    # If we set an attribute, the types must match.
    # An object attribute can only be set to an ObjectInfo
    # Under the hood, its really being set to the objectID.
    # ObjectInfos should never be manually created. They are initialized
    #   by dbg.deref() and then subsequently filled out by getattr.
    # All ObjectInfo objects are referenced in a dict in dbg for
    # deduplication.

    # Used to list available methods.
    # Note: (Invoking isn't really a goal.)
    await dbg.methods(obj: ObjectInfo)
    # Consider: Call method by name plus sig as first param.
    # Example: objref.func("(L)V", objref)
'''


class Debugger():

    def __init__(self, state=None):
        if state:
            self.state = state
        else:
            # TODO: Does DebuggerState event exist?
            self.state = DebuggerState()

        self.jdwp = self.state.jdwp
        self.classes_by_id = self.state.classes_by_id
        self.classes_by_signature = self.state.classes_by_signature
        self.unloaded_classes = self.state.unloaded_classes
        self.threads_by_id = self.state.threads_by_id
        self.dead_threads = self.state.dead_threads
        self.objects_by_id = self.state.objects_by_id

        # TODO: Consider the event handlers. We won't automatically hot reload them.


    async def start(self, host, port):
        # TODO: unwind this with JdmDebuggerState
        if self.state.jdwp is None:
            self.state.jdwp = Jdwp(host, port)
            self.jdwp = self.state.jdwp
        await self.jdwp.start()

        # Always immediately suspend VM
        await self.jdwp.VirtualMachine.Suspend()

        # Always need idsizes and version information
        # TODO: Implement actually using these ... assuming always 64bit atm.
        self.idsizes, _ = await self.jdwp.VirtualMachine.IDSizes()
        self.versions, _ = await self.jdwp.VirtualMachine.Version()

        # Always cache all prepared and unloaded classes
        await self.enable_class_prepare_events()
        await self.enable_class_unload_events()

        # Always cache all started and killed threads
        await self.enable_thread_start_events()
        await self.enable_thread_death_events()

        # Always get all current classes and threads
        print("Fetching all classes. This make take a moment.")
        await self.request_all_classes()
        await self.request_all_threads()
        print("Done fetching classes.")


    def object_info(self, object_id):
        if object_id in self.objects_by_id:
            return self.objects_by_id[object_id]
        return ObjectInfo(self, object_id)


    async def deref(self, obj):
        """Given an object_id or ObjectInfo, returns a dereferenced
           version in the form of a loaded ObjectInfo instance.

          Args:
            obj (int): Object ID.
            obj (ObjectInfo): ObjectInfo instance.

          Returns: Loaded ObjectInfo()
        """
        if not isinstance(obj, ObjectInfo):
            obj = self.object_info(obj)
        return await obj.load()


    async def enable_class_prepare_events(self):
        # Watch for new classes.
        #print("EventRequest.Set(CLASS_PREPARE / NO_SUSPEND)")
        evt_req = self.jdwp.EventRequest.SetRequest()
        evt_req.eventKind = Byte(Jdwp.EventKind.CLASS_PREPARE)
        evt_req.suspendPolicy = Byte(Jdwp.SuspendPolicy.NONE)
        # No modifiers.
        self.class_prepare_reqid, error_code = await self.jdwp.EventRequest.Set(evt_req)
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to enable class prepare events: {Jdwp.Error.string[error_code]}")
            return
        #print(f"enable_class_prepare_events RequestID = {self.class_prepare_reqid}")

        self.jdwp.register_event_handler(self.class_prepare_reqid, Debugger.handle_class_prepare, self)


    async def enable_class_unload_events(self):
        # Watch for removed classes.
        #print("EventRequest.Set(CLASS_UNLOAD)")
        evt_req = self.jdwp.EventRequest.SetRequest()
        evt_req.eventKind = Byte(Jdwp.EventKind.CLASS_UNLOAD)
        evt_req.suspendPolicy = Byte(Jdwp.SuspendPolicy.NONE)
        # No modifiers.
        self.class_unload_reqid, error_code = await self.jdwp.EventRequest.Set(evt_req)
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to enable class unload events: {Jdwp.Error.string[error_code]}")
            return
        #print(f"enable_class_unload_events RequestID = {self.class_unload_reqid}")

        async def handle_class_unload(event, composite, wp):
            # TODO: Do we check if it already existed?
            
            if event.signature in self.classes_by_signature:
                classInfo = self.classes_by_signature[event.signature]
                self.classes_by_signature.pop(event.signature, None)
                self.classes_by_id.pop(classInfo.typeID, None)
                self.unloaded_classes.append(classInfo)
                # TODO: Implement way to show first A chars and last B chars in X width.
                print(f"CLASS_UNLOAD: {classInfo.signature[:60]}")

        self.jdwp.register_event_handler(self.class_unload_reqid, handle_class_unload)


    async def enable_thread_start_events(self):
        # Watch for removed classes.
        evt_req = self.jdwp.EventRequest.SetRequest()
        evt_req.eventKind = Byte(Jdwp.EventKind.THREAD_START)
        #evt_req.suspendPolicy = Byte(Jdwp.SuspendPolicy.ALL)
        evt_req.suspendPolicy = Byte(Jdwp.SuspendPolicy.NONE)
        # No modifiers.
        self.thread_start_reqid, error_code = await self.jdwp.EventRequest.Set(evt_req)
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to enable thread start events: {Jdwp.Error.string[error_code]}")
            return
        #print(f"enable_thread_start_events RequestID = {self.thread_start_reqid}")

        async def handle_thread_start(event, composite, wp):
            # TODO: Do we check if it already existed?
            threadInfo = ThreadInfo(self, event.thread)
            # TODO: Do we see if it already exists first?
            self.threads_by_id[threadInfo.threadID] = threadInfo
            #print(f"THREAD_START: {threadInfo.threadID}")

        self.jdwp.register_event_handler(self.thread_start_reqid, handle_thread_start)


    async def enable_thread_death_events(self):
        evt_req = self.jdwp.EventRequest.SetRequest()
        evt_req.eventKind = Byte(Jdwp.EventKind.THREAD_DEATH)
        evt_req.suspendPolicy = Byte(Jdwp.SuspendPolicy.NONE)
        self.thread_death_reqid, error_code = await self.jdwp.EventRequest.Set(evt_req)
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to enable thread death events: {Jdwp.Error.string[error_code]}")
            return
        #print(f"enable_thread_death_events RequestID = {self.thread_death_reqid}")

        async def handle_thread_death(event, composite, wp):

            # TODO: Do we check if it already existed?
            if event.thread in self.threads_by_id:
                threadInfo = self.threads_by_id[event.thread]
                self.threads_by_id.pop(threadInfo.threadID, None)
                self.dead_threads.append(threadInfo)
                # TODO: Implement way to show first A chars and last B chars in X width.
                #print(f"THREAD_DEATH: {threadInfo.threadID}")

        self.jdwp.register_event_handler(self.thread_death_reqid, handle_thread_death)


    async def disable_class_prepare_event(self, request_id):
        evt_req = self.jdwp.EventRequest.ClearRequest()
        evt_req.eventKind = Byte(Jdwp.EventKind.CLASS_PREPARE)
        evt_req.requestID = request_id
        await self.jdwp.EventRequest.Clear(evt_req)

    

    async def disable_breakpoint_event(self, request_id):
        evt_req = self.jdwp.EventRequest.ClearRequest()
        evt_req.eventKind = Byte(Jdwp.EventKind.BREAKPOINT)
        evt_req.requestID = request_id
        await self.jdwp.EventRequest.Clear(evt_req)

    async def disable_step_event(self, request_id):
        evt_req = self.jdwp.EventRequest.ClearRequest()
        evt_req.eventKind = Byte(Jdwp.EventKind.SINGLE_STEP)
        evt_req.requestID = request_id
        await self.jdwp.EventRequest.Clear(evt_req)

    async def disable_method_entry_event(self, request_id):
        evt_req = self.jdwp.EventRequest.ClearRequest()
        evt_req.eventKind = Byte(Jdwp.EventKind.METHOD_ENTRY)
        evt_req.requestID = request_id
        await self.jdwp.EventRequest.Clear(evt_req)


    


    async def load_method_bytecode(self, classID, methodID):

        if classID in self.classes_by_id:
            classInfo = self.classes_by_id[classID]
            if methodID in classInfo.methods_by_id:
                methodInfo = classInfo.methods_by_id[methodID]

                if not methodInfo.bytecode:
                    req = self.jdwp.Method.BytecodesRequest()
                    req.refType = ReferenceTypeID(classID)
                    req.methodID = methodID
                    reply, error_code = await self.jdwp.Method.Bytecodes(req)
                    if error_code != Jdwp.Error.NONE:
                        print(f"ERROR: Failed to fetch bytecode: {Jdwp.Error.string[error_code]}")
                        return
                    methodInfo.bytecode = reply.bytecodes
        
                return methodInfo.bytecode

        return None


    


    def create_breakpoint(self, **kwargs):
        """Create object to manage immediate and deferred breakpoint.

        Args:
            class_signature (str): JVM/JNI Class Signature
            method_name (str): Name of method to break within.
            method_signature (str): JVM/JNI of specific method to break within.
            callback: Awaited async callback on breakpoint event.
                      `async def callback(event, composite, args) -> None`
            bytecode_index (int): 16bit aligned offset into method to break at.
            count (int): Number of times to pass breakpoint without breaking.

        Returns:
            BreakpointInfo: Breakpoint Object. Run `await obj.set_breakpoint()` to activate!
        """

        if 'class_signature' not in kwargs or \
           'method_name' not in kwargs or \
           'method_signature' not in kwargs or \
           not kwargs['class_signature'] or \
           not kwargs['method_name'] or \
           not kwargs['method_signature']:
            raise RuntimeError("Must have class_signature, method_name, and method_signature set for breakpoint.")

        return BreakpointInfo(self, **kwargs)


    @staticmethod
    async def handle_class_prepare(event, composite, dbg):
        """Callback for Debugger.enable_class_prepare_events()"""
        if event.typeID not in dbg.classes_by_id:

            # Unloaded until we think we'll deref.
            # TODO: Consider registering for generic event too.
            classInfo = dbg.create_class_info(\
                event.typeID,
                typeTag=event.refTypeTag,
                signature=event.signature)
            dbg.classes_by_id[event.typeID] = classInfo

            # classInfo = ClassInfo()
            # classInfo.refTypeTag = event.refTypeTag
            # classInfo.typeID = event.typeID
            # classInfo.signature = event.signature
            # #classInfo.generic = # TODO: Is there an event with class prepare with generic?
            # # TODO: Do we see if it already exists first?
            # dbg.classes_by_id[classInfo.typeID] = classInfo
            dbg.classes_by_signature[classInfo.signature] = classInfo
            # # TODO: Implement way to show first A chars and last B chars in X width.
            # #print(f"CLASS_PREPARE: {classInfo.signature[:60]}")


    async def request_all_classes(self):
        #print("VirtualMachine.AllClassesWithGeneric()")
        all_classes_reply, error_code = await self.jdwp.VirtualMachine.AllClassesWithGeneric()
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to fetch all classes: {Jdwp.Error.string[error_code]}")
            return

        #db['all_classes_reply1'] = all_classes_reply
        #i = 0
        for clazz in all_classes_reply.classes:

            # Unloaded until we think we'll deref.
            classInfo = self.create_class_info(\
                clazz.typeID,
                typeTag=clazz.refTypeTag,
                signature=clazz.signature,
                generic=clazz.genericString)

            self.classes_by_id[clazz.typeID] = classInfo

            # classInfo = ClassInfo()
            # classInfo.refTypeTag = clazz.refTypeTag
            # classInfo.typeID = clazz.typeID
            # classInfo.signature = clazz.signature
            # classInfo.generic = clazz.genericString
            # # TODO: Do we see if it already exists first?
            # self.classes_by_id[classInfo.typeID] = classInfo
            self.classes_by_signature[classInfo.signature] = classInfo
        

    async def get_class_id(self, object_id):
        # Get the object type
        reftype_reply, error_code = await self.jdwp.ObjectReference.ReferenceType(ObjectID(object_id))
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to get object type: {Jdwp.Error.string[error_code]}")
            return None

        return reftype_reply.typeID


    async def get_super_id(self, class_id):
        # Is there a super class?
        super_class_id, error_code = await self.jdwp.ClassType.Superclass(ClassID(class_id))
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to get superclass: {Jdwp.Error.string[error_code]}")
            return None
        return super_class_id

    # =====================================================================
    # =====================================================================
    # =====================================================================
    # =====================================================================
    # =====================================================================
    # =====================================================================
    # =====================================================================
    # =====================================================================
    # =====================================================================
    # =====================================================================

    """
    ClassID() of System
    ThreadID() of main
    MethodID() of loadLibrary
    arguments List of ["frida-gadget"]

    clazz: Optional[ClassID] = None
        thread: Optional[ThreadID] = None
        methodID: Optional[MethodID] = None
        arguments: List[Value] = []
        options: Optional[int] = None
    """


    async def _resolve_invoke_thread(self, thread_id):
        """Return a ThreadID usable for ClassType.InvokeMethod, or None.

        ART requires the target thread to be suspended *by an event that fired
        in that thread* (its ready_for_debug_invoke flag). A thread that merely
        has a positive suspend count from a VM-wide suspend is NOT valid and
        yields INVALID_THREAD. When a caller (e.g. a breakpoint callback)
        already has such a thread, pass it in as thread_id and it is used as-is.
        Otherwise we fall back to scanning for 'main' with suspend count > 0,
        which only works if 'main' was itself stopped by an event.
        """
        if thread_id is not None:
            return thread_id

        for tid in self.threads_by_id:
            name, error_code = await self.jdwp.ThreadReference.Name(tid)
            if error_code != Jdwp.Error.NONE:
                print(f"ERROR: Failed to get thread name for {tid}: {Jdwp.Error.string[error_code]}")
                continue
            suscount, error_code = await self.jdwp.ThreadReference.SuspendCount(tid)
            if error_code != Jdwp.Error.NONE:
                print(f"ERROR: Failed to get thread suspend count for {tid}: {Jdwp.Error.string[error_code]}")
                continue
            if name == "main" and suscount > 0:
                return tid

        print("Failed to find \"main\" thread id.")
        return None


    async def _invoke_system_string_method(self, method_name, method_sig, arg, thread_id=None):
        """Invoke a static java.lang.System method taking a single String arg.

        Shared by system_loadlibrary() and system_load(). Resolves the System
        class + method, creates the String argument, invokes on an
        event-suspended thread (options=INVOKE_SINGLE_THREADED), and -- crucially
        -- inspects reply.exception. A clean JDWP transport does NOT mean the
        Java method succeeded; a thrown exception (e.g. UnsatisfiedLinkError)
        comes back in reply.exception (objectID 0 == none), not as a JDWP error.

        Returns True on success, False if the thread couldn't be resolved, the
        invoke failed at the JDWP level, or the method threw.
        """
        # Get the class id from the debugger's initial scan.
        system_class_info = self.classes_by_signature['Ljava/lang/System;']
        await system_class_info.load()
        method_info = system_class_info.methods_by_signature[(method_name, method_sig)]

        main_thread_id = await self._resolve_invoke_thread(thread_id)
        if main_thread_id is None:
            return False

        # Create string
        string_id, error_code = await self.jdwp.VirtualMachine.CreateString(arg)
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to create string: {Jdwp.Error.string[error_code]}")
            return False

        # Prepare ClassType.InvokeMethod
        req = self.jdwp.ClassType.InvokeMethodRequest()
        req.clazz = ClassID(system_class_info.typeID)
        req.thread = ThreadID(main_thread_id)
        req.methodID = MethodID(method_info.methodID)
        str_val = Value()
        str_val.tag = Byte(Tag.STRING)
        str_val.value = Long(string_id)
        req.arguments = [str_val]
        # options bit 1 = INVOKE_SINGLE_THREADED: only the target thread runs
        # during the invoke; other threads stay suspended.
        req.options = Int(1)

        print(f"Using thread {main_thread_id} class {system_class_info.typeID} "
              f"method {method_info.methodID} ({method_name}) string {string_id}")

        reply, error_code = await self.jdwp.ClassType.InvokeMethod(req)
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to invoke System.{method_name}: {Jdwp.Error.string[error_code]}")
            return False

        # Check for a thrown exception (see docstring). objectID 0 == no exception.
        if reply.exception is not None and reply.exception.objectID:
            exc_id = reply.exception.objectID
            exc_class = await self.get_object_class_info(exc_id)
            exc_name = exc_class.signature if exc_class is not None else f"object {exc_id}"
            exc_msg = await self.exception_message(exc_id, main_thread_id)
            detail = f': {exc_msg}' if exc_msg else ''
            print(f'ERROR: System.{method_name}("{arg}") threw {exc_name}{detail} '
                  f'-- the library was NOT loaded.')
            return False

        print(f'Ran System.{method_name}("{arg}")')
        return True


    async def system_loadlibrary(self, libname:str="frida-gadget", thread_id=None):
        """Load a library by short name via System.loadLibrary(libname).

        Only finds libraries on the app's native library search path (its
        nativeLibraryDir). For a .so at an arbitrary path use system_load().

        NOTE: whether this blocks until a frida client connects depends on the
        gadget's config. frida-gadget's default `on_load` is `resume`, so the
        call returns immediately after the listener starts; set `on_load: wait`
        in the gadget config to make it block until you attach + resume().
        """
        return await self._invoke_system_string_method(
            "loadLibrary", "(Ljava/lang/String;)V", libname, thread_id=thread_id)


    async def system_load(self, path:str, thread_id=None):
        """Load a library by absolute path via System.load(path).

        Use this when the .so is not on the app's native library search path --
        e.g. a frida-gadget pushed to /data/local/tmp. The app process must be
        able to read/dlopen that path (SELinux/permissions permitting).
        """
        return await self._invoke_system_string_method(
            "load", "(Ljava/lang/String;)V", path, thread_id=thread_id)


    async def _invoke_virtual(self, object_id, thread_id, method_name, method_sig, arguments):
        """Invoke an instance method on object_id via ObjectReference.InvokeMethod.

        Resolves the methodID by walking object_id's runtime class hierarchy for
        (method_name, method_sig), so inherited/overridden methods work. arguments
        is a list of Value. thread_id must be an event-suspended
        (ready_for_debug_invoke) thread. Returns the InvokeMethodReply, or None.
        """
        obj_class = await self.get_object_class_info(object_id)
        if obj_class is None:
            return None
        await obj_class.load()

        key = (method_name, method_sig)
        decl_class = obj_class
        while decl_class is not None and key not in decl_class.methods_by_signature:
            decl_class = decl_class.super_class
        if decl_class is None:
            print(f"ERROR: method {key} not found on {obj_class.signature}")
            return None
        method_info = decl_class.methods_by_signature[key]

        req = self.jdwp.ObjectReference.InvokeMethodRequest()
        req.objectid = ObjectID(object_id)
        req.thread = ThreadID(thread_id)
        req.clazz = ClassID(decl_class.typeID)
        req.methodID = MethodID(method_info.methodID)
        req.arguments = arguments
        req.options = Int(1)   # INVOKE_SINGLE_THREADED

        reply, error_code = await self.jdwp.ObjectReference.InvokeMethod(req)
        if error_code != Jdwp.Error.NONE or reply is None:
            print(f"ERROR: invoke {method_name} failed: {Jdwp.Error.string[error_code]}")
            return None
        return reply


    async def resolve_app_library_path(self, libname, thread_id):
        """Ask the app's ClassLoader for the absolute path of libname.

        Uses the invoke thread's *context* ClassLoader -- on Android the main
        thread's context ClassLoader is the app's ClassLoader -- and calls
        ClassLoader.findLibrary(libname), which returns the full path to the .so
        inside the app's current native library dir (or null). This is robust
        across reinstalls because it queries the live app instead of assuming a
        path with volatile /data/app/~~<hash> segments.

        thread_id must be event-suspended. Returns the absolute path, or None.
        """
        # Thread object == thread_id in JDWP; getContextClassLoader() -> ClassLoader.
        reply = await self._invoke_virtual(
            thread_id, thread_id,
            'getContextClassLoader', '()Ljava/lang/ClassLoader;', [])
        if reply is None or (reply.exception is not None and reply.exception.objectID) \
           or reply.returnValue is None or not reply.returnValue.value:
            print("ERROR: could not get the thread's context ClassLoader "
                  "(app may not be initialized yet -- break slightly later).")
            return None
        classloader_id = reply.returnValue.value

        # findLibrary(String) -> absolute path (or null). Build the String arg.
        name_id, error_code = await self.jdwp.VirtualMachine.CreateString(libname)
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to create string: {Jdwp.Error.string[error_code]}")
            return None
        name_val = Value()
        name_val.tag = Byte(Tag.STRING)
        name_val.value = Long(name_id)

        reply = await self._invoke_virtual(
            classloader_id, thread_id,
            'findLibrary', '(Ljava/lang/String;)Ljava/lang/String;', [name_val])
        if reply is None or (reply.exception is not None and reply.exception.objectID) \
           or reply.returnValue is None or not reply.returnValue.value:
            print(f'ERROR: ClassLoader.findLibrary("{libname}") returned null '
                  f'(is lib{libname}.so packaged in the APK for this ABI?).')
            return None

        path, error_code = await self.jdwp.StringReference.Value(reply.returnValue.value)
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to read library path string: {Jdwp.Error.string[error_code]}")
            return None
        return path


    async def system_load_gadget(self, libname:str="frida-gadget", thread_id=None):
        """Resolve libname via the app's ClassLoader, then System.load() the path.

        Install-independent replacement for hardcoding an absolute /data/app path
        (which changes on every reinstall). Resolves the current path with
        resolve_app_library_path() and hands it to system_load().
        """
        thread_id = await self._resolve_invoke_thread(thread_id)
        if thread_id is None:
            return False

        path = await self.resolve_app_library_path(libname, thread_id)
        if not path:
            print(f"ERROR: could not resolve a path for {libname} via the app ClassLoader.")
            return False

        print(f'Resolved "{libname}" -> {path}')
        return await self.system_load(path, thread_id=thread_id)


    async def find_thread_by_name(self, target_name):
        """Return the ThreadID of the first live thread named target_name, or None."""
        for tid in self.threads_by_id:
            name, error_code = await self.jdwp.ThreadReference.Name(tid)
            if error_code != Jdwp.Error.NONE:
                print(f"ERROR: Failed to get thread name for {tid}: {Jdwp.Error.string[error_code]}")
                continue
            if name == target_name:
                return tid
        return None


    async def method_entry_loadlibrary(self, libname:str="frida-gadget", thread_id=None, class_pattern=None):
        """Inject via System.loadLibrary on the next method a thread enters.

        This is an alternative to setting a location breakpoint on a known
        method. It arms a METHOD_ENTRY event so the injection lands on the next
        method entered after the VM resumes -- no prior knowledge of any
        specific method in the target app is required.

        When the event fires, the hitting thread is suspended *by the event*,
        which satisfies ART's ready_for_debug_invoke requirement for
        ClassType.InvokeMethod. We then run System.loadLibrary(libname) on that
        thread and resume the VM.

        Call this while the VM is suspended (e.g. at wait-for-debugger), then
        call resume_vm() so the event can fire. This does NOT resume for you.

        Args:
            libname (str): Library name passed to System.loadLibrary.
            thread_id: Restrict the event to this thread. Defaults to the thread
                named "main". Pass 0 (or any falsy non-None value) to match any
                thread -- note METHOD_ENTRY is a VM-wide firehose without a
                thread or class filter.
            class_pattern (str): Optional dotted class-name glob (e.g.
                "sh.kau.playground.*") to further restrict which method entries
                qualify, matching JDWP ClassMatch semantics.

        Returns:
            The METHOD_ENTRY request id, or None on failure.
        """

        # Default to the main thread unless the caller explicitly opts out.
        if thread_id is None:
            thread_id = await self.find_thread_by_name("main")
            if thread_id is None:
                print('ERROR: Could not find "main" thread for method-entry injection.')
                return None

        evt_req = self.jdwp.EventRequest.SetRequest()
        evt_req.eventKind = Byte(Jdwp.EventKind.METHOD_ENTRY)
        # ALL so every thread halts while we invoke; the thread that hit the
        # event is the one that becomes ready_for_debug_invoke.
        evt_req.suspendPolicy = Byte(Jdwp.SuspendPolicy.ALL)

        # Fire only once.
        mod = self.jdwp.EventRequest.SetCountModifier()
        mod.count = Int(1)
        evt_req.modifiers.append(mod)

        # Restrict to a single thread (the main thread by default). Without this
        # (or a class filter) METHOD_ENTRY fires on every method entry VM-wide.
        if thread_id:
            mod = self.jdwp.EventRequest.SetThreadOnlyModifier()
            mod.thread = ThreadID(thread_id)
            evt_req.modifiers.append(mod)

        # Optionally narrow to a package/class glob.
        if class_pattern:
            mod = self.jdwp.EventRequest.SetClassMatchModifier()
            mod.classPattern = String(class_pattern)
            evt_req.modifiers.append(mod)

        reqid, error_code = await self.jdwp.EventRequest.Set(evt_req)
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to set method-entry event: {Jdwp.Error.string[error_code]}")
            return None

        async def handle_method_entry(event, composite, args):
            # Fire once: clear the event so subsequent entries don't re-trigger.
            await self.disable_method_entry_event(event.requestID)
            print(f"METHOD_ENTRY on thread {event.thread}; injecting {libname}...")
            # event.thread was suspended by this event -> ready_for_debug_invoke.
            await self.system_loadlibrary(libname, thread_id=event.thread)
            print(f'System.loadLibrary("{libname}") returned; resuming VM.')
            await self.resume_vm()

        self.jdwp.register_event_handler(reqid, handle_method_entry)
        print(f"Armed METHOD_ENTRY injection (reqid {reqid}); resume VM to trigger.")
        return reqid




    def create_class_info(self, typeID, typeTag=None, signature=None, generic=None):
        if typeID in self.classes_by_id:
            return

        class_info = ClassInfo(self, typeID)

        if typeTag:
            class_info.refTypeTag = typeTag

        if signature:
            class_info.signature = signature

        if generic:
            class_info.generic = generic

        return class_info


    async def class_info(self, clazz):
        clazz_orig = clazz
        if isinstance(clazz, int):
            clazz = self.classes_by_id[clazz]
        return await clazz.load()

    
    async def string(self, object_id):
        value, error_code = await self.jdwp.StringReference.IsCollected(ObjectID(object_id))
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to get string value: {Jdwp.Error.string[error_code]}")
            return None
        return value


    async def request_all_threads(self):
        thread_reply, error_code = await self.jdwp.VirtualMachine.AllThreads()
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to get all threads: {Jdwp.Error.string[error_code]}")
            return
        for thread_id in thread_reply.threads:
            # Caches itself in constructor.
            # Note: We don't load threads until we break.
            ThreadInfo(self, thread_id)


    async def resume_vm(self):
        """Resume VM"""
        await self.jdwp.VirtualMachine.Resume()


    def print_summary(self):
        print("")
        print("-- VM Info --")  
        print(f"Description: {self.versions.description}")
        print(f"JDWP Version: {self.versions.jdwpMajor}.{self.versions.jdwpMinor}")
        print(f"VM Version: {self.versions.vmVersion}")
        print(f"VM Name: {self.versions.vmName}")
        print("")
        print("-- Cache Info --")
        print(f"Class Count: {len(self.classes_by_id)}")
        print(f"Thread Count: {len(self.classes_by_id)}")


    async def thread(self, thread):
        # Only call when suspended.
        #print(f"Debugger.thread({thread})")
        if not isinstance(thread, ThreadInfo):
            # if thread == 21753:
            #     print("BREAKPOINT in DEBBUGGER.THREAD()")
            #     breakpoint()
            try:
                thread = self.threads_by_id[thread]
            except KeyError:
                thread = ThreadInfo(self, thread)

        if thread == 21753:
            print(f"Debugger.thread() thread {thread}")
        return await thread.load()


    async def frame(self, thread, frame=0):
        # Only call when broke.
        # thread can be ID or ThreadInfo
        if not isinstance(thread, ThreadInfo):
            thread = await self.thread(thread)
        return await thread.frame(frame)


    # Note: async def slot() is not useful at the moment.

    async def get_object_class_info(self, object_id):
        # Get the object type
        reftype_reply, error_code = await self.jdwp.ObjectReference.ReferenceType(ObjectID(object_id))
        if error_code != Jdwp.Error.NONE:
            print(f"ERROR: Failed to get object type: {Jdwp.Error.string[error_code]}")
            return

        # Get the class_info
        if reftype_reply.typeID not in self.classes_by_id:
            print(f"ERROR: Class id not found: {reftype_reply.typeID}")
            return

        return self.classes_by_id[reftype_reply.typeID]


    async def exception_message(self, exc_object_id, thread_id):
        """Best-effort fetch of Throwable.getMessage() for an exception object.

        thread_id must be an event-suspended (ready_for_debug_invoke) thread --
        e.g. the same thread the failed invoke ran on, which is still suspended
        because we have not resumed yet. Returns the message string, or None if
        it can't be retrieved (no getMessage found, null message, or the nested
        invoke failed). This is what turns a bare exception class into an
        actionable reason, e.g. 'dlopen failed: "..." is 32-bit instead of
        64-bit' or 'has text relocations'.
        """
        exc_class = await self.get_object_class_info(exc_object_id)
        if exc_class is None:
            return None
        await exc_class.load()

        # getMessage is declared on java.lang.Throwable; walk up to find it.
        getmsg_key = ('getMessage', '()Ljava/lang/String;')
        decl_class = exc_class
        while decl_class is not None and getmsg_key not in decl_class.methods_by_signature:
            decl_class = decl_class.super_class
        if decl_class is None:
            return None
        method_info = decl_class.methods_by_signature[getmsg_key]

        req = self.jdwp.ObjectReference.InvokeMethodRequest()
        req.objectid = ObjectID(exc_object_id)
        req.thread = ThreadID(thread_id)
        req.clazz = ClassID(decl_class.typeID)
        req.methodID = MethodID(method_info.methodID)
        req.arguments = []
        req.options = Int(1)   # INVOKE_SINGLE_THREADED

        reply, error_code = await self.jdwp.ObjectReference.InvokeMethod(req)
        if error_code != Jdwp.Error.NONE or reply is None:
            return None
        # getMessage itself threw, or returned a null message.
        if reply.exception is not None and reply.exception.objectID:
            return None
        if reply.returnValue is None or not reply.returnValue.value:
            return None
        msg, error_code = await self.jdwp.StringReference.Value(reply.returnValue.value)
        if error_code != Jdwp.Error.NONE:
            return None
        return msg
    
