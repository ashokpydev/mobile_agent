# System Architecture

## Context

Mobile Privacy Guardian protects Android users from privacy risks, scams, phishing, malware
indicators, suspicious permissions, data leaks, and social-engineering attempts. The backend is
privacy-first: most raw user artifacts should be analyzed on-device when possible, with only
redacted findings synced to the cloud by default.

## Services

- Android Collector: gathers installed app metadata, permission state, notification snippets, QR
  URLs, user-submitted messages, and file scan results.
- Local Analysis Runtime: SQLite-backed offline scanners for permissions, PII patterns, URL
  heuristics, and cached threat indicators.
- API Service: FastAPI service exposing analysis endpoints and agent Q&A.
- Detection Workers: async workers for OCR, APK analysis, feed ingestion, and heavier ML scoring.
- Threat Intelligence Service: normalizes malicious domains, phishing indicators, fake app package
  names, and malware signatures into Redis/PostgreSQL/pgvector.
- AI Agent Service: LangGraph workflow that chooses tools, summarizes evidence, explains risk, and
  recommends actions.
- Observability Stack: OpenTelemetry traces, Prometheus metrics, Grafana dashboards, LangSmith for
  agent traces.

## Data Flow

1. Android collects privacy/security artifact.
2. On-device scanners produce local findings when possible.
3. User-approved cloud analysis sends minimized payloads to FastAPI.
4. API routes call deterministic detection tools and threat feed lookups.
5. Agent workflow combines tool results into natural-language answers.
6. Findings are stored as encrypted records with retention controls.
7. Alerts are pushed to the notification engine and dashboard trend store.

## Microservice Boundaries

- `api-service`: REST, auth, RBAC, request validation, response shaping.
- `agent-service`: LangGraph execution, LLM provider routing, prompt/version management.
- `detection-service`: fraud, phishing, permission, malware, PII, and OCR pipelines.
- `threat-intel-service`: feed ingestion, reputation scoring, pgvector retrieval.
- `notification-service`: alert rules, deduplication, delivery, user preferences.
- `dashboard-service`: trend aggregation and privacy/security score history.

The current repository implements the first deployable slice inside one FastAPI process. The module
boundaries match the future service boundaries so teams can split them when scale requires it.

