# LangGraph Workflow

## Nodes

- `classify_intent`: determine whether the user asks about app risk, message fraud, URL safety,
  sensitive files, account compromise, or general privacy posture.
- `collect_context`: gather provided artifacts and user/device metadata.
- `permission_tool`: analyze installed apps and dangerous permissions.
- `fraud_tool`: classify scam or social-engineering messages.
- `phishing_tool`: analyze URLs, QR payloads, domains, and deep links.
- `pii_tool`: scan extracted text for sensitive data.
- `threat_intel_tool`: check known malicious domains, packages, hashes, and indicators.
- `recommendation_tool`: produce prioritized actions.
- `explain`: generate concise natural-language explanation with evidence.

## Edges

`classify_intent -> collect_context -> relevant tools -> recommendation_tool -> explain`

High-confidence critical findings should bypass extra LLM reasoning and return deterministic safety
guidance first. LLM responses should cite tool evidence and avoid claiming certainty beyond the
detector confidence.

## Privacy Rules

- Redact OTPs, account numbers, tokens, and card values before LLM calls.
- Prefer offline/on-device tools when available.
- Store prompts and traces only after user consent and redaction.
- Disable external AI by default for enterprise or high-sensitivity deployments.

