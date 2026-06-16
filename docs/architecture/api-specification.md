# API Specification

Base path: `/api/v1`

Protected analysis endpoints require:

- `x-api-key`: authenticated service or client key.
- `x-privacy-consent: granted`: explicit user consent for artifact analysis.

## Health

`GET /health`

Returns service health.

## Permission Analysis

`POST /analysis/permissions`

Analyzes installed app permissions and special access.

Request fields:

- `device_id`: stable pseudonymous device identifier.
- `apps`: list of installed applications, package names, permissions, and special access flags.

Response fields:

- `privacy_score`: 0-100, higher is safer.
- `risky_apps`: apps with risk score, severity, findings, and recommendations.

## Message Analysis

`POST /analysis/messages`

Classifies user-submitted message content as `Safe`, `Suspicious`, `High Risk`, or `Critical`.

## URL Analysis

`POST /analysis/urls`

Analyzes URLs, domains, QR payloads, and deep links for phishing indicators.

## Sensitive Data Scan

`POST /analysis/sensitive-data`

Scans text extracted from documents, images, or files. Image OCR is intended to run in the worker
pipeline before this endpoint receives text.

## Malware Indicator Scan

`POST /analysis/malware`

Analyzes app behavior signals and returns suspicious apps that should trigger user alerts.
Indicators include accessibility abuse, overlay permission, SMS behavior, unknown installer source,
dangerous permission combinations, high background network activity, suspicious package names, and
known malicious domain contacts.

## Content Safety Scan

`POST /analysis/content-safety`

Opt-in scanner for messages, extracted text, OCR output, image captions, media labels, and
video/audio transcripts.
The `enabled` flag must be true for scanning to occur. The scanner is limited to concrete
harmful/illegal indicators such as explicit threats, violent extremist recruitment indicators,
child-safety exploitation risk, financial crime, dangerous weapons instructions, and targeted
violence. It can also flag adult or sexually explicit media labels generated on-device so the app
can show a private popup without uploading private media or showing explicit thumbnails. For nudity
image findings, the mobile client should offer user-confirmed `Delete` and `Skip` actions locally.
It should not be used for broad political opinion monitoring.

## Download Guard

`POST /analysis/download-guard`

Evaluates a pending download before saving. The policy supports `block`, `warn`, or `allow` for
adult/explicit video indicators. Inputs should be minimized to URL, filename, MIME type, source app,
and on-device media labels. The app should not upload private videos for this decision.

## Agent Q&A

`POST /agent/ask`

Answers natural-language security questions with optional message or URL evidence.

## Privacy Controls

`GET /privacy/controls`

Returns runtime privacy posture, including consent requirement, raw artifact storage status,
retention windows, external AI status, and active privacy guarantees.
