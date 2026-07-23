# Resources

- frida-jdwp-loader
- jdwp-shellifier

This only works if android:debuggable="true" in the target's manifest, or the device itself is configured to force all apps debuggable (common on rooted test devices, ro.debuggable=1). If the real-world APK you're analyzing ships non-debuggable (the overwhelmingly common case for production/Play Store apps), this path is closed to you and your smali-patch approach remains the only option — worth having your tool check androguard's APK.get_attribute_value("application", "debuggable") up front and branch between the two injection strategies accordingly.

INTERNET permission is required on the target app if you use Gadget's default Listen mode (since it opens a TCP socket) — same requirement your smali-patched Gadget already has.
