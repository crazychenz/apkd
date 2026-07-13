
# Upstream or not

## APKTool

A lot of the foundational teardown of apkd is reinventing the same thing that apktool does. In my bigger vision, we're quite literally redoing from end to end what apktool can provide. There are several issues with depending on apktool...

- It doesn't always work. A simple no-op extract and build has failed in more than half of my cases. One possible workaround for the issue is not to extract resource or dex (or possibly other aspects of the apk).

- It has its own metadata and file layout. For reasons, it makes sense to work on an extracted APK from a file system and not purely from memory. To do this intelligently, you want to have a managed folder hierarchy whereby one of them is the apk's folder hierarchy. I don't know if the apktool folder structure is stable. In the event I integrate apktool, I would need to normalize its output folder structure into my own and then be able to reverse any of those actions for the build process. (Maybe worth it for rebuilding resources and dex?)

- Requires yet another dependency from another ecosystem. I accept that I'll likely need full java JRE and Android SDK to accomplish the goals I have for apkd, but apktool and baksmali are external to python, Oracle's Java, and Google's Android SDK. I shouldn't require either of them to accomplish the majority of apkd's goals (IMHO). ... that said, I'm not confident yet how I plan to avoid using baksmali jar (but I have ideas).

## Androguard

An absolutely amazing tool that apkd leans heavily on. Androguard comes with its own CLI tools that are mostly identical to apkd sub commands. Why? ... consistency. When running through specific apkd use cases, we want to use a consistent interface that covers a wide range of tools. I'd consider using androguard CLI directly in a "how to do analysis" article, but in the case of apkd usage, we want to stay as much in the apkd ecosystem as we can. (We'll already be required to do a lot of manual things to the target under test as it stands.)



## Plan

apkd will:

- extract apk (i.e. unzip)
- decode/encode AndroidManifest.xml (pxaml)
- manage keys (via keytool)
- package apk (i.e. zip, zipalign, sign)


## Patching APK with upstream

With objection:

```sh
pip install objection
objection patchapk -s target.apk
```

With apktool:

```sh
# 1. Decompile
apktool d target.apk -o target_out

# 2. Find the main activity's smali file and add the gadget load:
#    const-string v0, "frida-gadget"
#    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
#    — inserted into <clinit> if it exists, else a new static constructor

# 3. Drop the gadget .so into the right ABI folder
mkdir -p target_out/lib/arm64-v8a
cp libfrida-gadget.so target_out/lib/arm64-v8a/

# 4. Rebuild, align, sign
apktool b target_out -o target_patched.apk
zipalign -v 4 target_patched.apk target_aligned.apk
apksigner sign --ks my.keystore target_aligned.apk
```

As `.so` dependency with lief (Library to Instrument Executable Formats):

```python
import lief
lib = lief.parse("target_out/lib/arm64-v8a/libsomething.so")
lib.add_library("libfrida-gadget.so")
lib.write("target_out/lib/arm64-v8a/libsomething.so")
```

Note: This is more of a work around for situations where we can't modify smali.

## Resources

- androguard - does not assemble or build, only read and analysis
- apk-parser - does not include dex analysis engine
- `objection patchapk`

```sh
# disassemble
java -jar smali-baksmali-fat.jar disassemble classes.dex -o smali_out/

# ...edit files under smali_out/...

# reassemble
java -jar smali-fat.jar assemble smali_out/ -o classes_new.dex
```

