# CounterIpApp — Build & Operations Guide

Minimal two-screen Android test app: a counter screen (1s tick, used to observe
whether the process is alive/suspended) and a button that fetches the
public-facing IP over HTTPS and shows it on a second screen.

Target: **compileSdk / targetSdk = 33 (Android 13)**, **minSdk = 24**.

---

## Prerequisites

- Android SDK installed, with `platforms;android-33` and a matching
  `build-tools` version available (via `sdkmanager` or the newer `android`
  CLI).
- `ANDROID_HOME` (or `ANDROID_SDK_ROOT`) set, or a `local.properties` file in
  the project root pointing `sdk.dir` at your SDK.
- No separate Gradle install needed — `./gradlew` is bundled and will
  download the correct Gradle version (8.7) on first run.

```bash
unzip CounterIpApp.zip
cd CounterIpApp
chmod +x gradlew   # in case the zip lost the executable bit
```

---

## Debug build

```bash
./gradlew assembleDebug
```

Output: `app/build/outputs/apk/debug/app-debug.apk`

Debug builds use the auto-generated Android debug keystore, so no signing
setup is required.

### Install directly to a connected device/emulator

```bash
./gradlew installDebug
# or
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Uninstall

```bash
adb uninstall com.example.counteripapp
```

---

## Release build (unsigned, no setup)

```bash
./gradlew assembleRelease
```

If `keystore.properties` doesn't exist yet, this produces an **unsigned**
APK:

```
app/build/outputs/apk/release/app-release-unsigned.apk
```

This is useful on its own if you only need an unsigned artifact (e.g. to
manually sign with different keys per test run), but it **won't install** on
a device as-is until it's signed.

---

## Release build (signed, automatic via Gradle)

### 1. Generate a signing key (skip if you already have one)

```bash
keytool -genkeypair -v \
  -keystore my-release-key.jks \
  -alias release-key \
  -keyalg RSA -keysize 2048 -validity 10000
```

Place the resulting `.jks` file wherever you like (commonly the project
root, one level up from `app/`).

### 2. Configure signing

```bash
cp keystore.properties.template keystore.properties
```

Edit `keystore.properties`:

```properties
storeFile=../my-release-key.jks
storePassword=<your store password>
keyAlias=release-key
keyPassword=<your key password>
```

`storeFile` is relative to the project root (where `keystore.properties`
lives). `keystore.properties` is already listed in `.gitignore` — don't
commit the real version.

### 3. Build

```bash
./gradlew assembleRelease
```

Output (now signed + zipaligned automatically by AGP):

```
app/build/outputs/apk/release/app-release.apk
```

### Sanity check that signing was picked up

```bash
ls app/build/outputs/apk/release/
```

- `app-release.apk` → signed correctly.
- `app-release-unsigned.apk` → `keystore.properties` wasn't found, or a
  property failed to parse. Confirm the file is in the project root (next
  to `settings.gradle.kts`), not inside `app/`.

---

## Release build (signed manually with `apksigner`)

If you'd rather sign outside of Gradle — e.g. to test signing separately —
skip `keystore.properties` entirely and sign the unsigned APK yourself:

```bash
./gradlew assembleRelease
# -> app/build/outputs/apk/release/app-release-unsigned.apk

zipalign -v -p 4 \
  app/build/outputs/apk/release/app-release-unsigned.apk \
  app-release-aligned.apk

apksigner sign \
  --ks my-release-key.jks \
  --out app-release-signed.apk \
  app-release-aligned.apk

apksigner verify app-release-signed.apk
```

`zipalign` and `apksigner` both live in
`$ANDROID_HOME/build-tools/<version>/`.

---

## Verifying a built APK

```bash
# Confirm signing scheme(s) used
apksigner verify --verbose app-release.apk

# Inspect the manifest / permissions / SDK versions
aapt dump badging app-release.apk

# Confirm the exact IP-fetch / activity behavior at the bytecode level
unzip -l app-release.apk        # list contents
```

---

## Cleaning the project

```bash
./gradlew clean
```

Removes all `build/` output directories (`app/build/`, etc.) without
touching source, config, or the Gradle wrapper itself.

---

## Full rebuild from scratch

```bash
./gradlew clean assembleDebug assembleRelease
```

Builds both variants in one pass — handy when you want a fresh debug and
release APK pair for comparison in your analysis tool.

---

## Checking dependency / SDK versions in use

```bash
./gradlew app:dependencies          # full dependency tree
./gradlew -v                        # Gradle + JVM version info
```

---

## Key files reference

| File | Purpose |
|---|---|
| `app/src/main/java/.../MainActivity.kt` | Counter screen; `loadIpScreen()` is the intended breakpoint target (network call + screen transition) |
| `app/src/main/java/.../SecondActivity.kt` | IP display screen + exit button |
| `app/build.gradle.kts` | App module config: SDK versions, dependencies, signing |
| `keystore.properties.template` | Copy to `keystore.properties` and fill in real values to enable signed release builds |
| `gradle/wrapper/gradle-wrapper.properties` | Pins the Gradle version (8.7) that `./gradlew` will download and use |

---

## Common gotchas

- **`Package platforms;android-33 not found`** — install it:
  `sdkmanager "platforms;android-33"` or `android sdk install platforms/android-33`.
- **`SDK location not found`** — set `ANDROID_HOME`, or create
  `local.properties` in the project root with `sdk.dir=/path/to/sdk`.
- **`app-release-unsigned.apk` when you expected a signed one** — see the
  sanity-check step under "Release build (signed, automatic via Gradle)"
  above.
- **First `./gradlew` invocation is slow** — it's downloading the full
  Gradle 8.7 distribution; subsequent runs use the cached copy in
  `~/.gradle/wrapper/dists/`.