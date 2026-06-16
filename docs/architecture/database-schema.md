# Database Schema

## Tables

### `device_app_risks`

- `id`: UUID primary key.
- `device_id`: pseudonymous device identifier.
- `package_name`: Android package name.
- `app_name`: display name.
- `risk_score`: 0-100.
- `severity`: Low, Medium, High, Critical.
- `permissions`: JSON permission list.
- `findings`: JSON finding details.
- `created_at`: timestamp.

### `threat_findings`

- `id`: UUID primary key.
- `device_id`: optional pseudonymous device identifier.
- `category`: fraud, phishing, pii, permission, malware, threat-intel.
- `severity`: Low, Medium, High, Critical.
- `confidence`: model confidence.
- `title`: short finding title.
- `explanation`: human-readable explanation.
- `evidence`: minimized JSON evidence.
- `created_at`: timestamp.

## Planned Tables

- `devices`: device metadata, attestation status, and encrypted user binding.
- `notification_rules`: alert thresholds and user notification preferences.
- `threat_indicators`: normalized domains, APK hashes, package names, and feed source metadata.
- `scan_jobs`: OCR, APK, and file scan job state.
- `score_snapshots`: dashboard trend history for privacy, permission, threat, and exposure scores.
- `audit_events`: RBAC and administrative access logs.

## Vector Storage

Use pgvector for threat intelligence embeddings and prior explanation retrieval:

- phishing kit descriptions
- malware family notes
- scam message exemplars
- app reputation summaries

