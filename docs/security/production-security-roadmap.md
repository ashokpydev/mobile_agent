# Production Security Roadmap

This application should compete on trust, not only detection breadth. The differentiator is a
privacy-first security architecture that protects users even while analyzing threats.

## Implemented Guardrails

- Scoped API-key authorization foundation.
- Explicit consent requirement for analysis routes.
- Per-device or per-client rate limiting.
- Redaction helper for audit summaries.
- Pseudonymous device hashing for audit events.
- Raw artifact retention disabled by default.
- External AI disabled by default.
- Privacy controls endpoint for runtime posture inspection.
- Threat model and hardening checklist.

## Next Required Controls

- Replace API-key auth with OIDC/OAuth2, short-lived JWTs, device attestation, and refresh rotation.
- Store secrets in KMS or cloud secret manager; never in environment-only production config.
- Persist audit logs to append-only storage with tamper-evident hashing.
- Apply field-level encryption to findings and evidence columns.
- Add user-controlled export, delete, and retention workflows.
- Add signed threat-feed ingestion and feed provenance verification.
- Add malware/APK static analysis sandboxing.
- Add OCR isolation for image/document scanning.
- Add SAST, DAST, dependency, container, and IaC scans to CI.
- Add mobile biometric gate for vault and sensitive remediation actions.
- Add privacy-preserving telemetry with opt-in sampling.

## Differentiation From Existing Apps

- Local-first protection instead of cloud-first inspection.
- User-controlled consent and retention for each sensitive data source.
- Explainable scoring rather than opaque “safe/unsafe” labels.
- Scam, phishing, permissions, file exposure, and AI guidance in one assistant.
- Redacted AI workflow that can run without external LLM providers.
- Enterprise-friendly posture reporting for compliance and audits.
- Designed for India-specific risks such as PAN, Aadhaar-like patterns, UPI, KYC, and banking scams,
  while remaining extensible for global privacy identifiers.

