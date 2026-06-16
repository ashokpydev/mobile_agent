# Mobile Privacy Guardian Agent

Production-grade FastAPI backend for an AI-powered Android privacy and security assistant.
The service analyzes app permissions, suspicious messages, phishing URLs, and sensitive data
exposure, then returns explainable risk scores and recommendations.

## Capabilities

- Consent-first, privacy-by-design API guardrails.
- Scoped API-key authorization foundation for service-to-service access.
- Per-device rate limiting to reduce automated abuse.
- Privacy-safe audit event generation with pseudonymized device IDs and redacted summaries.
- Default zero-hour raw artifact retention; findings retain only minimized security evidence.
- Permission intelligence for dangerous Android permissions and special access.
- Fraud and social-engineering message detection for SMS, exports, email, and notifications.
- Phishing URL checks for obfuscation, typosquatting, suspicious TLDs, and unsafe transport.
- Sensitive data discovery for PAN, Aadhaar-like IDs, payment cards, CVV, IFSC, API keys,
  tokens, recovery phrases, and wallet addresses.
- Malware indicator alerts for suspicious app behavior, unknown installer sources, dangerous
  permission combinations, overlays, accessibility abuse, SMS abuse, and malicious domain contact.
- Opt-in harmful/illegal content safety scan for concrete indicators such as explicit threats,
  violent extremist recruitment indicators, child-safety risks, financial crime, dangerous weapon
  instructions, targeted-violence indicators, and adult media labels from on-device classifiers.
- Download Guard policy to block, warn, or allow adult/explicit video downloads before saving.
- LangGraph-ready agent orchestration layer for natural-language security Q&A.
- Async FastAPI foundation with Pydantic v2 and SQLAlchemy models.
- Docker, Kubernetes, CI, monitoring rules, and enterprise security documentation.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

## Example Requests

```bash
curl -X POST http://localhost:8000/api/v1/analysis/messages \
  -H 'content-type: application/json' \
  -H 'x-api-key: dev-local-api-key' \
  -H 'x-privacy-consent: granted' \
  -d '{"source":"sms","text":"Urgent KYC update. Share OTP at http://bit.ly/fix-now"}'
```

```bash
curl -X POST http://localhost:8000/api/v1/analysis/permissions \
  -H 'content-type: application/json' \
  -H 'x-api-key: dev-local-api-key' \
  -H 'x-privacy-consent: granted' \
  -d '{"device_id":"device-1","apps":[{"package_name":"com.demo","app_name":"Demo","permissions":["android.permission.READ_SMS"],"can_draw_overlays":true}]}'
```

```bash
curl http://localhost:8000/api/v1/privacy/controls \
  -H 'x-api-key: dev-local-api-key'
```

```bash
curl -X POST http://localhost:8000/api/v1/analysis/malware \
  -H 'content-type: application/json' \
  -H 'x-api-key: dev-local-api-key' \
  -H 'x-privacy-consent: granted' \
  -d '{"device_id":"device-1","apps":[{"package_name":"com.secure.bank.verify","app_name":"Bank Security Update","permissions":["android.permission.READ_SMS"],"uses_accessibility_service":true,"can_draw_overlays":true,"known_bad_domain_contacts":["malicious-example.test"],"suspicious_package_name":true}]}'
```

```bash
curl -X POST http://localhost:8000/api/v1/analysis/content-safety \
  -H 'content-type: application/json' \
  -H 'x-api-key: dev-local-api-key' \
  -H 'x-privacy-consent: granted' \
  -d '{"device_id":"device-1","enabled":true,"items":[{"item_id":"msg-1","content_type":"message","source":"sms","text":"message says to attack a public crowd tomorrow"}]}'
```

For private media, the Android app should run frame/image/video classification on-device and send
only labels such as `adult`, `nudity`, or `explicit sexual`:

```bash
curl -X POST http://localhost:8000/api/v1/analysis/content-safety \
  -H 'content-type: application/json' \
  -H 'x-api-key: dev-local-api-key' \
  -H 'x-privacy-consent: granted' \
  -d '{"device_id":"device-1","enabled":true,"items":[{"item_id":"video-1","content_type":"video","source":"gallery","file_name":"private_video.mp4","media_labels":["adult","nudity","explicit sexual"]}]}'
```

```bash
curl -X POST http://localhost:8000/api/v1/analysis/download-guard \
  -H 'content-type: application/json' \
  -H 'x-api-key: dev-local-api-key' \
  -H 'x-privacy-consent: granted' \
  -d '{"device_id":"device-1","url":"https://example.test/downloads/adult-video.mp4","file_name":"adult-video.mp4","mime_type":"video/mp4","source_app":"Chrome","media_labels":["adult","explicit sexual"],"policy":{"enabled":true,"adult_content_action":"block"}}'
```

## Product Differentiators

- Local-first detection: the Android client should run permission, URL, PII, and cached threat
  checks offline before sending anything to the cloud.
- Consent-gated cloud analysis: no analysis endpoint accepts user artifacts unless consent is
  explicitly present.
- Zero raw retention by default: raw messages, file text, and sensitive artifacts are not retained
  unless enterprise policy changes the retention setting.
- Explainable risk engine: every score is backed by findings, evidence, and remediation guidance.
- Redacted auditability: security teams can audit system behavior without exposing raw user data.
- External AI off by default: LLM calls are policy-controlled and must be preceded by redaction.
- Mobile-specific protection: permissions, accessibility, overlays, notification access, OTP abuse,
  UPI/KYC scams, QR/deep links, and sensitive file exposure are handled together.
- Harmful-content scanning is opt-in and category-bound; it is not designed for broad political
  opinion monitoring or vague “anti-national” labeling.

## Project Layout

```text
app/
  api/v1/              REST API surface
  core/                settings and security primitives
  db/                  async SQLAlchemy session setup
  models/              persistence models
  schemas/             Pydantic request/response contracts
  services/
    agent/             AI agent orchestration
    detection/         permissions, fraud, phishing, PII engines
    threat_intel/      threat feed adapters
docs/                  architecture, API, schema, threat model, hardening
deploy/                Kubernetes and monitoring assets
tests/                 unit and API tests
```

## Roadmap

- Add Android client collector for permissions, notification events, and local SQLite sync.
- Replace heuristic model adapters with trained fraud, phishing, OCR, and PII pipelines.
- Add pgvector retrieval over threat intelligence and user-specific security history.
- Add RBAC, biometric device attestation hooks, signed feed updates, and audit trails.
