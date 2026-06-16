# Android App

The `android-app/` project is a native Android shell for the Mobile Privacy Guardian product.
It is intentionally local-first: the first screen audits installed applications that request camera
permission and highlights riskier combinations such as camera plus microphone, SMS, overlays,
accessibility, unknown APK installation, or precise location.

## Build

Open `android-app/` in Android Studio, or build from the command line:

```bash
cd android-app
gradle assembleDebug
```

For command-line builds, `local.properties` must point at an installed Android SDK:

```properties
sdk.dir=/path/to/Android/Sdk
```

The debug APK is generated at:

```text
android-app/app/build/outputs/apk/debug/app-debug.apk
```

Install with:

```bash
adb install -r android-app/app/build/outputs/apk/debug/app-debug.apk
```

## Camera Access Scope

Android normal apps cannot reliably identify every other app that is using the camera at the exact
current moment. The app therefore provides:

- A local scan of apps that request `android.permission.CAMERA`.
- Risk scoring for camera apps that also request sensitive permissions or special capabilities.
- Shortcuts to Android Privacy Dashboard, Camera Permission Manager, installed-app settings, and
  per-app settings.

For live or recent camera access, users should use Android's green privacy indicator and Privacy
Dashboard. Future privileged or enterprise builds can add device-owner APIs where policy allows.
