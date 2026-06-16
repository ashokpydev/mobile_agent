import hashlib
import hmac
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.core.privacy import pseudonymize, redact_text


class AuditLogger:
    """Privacy-safe audit event builder and short action-log writer.

    Production should send this to an append-only audit sink. The local scaffold also writes a
    compact redacted line to disk without retaining raw user artifacts.
    """

    def __init__(self, log_path: str | Path | None = None) -> None:
        self.log_path = Path(log_path or settings.action_log_path)
        self.chain_path = self.log_path.with_suffix(f"{self.log_path.suffix}.chain")

    def event(
        self,
        *,
        actor: str,
        action: str,
        device_id: str | None,
        summary: str,
        metadata: dict | None = None,
    ) -> dict:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "action": action,
            "device_hash": pseudonymize(device_id) if device_id else None,
            "summary": redact_text(summary),
            "metadata": metadata or {},
        }
        self._append_short_log(event | {"timestamp": timestamp})
        return event

    def _append_short_log(self, event: dict) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._rotate_if_needed()
        device = event["device_hash"][:12] if event["device_hash"] else "none"
        body = (
            f"{event['timestamp']} | actor={event['actor']} | action={event['action']} | "
            f"device={device} | {event['summary']}"
        )
        signature = self._signature(body)
        line = f"{body} | sig={signature}\n"
        self.chain_path.write_text(signature, encoding="utf-8")
        with self.log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(line)

    def _signature(self, body: str) -> str:
        previous = self._previous_signature()
        payload = f"{previous}|{body}".encode("utf-8")
        return hmac.new(
            settings.audit_log_signing_key.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()

    def _previous_signature(self) -> str:
        if not self.chain_path.exists():
            return "GENESIS"
        return self.chain_path.read_text(encoding="utf-8").strip() or "GENESIS"

    def _rotate_if_needed(self) -> None:
        if not self.log_path.exists() or self.log_path.stat().st_size < settings.action_log_max_bytes:
            return
        rotated_path = self.log_path.with_suffix(
            f"{self.log_path.suffix}.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        )
        self.log_path.rename(rotated_path)
