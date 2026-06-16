# Threat Model

## Protected Assets

- SMS, notification, and message content.
- App inventory and permission state.
- Sensitive files, OCR text, and detected PII.
- User identity, device identifiers, and security history.
- Threat intelligence feeds and model outputs.

## Adversaries

- Phishing operators and scam callers.
- Malicious Android applications.
- Network attackers attempting interception.
- Insider misuse of user scan data.
- Model prompt-injection attempts through messages or URLs.
- Supply-chain attackers targeting feeds, dependencies, or CI/CD.

## Key Threats

- Raw sensitive data leakage to cloud or LLM providers.
- False negative on high-risk scam content.
- False positive causing user alarm or account lockout.
- Feed poisoning with malicious or misleading indicators.
- Unauthorized access to stored scan findings.
- Abuse of accessibility or notification collection on Android.

## Mitigations

- Data minimization and local-first analysis.
- TLS everywhere and encryption at rest.
- Field-level encryption for sensitive evidence.
- Pseudonymous device identifiers.
- RBAC, audit logs, and short-lived service credentials.
- Signed threat feeds and feed provenance tracking.
- Deterministic critical-path recommendations.
- Prompt-injection filtering and redaction before external model calls.
- Retention controls and user-controlled deletion.

