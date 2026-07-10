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

// frida -U -f com.example.app -l smali_stepper.js --no-pause
