The fix
The reason the direct system_loadlibrary() call was returning INVALID_THREAD is what we established earlier: ART's ClassType.InvokeMethod rejects any thread that isn't suspended by an event in that thread (ready_for_debug_invoke). The old code scanned AllThreads for main with a positive suspend count, but that count came from the startup VirtualMachine.Suspend(), so the invoke was always illegal.

src/thirdparty/debug/dalvik/init.py — system_loadlibrary now takes an optional thread_id. When provided, it uses that thread directly and skips the scan; the fallback scan is preserved but documented as unreliable. This lets a breakpoint callback pass the thread that was actually stopped by the event.

entry_new.py — added a third breakpoint example that drives the injection correctly:

load_gadget_on_break(event, composite, args) — disables the breakpoint (fire once), then calls system_loadlibrary("frida-gadget", thread_id=event.thread), then resume_vm(). event.thread is the thread the breakpoint suspended, so it satisfies ready_for_debug_invoke.
A loadGadget breakpoint on fetchQuote, activated with that callback. BreakpointInfo sets suspendPolicy=ALL, so the hitting thread is suspended by the event.
The startup path now just calls resume_vm() to let the app run up to the breakpoint — the callback drives everything from there (no more blocking input() prompt).
I also commented out the pre-existing await fetchQuote.set_breakpoint() activation, since the injection breakpoint now handles the same method and two active breakpoints at one location would race on resume_vm.

One thing to be aware of
Because system_loadlibrary uses options=INVOKE_SINGLE_THREADED (1), the InvokeMethod await inside the callback will not return until a frida client releases the gadget — adb forward tcp:27042, then device.attach("Gadget"), then device.resume("Gadget"). Only then does loadLibrary() return and the callback proceed to resume_vm(). That matches the sequence in the module docstring. Also, fetchQuote needs to actually execute for the breakpoint to fire; if it runs on a coroutine/background thread rather than main, that's fine for the invoke (any event-suspended thread works), but make sure it's a method the app reaches before the point you care about.



Great question — and the error message you got is actually the proof of the answer. The short version: it's not that the library path "isn't loaded yet." It's that System.loadLibrary searched a different library path than the one the gadget lives on, because which path it searches is decided by which ClassLoader it's handed — and over JDWP it gets the wrong one.

What loadLibrary actually does internally
System.loadLibrary(name) doesn't have a fixed search path. It delegates to Runtime.loadLibrary0(loader, name), and that method branches on the ClassLoader (this is Android 13's libcore, paraphrased):


void loadLibrary0(ClassLoader loader, Class<?> caller, String libname) {
    if (loader != null && !(loader instanceof BootClassLoader)) {
        // --- app ClassLoader branch ---
        String filename = loader.findLibrary(libname);          // <-- THIS
        if (filename == null)
            throw new UnsatisfiedLinkError(loader + " couldn't find \"" +
                                           System.mapLibraryName(libname) + "\"");
        nativeLoad(filename, loader);   // load by absolute path
        return;
    }
    // --- boot/null ClassLoader branch ---
    String filename = System.mapLibraryName(libname);           // "libfrida-gadget.so"
    nativeLoad(filename, loader);       // linker searches DEFAULT namespace paths
}
Look at the first branch: loader.findLibrary(libname) is exactly what resolve_app_library_path calls. When loadLibrary has a real app ClassLoader, it internally does the same thing you're doing manually. findLibrary on a PathClassLoader/BaseDexClassLoader walks that loader's nativeLibraryDirectories (its DexPathList), which includes the app's nativeLibraryDir — /data/app/~~…/lib/x86_64 — and returns the absolute path. So resolve_app_library_path isn't doing anything exotic; it's reaching the app-ClassLoader code path that loadLibrary would have taken if it had the app's loader.

Why the JDWP call takes the wrong branch
loadLibrary gets its ClassLoader from the caller (VMStack.getCallingClassLoader() / the caller class). In a normal in-app call, the caller is one of the app's classes → app ClassLoader → first branch → found.

Your invoke is different in two reinforcing ways:

It's a synthetic ClassType.InvokeMethod with no real Java caller frame, and
you're suspended inside android.os.Handler.dispatchMessage — Handler is a framework class loaded by the boot ClassLoader.
Either way, the calling ClassLoader resolves to the boot ClassLoader, so loadLibrary0 takes the second branch. That branch ignores any app path and just asks the linker to dlopen("libfrida-gadget.so") against the default namespace's default search dirs (the system libraries — the java.library.path world: /system/lib64, /vendor/lib64, …). The gadget isn't there, so the linker reports:


dlopen failed: library "libfrida-gadget.so" not found
That exact wording is the tell. The app-ClassLoader branch would have thrown a Java-generated UnsatisfiedLinkError: <loader> couldn't find "libfrida-gadget.so". You got the linker's "dlopen failed … not found" instead — which only comes from the boot/null-loader branch. So the message itself confirms loadLibrary was handed the boot ClassLoader and searched the system dirs.

Answering your specific question
Is the java library path not loaded at the breakpoint?

No — it's loaded and fully available. loadLibrary genuinely did search a valid library path; it just searched the boot ClassLoader's path (system dirs), not the app ClassLoader's path (the app's nativeLibraryDir). There are two different native-library search lists in play:

boot/system: the java.library.path system dirs — what the failed loadLibrary consulted.
app: nativeLibraryDirectories inside the app ClassLoader's DexPathList — where libfrida-gadget.so actually is, and what findLibrary consults.
Nothing was missing or unloaded. It was purely a "which ClassLoader, therefore which search path" mismatch. resolve_app_library_path fixes it by explicitly grabbing the app's ClassLoader (off the thread's context ClassLoader) and calling the very same findLibrary that loadLibrary uses internally — then System.load() takes the resulting absolute path, bypassing ClassLoader resolution altogether.

One corollary worth knowing: you could have made loadLibrary itself work by handing it the app loader directly — e.g. invoking Runtime.loadLibrary0(appClassLoader, …) — but that method's signature has churned across Android versions, whereas findLibrary + System.load uses stable APIs and doesn't care where you broke.

libfrida-gadget.config.so.json:

```json
{
  "interaction": {
    "type": "listen",
    "address": "127.0.0.1",
    "port": 27043
  }
}
```
