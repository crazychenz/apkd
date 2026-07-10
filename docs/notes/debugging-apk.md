Install android tools

```
export ANDROID_HOME=$(realpath ~)/.android/
export PATH=${ANDROID_HOME}cmdline-tools/latest/bin:$PATH
export PATH=${ANDROID_HOME}platform-tools:$PATH
export PATH=${ANDROID_HOME}cmdline-tools/latest/bin:$PATH
export PATH=${ANDROID_HOME}emulator:$PATH
export PATH=${ANDROID_HOME}build-tools/34.0.0:$PATH
```

Create Android Emulator:

```
avdmanager create avd -n android14 -k "system-images;android-34;default;x86_64"
```

Run Android Emulator:

```
emulator -avd android14 -no-snapshot -writable-system \
  -show-kernel -verbose -no-audio -no-window
```

Unlock emulator:

```
adb root
adb disable-verity
adb reboot
adb root
adb remount
```

Install JDK _17_.

Get some projects to inspect:

```
git clone https://github.com/kaushikgopal/playground-android.git
git clone https://github.com/cortinico/kotlin-android-template.git
```

Download template, run gradlew (make all or gradlew assembleRelease).

Using _release_ APK, inject android:debuggable="true" into Manifest to enable debugging:

```
#!/bin/bash

# Tools
# https://github.com/baksmali/smali/releases/download/3.0.9/baksmali-3.0.9-fat.jar
# https://github.com/iBotPeaches/Apktool/releases/download/v2.12.0/apktool_2.12.0.jar

# References
# https://source.android.com/devices/tech/dalvik/dalvik-bytecode.html
# https://github.com/JesusFreke/smali/wiki/Registers
# https://github.com/JesusFreke/smali/wiki/TypesMethodsAndFields
# https://source.android.com/devices/tech/dalvik/dex-format.html


if [ ! -e "keys" ]; then
  echo "Making keystore and signing key."
  mkdir keys \
  && keytool -genkey -v -keystore keys/my-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
fi

APKDPATH=./outputs/app-release-unsigned

if [ ! -e "./outputs/rebuild-aligned.apk" ]; then
    echo "Using apktool to extract apk."
    mkdir -p ./outputs
    java -jar apktool_2.12.0.jar d -o ${APKDPATH} ./app-release-unsigned.apk

    echo "Injecting android:debuggable into AndroidManifest.xml"
    sed -i 's/<application/<application android:debuggable="true" /' ${APKDPATH}/AndroidManifest.xml
    touch ./outputs/debug_injection_complete

    echo "Rebuilding, aligning, and signing apk."
    java -jar apktool_2.12.0.jar b -o ./outputs/rebuild-unaligned.apk ${APKDPATH} \
    && zipalign 4 ./outputs/rebuild-unaligned.apk ./outputs/rebuild-aligned.apk \
    && apksigner sign --ks ./keys/my-release-key.jks --ks-key-alias my-key-alias \
        --ks-pass pass:gofish --key-pass pass:gofish --out ./outputs/rebuild-signed.apk \
        ./outputs/rebuild-aligned.apk
fi

if [ ! -e "outputs/rebuild-aligned_min.apk" ]; then
  if [ ! -z "$(which pyaxml 2>/dev/null)" ]; then
    mkdir -p outputs

    echo "Min: Extracting apk with apktool (without resources or source)."
    java -jar apktool_2.12.0.jar d --no-res --no-src -o ${APKDPATH}_min ./app-release-unsigned.apk

    echo "Min: Decoding axml AndroidManifest"
    cp ${APKDPATH}_min/AndroidManifest.xml outputs/AndroidManifest.original.axml
    pyaxml -i outputs/AndroidManifest.original.axml -o outputs/AndroidManifest.xml axml2xml

    echo "Min: Injecting debuggable."
    sed -i 's/<application/<application android:debuggable="true" /' outputs/AndroidManifest.xml

    echo "Min: Serializing AndroidManifest xml to axml."
    pyaxml -i outputs/AndroidManifest.xml -o ${APKDPATH}_min/AndroidManifest.xml xml2axml

    echo "Min: Rebuilding, aligning, and signing."
    java -jar apktool_2.12.0.jar b -o ./outputs/rebuild-unaligned_min.apk ${APKDPATH}_min \
    && zipalign 4 ./outputs/rebuild-unaligned_min.apk ./outputs/rebuild-aligned_min.apk \
    && apksigner sign --ks ./keys/my-release-key.jks --ks-key-alias my-key-alias \
        --ks-pass pass:gofish --key-pass pass:gofish --out ./outputs/rebuild-signed_min.apk \
        ./outputs/rebuild-aligned_min.apk
  fi
fi

if [ ! -e "./outputs/smali" ]; then
  echo "Extracting smali with byte code offsets."
  mkdir -p ./outputs/smali
  java -jar baksmali-3.0.9-fat.jar d --code-offsets ${APKDPATH}/build/apk/classes.dex -o ./outputs/smali/classes
  java -jar baksmali-3.0.9-fat.jar d --code-offsets ${APKDPATH}/build/apk/classes2.dex -o ./outputs/smali/classes2
fi
```

Install application into Android Emulator:

```
# Optionally uninstall
adb uninstall sh.kau.playground
adb install ./outputs/rebuild-signed_min.apk
```

Enable Developer Tools, Indicate "Wait For Debugger", Add target application.

Start the application from emulator.

Get the JDWP pid and start debugger:

```
adb jdwp
# You may need to Ctrl+C out of 'adb jdwp' command.
adb forward tcp:8700 jdwp:20414
jdb -attach localhost:8700
```

```
Set uncaught java.lang.Throwable
Set deferred uncaught java.lang.Throwable
Initializing jdb ...
> stop in sh.kau.playground.quoter.QuotesRepoImpl.fetchQuote
Set breakpoint sh.kau.playground.quoter.QuotesRepoImpl.fetchQuote
> cont
> Nothing suspended.

Breakpoint hit: "thread=DefaultDispatcher-worker-3", sh.kau.playground.quoter.QuotesRepoImpl.fetchQuote(), line=25 bci=31

DefaultDispatcher-worker-3[1] where
  [1] sh.kau.playground.quoter.QuotesRepoImpl.fetchQuote (QuotesRepoImpl.kt:25)
  [2] sh.kau.playground.quoter.QuotesRepoImpl.quoteForTheDay (QuotesRepoImpl.kt:22)
  [3] sh.kau.playground.features.settings.viewmodel.SettingsBViewModelImpl$onSubscribed$1.invokeSuspend (SettingsBViewModel
Impl.kt:38)
  [4] kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith (ContinuationImpl.kt:33)
  [5] kotlinx.coroutines.DispatchedTask.run (DispatchedTask.kt:101)
  [6] kotlinx.coroutines.internal.LimitedDispatcher$Worker.run (LimitedDispatcher.kt:113)
  [7] kotlinx.coroutines.scheduling.TaskImpl.run (Tasks.kt:89)
  [8] kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely (CoroutineScheduler.kt:589)
  [9] kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask (CoroutineScheduler.kt:823)
  [10] kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker (CoroutineScheduler.kt:720)
  [11] kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run (CoroutineScheduler.kt:707)
DefaultDispatcher-worker-3[1] bytecodes sh.kau.playground.quoter.QuotesRepoImpl quoteForTheDay
0000: 70 20 06 c8 10 00 0c 01 11 01
```

Get more insight into smali bytecode offsets via baksmali output with bytecode offsets included. For example:

```
java -jar baksmali.jar d --code-offsets classes.dex -o smali/
```

Note: We've already done this with our script above in `outputs/smali`.

## Untested

You can than use the smali output's bytecode offsets to interpret the exact line being executed via Frida hooks:

```
// smali_stepper.js
'use strict';

const libart = "libart.so";
let stepping = true; // start in step mode

// Hook ART interpreter bridge
function hookSymbol(name) {
    const addr = Module.findExportByName(libart, name);
    if (!addr) {
        console.error("[-] Could not find " + name);
        return;
    }

    Interceptor.attach(addr, {
        onEnter: function (args) {
            const dex_pc = args[2].toInt32(); // dex program counter
            send({ event: "step", dex_pc: dex_pc });

            if (stepping) {
                // Block thread until host replies
                const op = recv("control", function (msg) {
                    if (msg.payload === "continue") {
                        stepping = false;
                    } else if (msg.payload === "step") {
                        stepping = true;
                    }
                });
                op.wait(); // block until host says continue or step
            }
        }
    });
    console.log("[+] Hooked " + name + " @ " + addr);
}

hookSymbol("artInterpreterToInterpreterBridge");
```

Run the frida server on the android side.

Inject the Frida gadget via:

```
frida -U -f com.example.app -l smali_stepper.js --no-pause
```

Host side:

```
import frida
import sys

def on_message(message, data):
    if message['type'] == 'send':
        payload = message['payload']
        if payload['event'] == 'step':
            dex_pc = payload['dex_pc']
            print(f"[smali-step] dex_pc=0x{dex_pc:x} ({dex_pc})")

            # Simple REPL
            cmd = input("(stepper) [n]ext / [c]ontinue > ").strip()
            if cmd == "c":
                script.post({"type": "control", "payload": "continue"})
            else:
                script.post({"type": "control", "payload": "step"})

    elif message['type'] == 'error':
        print("Error:", message['stack'])

package = "com.example.app"
device = frida.get_usb_device()
pid = device.spawn([package])
session = device.attach(pid)

with open("smali_stepper.js") as f:
    script = session.create_script(f.read())
script.on("message", on_message)
script.load()

device.resume(pid)
sys.stdin.read()

# python3 stepper.py

'''
java -jar baksmali.jar d -b classes.dex -o smali_out/

[smali-step] dex_pc=0xc (12)
(stepper) [n]ext / [c]ontinue >

Optionally disable AOT/JIT with: adb shell setprop dalvik.vm.usejit false
'''
```

Now use the dex_pc to map to the relavent line of code in a Class.Method.


```
# resetprop ro.debuggable 1
# stop
# start
$ adb shell am set-debug-app -w <package>
$ adb shell am set-debug-app -w --persistent <package>
```

Note: TWRP can be run temporarily: `fastboot boot twrp.img`

Test TWRP on emulator: https://twrp.me/twrp/androidemulator.html

https://bitbucket.org/JesusFreke/smalidea/downloads/smalidea-0.06.zip


https://crosp.net/blog/software-development/mobile/android/android-reverse-engineering-debugging-smali-using-smalidea/