# Patching Frida in Smali

## Objection Identify MainActivity

- Look for `activity` / `intent-filter` containing `android.intent.action.MAIN` + `android.intent.category.LAUNCHER`
  - Optionally look for `launchable-activity: name='com.example.app.MainActivity'` via aapt2
- Look for `targetActivity` in manifest
- Explicitly inject via `--target-class`
- **Note:** Multiple MAIN / LAUNCHER activities (e.g. android:enabled="false") causes issues. Breaks androguard too via get_main_activity(). Split APKs are also problematic.

## Use ADB to Identify MainActivity

```sh
adb shell dumpsys package <package.name>

# Look for
# - `Application` in `applicationInfo={... className=... }`
# - `Registered ContentProviders:` ... any `ContentProvider` classes
# - `Activity Resolver Tables`
adb shell cmd package resolve-activity --brief <package.name>

# Confirm with
adb shell am force-stop <package.name>
adb logcat -c
adb shell am start -W -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n <package.name>/<resolved-activity>
adb logcat | grep -E "ActivityTaskManager|ActivityManager"
```

Android Startup Process:

1. `Application.attachBaseContext()`
2. Every declared `ContentProvider`'s `onCreate()` (yes — before Application.onCreate())
3. `Application.onCreate()`
4. The launcher `Activity`'s `onCreate()`

Recommended Approach:

- Patch custom `Application` subclass.
- Patch any `ContentProvider` (e.g. `androidx.startup.InitializationProvider`)

Observe with frida:

```javascript
// startup_order.js
// Logs the real order of Application / ContentProvider / Activity creation
// so you can pick the earliest reliable Frida hook point.

Java.perform(function () {
    var t0 = Date.now();
    function log(tag, name) {
        console.log("[+" + (Date.now() - t0) + "ms] " + tag + ": " + name);
    }

    // --- 1. Application creation ---
    // Instrumentation.newApplication is called by the system to instantiate
    // the app's Application (or custom subclass), before attachBaseContext/onCreate.
    try {
        var Instrumentation = Java.use("android.app.Instrumentation");

        // Overload: newApplication(ClassLoader, String className, Context)
        Instrumentation.newApplication.overload(
            "java.lang.ClassLoader", "java.lang.String", "android.content.Context"
        ).implementation = function (cl, className, ctx) {
            log("Application (newApplication)", className);
            return this.newApplication(cl, className, ctx);
        };
    } catch (e) {
        console.log("[!] Could not hook newApplication(cl,str,ctx): " + e);
    }

    try {
        var Instrumentation2 = Java.use("android.app.Instrumentation");
        // Overload: newApplication(Class, Context)
        Instrumentation2.newApplication.overload(
            "java.lang.Class", "android.content.Context"
        ).implementation = function (clazz, ctx) {
            log("Application (newApplication/Class)", clazz.getName());
            return this.newApplication(clazz, ctx);
        };
    } catch (e) {
        console.log("[!] Could not hook newApplication(Class,ctx): " + e);
    }

    // callApplicationOnCreate fires right after attachBaseContext, wrapping onCreate()
    try {
        var Instrumentation3 = Java.use("android.app.Instrumentation");
        Instrumentation3.callApplicationOnCreate.implementation = function (app) {
            log("Application.onCreate", app.getClass().getName());
            return this.callApplicationOnCreate(app);
        };
    } catch (e) {
        console.log("[!] Could not hook callApplicationOnCreate: " + e);
    }

    // --- 2. ContentProvider creation ---
    // attachInfo() runs before onCreate(), is rarely overridden by subclasses,
    // and hands us the ProviderInfo (with .name = fully qualified class name).
    try {
        var ContentProvider = Java.use("android.content.ContentProvider");
        ContentProvider.attachInfo.overload(
            "android.content.Context", "android.content.pm.ProviderInfo"
        ).implementation = function (ctx, info) {
            log("ContentProvider.attachInfo", info.name.value);
            return this.attachInfo(ctx, info);
        };
    } catch (e) {
        console.log("[!] Could not hook ContentProvider.attachInfo(2-arg): " + e);
    }

    try {
        var ContentProvider2 = Java.use("android.content.ContentProvider");
        // Some API levels have a 3-arg private overload too
        ContentProvider2.attachInfo.overload(
            "android.content.Context", "android.content.pm.ProviderInfo", "boolean"
        ).implementation = function (ctx, info, testing) {
            log("ContentProvider.attachInfo(3-arg)", info.name.value);
            return this.attachInfo(ctx, info, testing);
        };
    } catch (e) {
        // fine if this overload doesn't exist on this API level
    }

    // --- 3. Activity creation ---
    // callActivityOnCreate is called by the system regardless of which
    // Activity subclass is involved, and gives us the instance directly.
    try {
        var Instrumentation4 = Java.use("android.app.Instrumentation");
        Instrumentation4.callActivityOnCreate.overload(
            "android.app.Activity", "android.os.Bundle"
        ).implementation = function (activity, bundle) {
            log("Activity.onCreate", activity.getClass().getName());
            return this.callActivityOnCreate(activity, bundle);
        };
    } catch (e) {
        console.log("[!] Could not hook callActivityOnCreate(2-arg): " + e);
    }

    try {
        var Instrumentation5 = Java.use("android.app.Instrumentation");
        // Newer API levels added a PersistableBundle overload
        Instrumentation5.callActivityOnCreate.overload(
            "android.app.Activity", "android.os.Bundle", "android.os.PersistableBundle"
        ).implementation = function (activity, bundle, persistentState) {
            log("Activity.onCreate(+persistentState)", activity.getClass().getName());
            return this.callActivityOnCreate(activity, bundle, persistentState);
        };
    } catch (e) {
        // fine if unavailable on this API level
    }

    console.log("[*] Startup-order tracer installed.");
});
```

Run app with frida:

```sh
frida -U -f <package> -l startup_order.js --no-pause
```

Example Output:

```text
[*] Startup-order tracer installed.
[+12ms] Application (newApplication): com.example.app.MyApplication
[+18ms] Application.onCreate: com.example.app.MyApplication
[+31ms] ContentProvider.attachInfo: com.example.app.startup.InitProvider
[+45ms] Activity.onCreate: com.example.app.MainActivity
```

## Adjust locals

```text
Injecting loadLibrary call at line: 10
Attempting to fix the constructors .locals count
Current locals value is 0, updating to 1
```

## clinit exists

Before:

```smali
.class public Lcom/example/app/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"

# static fields
.field private static final TAG:Ljava/lang/String;

# direct methods
.method static constructor <clinit>()V
    .locals 1

    const-string v0, "MainActivity"

    sput-object v0, Lcom/example/app/MainActivity;->TAG:Ljava/lang/String;

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method
```

After:

```smali
.method static constructor <clinit>()V
    .locals 1

    const-string v0, "frida-gadget"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    const-string v0, "MainActivity"

    sput-object v0, Lcom/example/app/MainActivity;->TAG:Ljava/lang/String;

    return-void
.end method
```

## clinit does not exist

Before:

```smali
.class public Lcom/example/app/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"

# direct methods
.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 1

    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f030000

    invoke-virtual {p0, v0}, Lcom/example/app/MainActivity;->setContentView(I)V

    return-void
.end method
```

After:

```smali
.class public Lcom/example/app/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"

# direct methods
.method static constructor <clinit>()V
    .locals 1

    const-string v0, "frida-gadget"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 1

    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    const v0, 0x7f030000

    invoke-virtual {p0, v0}, Lcom/example/app/MainActivity;->setContentView(I)V

    return-void
.end method
```




## Use Case: Dynamic Patching

- Re-sign APK
- Deploy
- Detect Hook Points (adb)
- Patch
- Build
- Deploy
- Test


## Use Case: Static Patching

- Guess activity via manifest
- Patch
- Build
- Deploy
- Test