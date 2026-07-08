# Mobile Privacy Guardian - Application Requirements and Development Status

## 1. Application Overview

Mobile Privacy Guardian is an Android privacy and security assistant with a FastAPI backend. The
application helps users detect risky app permissions, scam messages, phishing URLs, sensitive data
exposure, malware indicators, harmful content signals, and unsafe downloads.

The product is designed around a privacy-first model:

- Run analysis locally on the Android device whenever possible.
- Send only minimized or redacted data to the backend.
- Require explicit user consent before cloud analysis.
- Avoid storing raw messages, private files, private media, or sensitive artifacts by default.
- Provide explainable findings, risk scores, and recommended user actions.

## 2. Objectives

- Protect Android users from privacy leaks, scams, phishing, malware indicators, and unsafe content.
- Give users clear risk scores and plain-language recommendations.
- Detect suspicious permission combinations in installed apps.
- Identify sensitive information inside user-submitted text or extracted document content.
- Help users make safe decisions before opening links, trusting messages, or saving risky downloads.
- Maintain privacy-safe auditability without exposing raw user data.
- Provide a backend architecture that can grow into separate services for detection, threat
  intelligence, agent workflows, notifications, and dashboards.

## 3. Target Users

- Android users who want personal privacy and security protection.
- Users who frequently receive SMS, messaging, email, QR, or link-based fraud attempts.
- Users who want to review risky permissions used by installed apps.
- Enterprise or managed-device users who may later need policy controls, audit trails, and
  administrative dashboards.

## 4. Functional Requirements

### 4.1 Android Permission Audit

The application must scan installed Android apps and identify risky permissions or special access.

Required capabilities:

- Collect installed app package name, app name, permissions, and special access flags.
- Detect sensitive permissions such as camera, microphone, SMS, precise location, notification
  access, VPN access, accessibility service access, overlay access, and unknown app installation.
- Identify risky permission combinations.
- Produce an app-level risk score from 0 to 100.
- Assign severity for each risky app.
- Show findings and recommendations to the user.
- Provide shortcuts to Android privacy settings, app settings, and permission managers.

### 4.2 Message Scam and Fraud Detection

The application must analyze user-submitted messages from sources such as SMS, WhatsApp, Telegram,
email, or notifications.

Required capabilities:

- Detect phishing, KYC scams, OTP scams, fake banking alerts, payment fraud, malware install lures,
  unknown-source APK prompts, and protection-disable instructions.
- Classify messages as safe, suspicious, high risk, or critical.
- Return risk score, confidence, findings, explanation, and recommended actions.
- Avoid logging or retaining raw message content.

### 4.3 URL and QR Phishing Detection

The application must analyze URLs, domains, QR payloads, and deep links.

Required capabilities:

- Detect suspicious domains, unsafe HTTP, obfuscated URLs, shortened links, suspicious TLDs,
  typosquatting, and phishing-like patterns.
- Return domain, severity, risk score, confidence, findings, and recommended actions.
- Support user-shared browser URLs or browser export data.
- Avoid hidden access to other browsers' private history.

### 4.4 Sensitive Data Detection

The application must scan text extracted from user-selected files, images, documents, or pasted
content.

Required capabilities:

- Detect Aadhaar-like IDs, PAN-like IDs, payment card numbers, CVV, IFSC codes, API keys, tokens,
  recovery phrases, wallet addresses, phone numbers, and emails.
- Mask sensitive values in results.
- Return exposure score, findings, and recommendations.
- Support OCR pipeline integration in the future.

### 4.5 Malware Indicator Detection

The application must detect suspicious app behavior signals.

Required capabilities:

- Analyze permissions, installer source, APK hash, accessibility usage, overlay usage, SMS behavior,
  notification reading, background network activity, known bad domain contacts, and suspicious
  package names.
- Flag suspicious apps.
- Return highest severity, indicators, explanation, and recommended action.

### 4.6 Content Safety Scan

The application must support opt-in content safety scanning.

Required capabilities:

- Scan only when the user or policy enables the feature.
- Analyze message text, extracted text, OCR output, captions, media labels, and transcripts.
- Detect concrete harmful or illegal indicators such as explicit threats, violent extremist
  recruitment indicators, child-safety exploitation risks, financial crime, dangerous weapon
  instructions, and targeted violence.
- Support on-device media labels such as adult, nudity, or explicit sexual content.
- Avoid uploading private images or videos.
- Provide a privacy note in the response.

### 4.7 Private Media and Nudity Handling

The Android app must handle private media locally.

Required capabilities:

- Run image or video classification on-device.
- Send only labels to the backend when cloud decision support is required.
- Show a private popup for nudity or explicit media findings.
- Provide user actions such as Delete and Skip.
- Avoid showing explicit previews in alerts.

### 4.8 Download Guard

The application must evaluate pending downloads before saving.

Required capabilities:

- Accept URL, file name, MIME type, source app, and on-device media labels.
- Support policy decisions: allow, warn, or block.
- Block or warn on adult or explicit video indicators depending on policy.
- Optionally block unknown sources.
- Avoid uploading private video content.

### 4.9 AI Security Assistant

The backend must provide an agent-style question-and-answer endpoint.

Required capabilities:

- Accept a natural-language security question.
- Optionally include message or URL evidence.
- Return an answer, recommended actions, confidence, and evidence.
- Use tool-based detection results where available.
- Support future LangGraph orchestration and external AI routing with redaction controls.

### 4.10 Privacy Controls

The backend must expose the current privacy posture.

Required capabilities:

- Report whether consent is required.
- Report raw artifact storage status.
- Report findings and raw artifact retention windows.
- Report whether external AI is enabled.
- Return active privacy guarantees.

## 5. API Requirements

Base API path: `/api/v1`

Implemented and required endpoints:

- `GET /health`
- `POST /analysis/permissions`
- `POST /analysis/messages`
- `POST /analysis/urls`
- `POST /analysis/sensitive-data`
- `POST /analysis/malware`
- `POST /analysis/content-safety`
- `POST /analysis/download-guard`
- `POST /agent/ask`
- `GET /privacy/controls`

Analysis endpoints must require:

- `x-api-key`
- `x-privacy-consent: granted`

## 6. Security and Privacy Requirements

- Require API-key authentication for protected routes.
- Enforce scoped authorization for analysis operations.
- Enforce rate limiting.
- Require explicit privacy consent before artifact analysis.
- Pseudonymize device identifiers in audit logs.
- Redact sensitive summaries before logging.
- Use tamper-evident HMAC-chained action logs.
- Disable raw artifact storage by default.
- Disable external AI by default.
- Redact content before any future external AI call.
- Add security headers in production.
- Validate production configuration strictly.

## 7. Non-Functional Requirements

- Backend must use FastAPI and asynchronous request handling.
- Request and response models must use Pydantic.
- Detection results must be explainable.
- The system must be deployable with Docker.
- Kubernetes deployment manifests must be available for production-style deployment.
- Tests must cover API behavior, privacy guardrails, detection logic, and audit logging.
- Architecture must allow future service separation.
- Observability should support Prometheus metrics, traces, and dashboarding.

## 8. What Has Been Implemented So Far

### 8.1 Backend Foundation

Implemented:

- FastAPI application setup.
- API router under `/api/v1`.
- Health endpoint.
- Pydantic request and response schemas.
- Configuration management.
- CORS support.
- Trusted host middleware support.
- Security headers middleware.
- Dockerfile and Docker Compose setup.
- Kubernetes deployment, service, and config map manifests.

### 8.2 Authentication, Consent, and Rate Limiting

Implemented:

- API key based access.
- Scoped authorization foundation.
- Privacy consent enforcement for analysis routes.
- Per-device or client-oriented rate limiting foundation.
- Tests confirming that analysis requests fail when consent is missing.

### 8.3 Detection Modules

Implemented:

- Permission risk analyzer.
- Fraud and suspicious message detector.
- Phishing URL detector.
- Sensitive data detector.
- Malware indicator detector.
- Content safety detector.
- Download Guard evaluator.
- Risk scoring, severity, findings, and recommendations across core detectors.

### 8.4 Privacy and Audit Features

Implemented:

- Privacy controls endpoint.
- Safe defaults showing consent required, raw artifact storage disabled, and external AI disabled.
- Privacy-safe audit logger.
- Pseudonymized device IDs in action logs.
- Redacted action summaries.
- HMAC-chained signatures for tamper-evident logs.

### 8.5 Android App Scaffold

Implemented:

- Native Android project scaffold.
- App name and basic Android resources.
- Main activity.
- Settings activity.
- History activity.
- Share scan activity.
- Backend client class.
- Local scan support for camera permission audit.
- Risk scoring for suspicious permission combinations.
- Shortcuts into Android privacy and app settings.
- Supporting Android classes for browser privacy, notification monitoring, realtime monitoring,
  sensitive text guard, scan history, boot receiver, and VPN service scaffolding.

### 8.6 Agent Layer

Implemented:

- Agent request and response schemas.
- Agent API route.
- LangGraph-ready workflow structure.
- Tool-oriented agent service modules.

### 8.7 Documentation and Tests

Implemented:

- README with capabilities and quickstart.
- API specification document.
- System architecture document.
- Android app architecture document.
- Database schema document.
- Deployment architecture document.
- LangGraph workflow document.
- Mobile integration document.
- Threat model and production hardening documentation.
- Tests for API behavior.
- Tests for detection logic.
- Tests for audit behavior.

## 9. What Still Needs To Be Developed

### 9.1 Android App Completion

Needs development:

- Complete production UI for dashboard, alerts, scan results, settings, and history.
- Full local permission collector for all supported privacy permissions.
- Local SQLite storage and sync queue.
- User consent screens and privacy settings.
- Share-sheet integration for URLs, messages, and files.
- Notification-based scanning with user-approved accessibility or notification access.
- On-device URL, PII, and cached threat checks.
- On-device media classifier for nudity/adult labels.
- Delete and Skip workflow for private media alerts.
- Download interception or browser/VPN-based download guard integration.
- Better offline mode and retry behavior.
- Android build verification in CI.

### 9.2 Detection Improvements

Needs development:

- Replace heuristic detectors with stronger trained or hybrid ML pipelines where appropriate.
- Add OCR pipeline for images and documents.
- Add APK/static analysis pipeline.
- Add fake app/package reputation checks.
- Add QR-specific parsing and deep-link risk scoring.
- Add richer UPI, banking, KYC, and regional scam detection patterns.
- Add false-positive feedback loop.
- Add model evaluation datasets and benchmarks.

### 9.3 Threat Intelligence

Needs development:

- Threat feed ingestion service.
- Malicious domain, phishing indicator, malware signature, and fake package feeds.
- Signed feed updates.
- Local cache for offline Android checks.
- Reputation scoring.
- pgvector retrieval over threat intelligence and prior findings.

### 9.4 AI Agent Productionization

Needs development:

- Full LangGraph workflow execution.
- Retrieval over threat intelligence and user security history.
- Prompt/version management.
- Redaction layer before AI calls.
- External AI provider policy controls.
- Agent trace observability.
- Stronger confidence calibration and fallback handling.

### 9.5 Backend Persistence and Data Lifecycle

Needs development:

- Production database migrations.
- Encrypted findings storage.
- Retention jobs for findings and raw artifacts if ever enabled.
- User/device profile management.
- Alert deduplication and status tracking.
- Scan history API.
- Privacy-safe export and delete flows.

### 9.6 Notifications and User Alerts

Needs development:

- Notification service.
- Alert rules and severity thresholds.
- User preferences for alert categories.
- Alert deduplication.
- Push notification integration.
- In-app alert timeline.

### 9.7 Enterprise and Admin Features

Needs development:

- Role-based access control.
- Admin dashboard.
- Organization and device grouping.
- Policy management.
- Device attestation.
- Managed-device or device-owner mode integrations.
- Compliance reports.

### 9.8 Production Hardening

Needs development:

- Secrets management integration.
- Strong production API-key lifecycle.
- Request signing or device attestation for mobile clients.
- More complete abuse prevention.
- Expanded security tests.
- Dependency vulnerability checks in CI.
- Observability dashboards.
- Runbooks for incident response.

## 10. Suggested Development Priorities

1. Complete Android user flows for permission scan, message/link sharing, scan history, and settings.
2. Add local SQLite storage, consent state, and offline scan queue.
3. Strengthen detection quality for messages, URLs, sensitive data, and malware indicators.
4. Add threat intelligence ingestion and local cache support.
5. Implement production persistence, alert history, and retention jobs.
6. Productionize the AI agent workflow with redaction and policy controls.
7. Add dashboard, enterprise policy, and admin features.
8. Expand testing, CI, monitoring, and production hardening.

## 11. Current Project Status Summary

The project currently has a strong backend foundation and a working Android scaffold. Core API
contracts, privacy guardrails, detection modules, audit logging, deployment files, architecture
documents, and tests are already present.

The main remaining work is to turn the Android scaffold into a complete user-facing product, improve
detection depth beyond heuristics, add threat intelligence and persistence, and productionize the
agent, notifications, dashboard, and enterprise controls.
