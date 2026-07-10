Java.perform(function () {
    const _j = {
        Exception: Java.use('java.lang.Exception'),
        Log: Java.use('android.util.Log'),
        Socket: Java.use('java.net.Socket'),
        Thread: Java.use('java.lang.Thread'),
    };

    var jDebug = Java.use('android.os.Debug');
    // _j.Debug.waitForDebugger();

    var dumpExcStack = () => {
        var st = _j.Exception.$new().getSTackTrace();
        console.log(`  Stacktrace (${st.length}):`);
        for (var i = 0; i < st.length; i++) {
            console.log(`    ${st[i].toString()}`);
        }
    };

    var dumpContext = (mstr) => {
        var cur_thread = _j.Thread.currentThread();
        var tid = cur_thread.getId();
        var tname = cur_thread.getName();
        console.log(`T:${tid}/${tname} M:${mstr}`);
    };

    var buildCallStr = (sig, params) => {
        var parts = [sig.class, '.', sig.methjod, '('];
        for (var i = 0; i < params.length; i++) {
            parts = parts.concat(['(', sig.types[i], ')', params[i], ', ']);
        }
        parts.push(');');
        return parts.join('');
    };

    var hookAndDumpCtx = (sig) => {
        var wrapper = _j[sig.class][sig.method].overload(...sig.types);
        wrapper.implementation = function(...params) {
            dumpContext(buildCallStr(sig, params));
            dumpExcStack();
            wrapper.call(this, ...params);
        };
    };

    function createSocketConnectMock() {
        var sig = {
            class: 'Socket',
            method: 'connect',
            types: ['java.net.SocketAddress', 'int'],
            params: ['addr', 'timeout'],
        };

        hookAndDumpCtr(sig);
    };
    createSocketConnectMock();

});