# Production Hardening Plan

Current target: raise real-user production readiness from roughly 4.5/10 to 8+/10.

## Implemented In This Iteration

- Production config validation blocks default API, encryption, and audit signing keys.
- Security headers middleware adds no-sniff, frame denial, no-store caching, referrer policy, and
  permissions policy.
- Optional trusted hosts and CORS allow-list configuration.
- Tamper-evident short action logs with HMAC signatures chained line by line.
- Action log size rotation.
- CI static security scan with Bandit.
- CI dependency vulnerability scan with pip-audit.

## Highest-Impact Remaining Work

1. Replace API-key auth with OIDC/OAuth2, short-lived JWTs, refresh rotation, and device-bound
   credentials.
2. Add Android Play Integrity or hardware-backed device attestation.
3. Store encryption and signing keys in KMS or a cloud secret manager.
4. Move audit logs to append-only object storage or database table with WORM retention.
5. Encrypt database evidence fields with envelope encryption.
6. Add Alembic migrations and retention/delete/export jobs.
7. Add signed threat-intelligence feeds with provenance validation.
8. Add isolated OCR/media/APK worker sandboxes.
9. Add TLS ingress, mTLS service-to-service traffic, WAF, and rate limits at edge.
10. Add mobile local enforcement for download blocking and permission remediation.

## Score Impact

- After this iteration: estimated production readiness improves from 4.5/10 to about 5.8/10.
- With OIDC, KMS, encrypted persistence, device attestation, and append-only audit storage: 7.5/10.
- With isolated malware/media pipelines, signed feeds, full retention controls, and production
  monitoring: 8.5+/10.

