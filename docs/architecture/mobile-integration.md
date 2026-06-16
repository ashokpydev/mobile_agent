# Mobile Integration Architecture

## Android Modules

- Permission Collector: uses Android package APIs to inventory permissions and special access.
- Notification Guard: optional notification listener with explicit consent and local redaction.
- Message Importers: user-initiated SMS, WhatsApp, Telegram, and email export analysis.
- URL and QR Scanner: extracts links from clipboard, QR codes, and shared intents.
- File Scanner: local text extraction and OCR before minimized backend submission.
- Secure Vault: encrypted local storage for sensitive documents and remediation actions.

## Offline Mode

The Android app should cache detector rules, threat indicators, and user preferences in SQLite.
Offline scans should return local findings and sync only summary metadata when connectivity returns
and user policy allows sync.

## Privacy Controls

- Explicit opt-in for notification, accessibility, file, and message import features.
- Per-source toggles and visible data-retention controls.
- Redaction before cloud analysis.
- Clear explanations for every requested Android permission.

