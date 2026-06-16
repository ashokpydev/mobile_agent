from datetime import datetime, timezone

from app.core.privacy import pseudonymize, redact_text


class AuditLogger:
    """Privacy-safe audit event builder.

    Production should send this to an append-only audit sink. The local scaffold returns the event
    object so route handlers can persist or emit it without retaining raw user artifacts.
    """

    def event(
        self,
        *,
        actor: str,
        action: str,
        device_id: str | None,
        summary: str,
        metadata: dict | None = None,
    ) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "action": action,
            "device_hash": pseudonymize(device_id) if device_id else None,
            "summary": redact_text(summary),
            "metadata": metadata or {},
        }

