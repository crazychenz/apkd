const mod = Process.getModuleByName("libart.so");
const symOffset = 0x444940; // objdump -T libart.so | grep SetJdwp
const addr = mod.base.add(symOffset);
console.log("libart base: " + mod.base);
console.log("Computed address: " + addr);

Interceptor.attach(addr, {
  onEnter: function (args) {
    console.log("Entered SetJdwpAllowed @ " + addr);
    try { console.log("arg:", args[0]); } catch (e) {}
  },
  onLeave: function (retval) {
    console.log("Leaving SetJdwpAllowed, retval:", retval);
  }
});

/*
var SetJdwpAllowed = Module.findExportByName("libart.so", "_ZN3art3Dbg14SetJdwpAllowedEb");

if (SetJdwpAllowed) {
    Interceptor.attach(SetJdwpAllowed, {
        onEnter: function(args) {
            console.log("[+] SetJdwpAllowed called");
            console.log("    allowed = " + args[0]);
            
            // Force it to always be true
            args[0] = ptr(1);
        },
        onLeave: function(retval) {
            console.log("[+] SetJdwpAllowed finished");
        }
    });
    console.log("[+] Hooked SetJdwpAllowed");
} else {
    console.log("[-] SetJdwpAllowed not found");
}
*/
