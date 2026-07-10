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