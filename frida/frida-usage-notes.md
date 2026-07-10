
Load the server:

```
adb push frida-server-17.3.2-android-x86_64 /data/frida-server
adb shell chmod +x /data/frida-server
adb shell setsid /data/frida-server &
```

Test the server is running from client:

```
frida-ps -U
```

Fire up target application with the client:

```
frida -U -f sh.kau.playground
```

Start target all and inject script:

```
frida -U -f sh.kau.playground -l path/to/script.js
```





Consider

- ThreadReference.Name ... get all the thread names during AllThreads and during Thread Start events.
- Treat ThreadReference as an ObjectReference?!