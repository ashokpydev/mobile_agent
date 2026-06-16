# Deployment Architecture

## Environments

- Local: Docker Compose with FastAPI, PostgreSQL/pgvector, Redis.
- Staging: Kubernetes namespace with reduced retention and synthetic data.
- Production: Kubernetes with managed PostgreSQL, managed Redis, KMS, WAF, and private networking.

## Runtime

- API replicas scale horizontally behind an ingress controller.
- Workers scale independently by queue depth.
- PostgreSQL stores findings, device risk snapshots, and audit records.
- Redis caches threat indicators, deduplication keys, and rate-limit counters.
- Object storage holds encrypted OCR artifacts only when policy permits.

## CI/CD

1. Lint and test.
2. Build signed container image.
3. Run vulnerability and IaC scans.
4. Deploy to staging.
5. Run smoke and integration tests.
6. Promote to production through approval gate.
7. Emit deployment markers to observability tools.

