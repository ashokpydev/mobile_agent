import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.config import settings
from app.core.privacy import pseudonymize, redact_text
from app.core.security import get_field_encryptor


class AuditLogger:
    """Privacy-safe audit event builder and short action-log writer.

    Production should send this to an append-only audit sink. The local scaffold writes
    a compact line to disk with the free-text fields encrypted at rest (via the configured
    `encryption_key`) on top of PII redaction, and enforces `default_retention_days` by
    dropping expired entries from the active log and deleting expired rotated archives.
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
            "timestamp": timestamp,
            "actor": actor,
            "action": action,
            "device_hash": pseudonymize(device_id) if device_id else None,
            "summary": redact_text(summary),
            "metadata": metadata or {},
        }
        self._append_short_log(event)
        return event

    def decrypt_summary(self, token: str) -> str:
        """Decrypt a `summary_enc`/`metadata_enc` value read back from the log file."""
        return get_field_encryptor().decrypt(token)

    def _append_short_log(self, event: dict) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._enforce_retention()
        device = event["device_hash"][:12] if event["device_hash"] else "none"
        encryptor = get_field_encryptor()
        body = (
            f"{event['timestamp']} | actor={event['actor']} | action={event['action']} | "
            f"device={device} | summary_enc={encryptor.encrypt(event['summary'])}"
        )
        if event["metadata"]:
            metadata_token = encryptor.encrypt(json.dumps(event["metadata"], default=str))
            body = f"{body} | metadata_enc={metadata_token}"
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

    def _enforce_retention(self) -> None:
        if self.log_path.exists() and self.log_path.stat().st_size >= settings.action_log_max_bytes:
            rotated_path = self.log_path.with_suffix(
                f"{self.log_path.suffix}.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            )
            self.log_path.rename(rotated_path)
        else:
            self._drop_expired_lines()
        self._purge_expired_archives()

    def _drop_expired_lines(self) -> None:
        if not self.log_path.exists():
            return
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.default_retention_days)
        lines = self.log_path.read_text(encoding="utf-8").splitlines(keepends=True)
        kept = [line for line in lines if not self._line_expired(line, cutoff)]
        if len(kept) != len(lines):
            self.log_path.write_text("".join(kept), encoding="utf-8")

    def _purge_expired_archives(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.default_retention_days)
        for archive in self.log_path.parent.glob(f"{self.log_path.name}.*"):
            if archive == self.chain_path:
                continue
            try:
                archived_at = datetime.strptime(archive.suffix.lstrip("."), "%Y%m%d%H%M%S").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                continue
            if archived_at < cutoff:
                archive.unlink(missing_ok=True)

    @staticmethod
    def _line_expired(line: str, cutoff: datetime) -> bool:
        timestamp_str = line.split(" | ", 1)[0].strip()
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
        except ValueError:
            return False
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return timestamp < cutoff
