import re
from datetime import datetime, timedelta, timezone

from app.services.audit import AuditLogger


def _summary_token(log_line: str) -> str:
    match = re.search(r"summary_enc=([^|]+?)\s*\|", log_line)
    return match.group(1).strip()


def test_audit_logger_writes_short_redacted_action_log(tmp_path) -> None:
    log_path = tmp_path / "actions.log"
    logger = AuditLogger(log_path=log_path)

    event = logger.event(
        actor="api-key-client",
        action="analysis.sensitive_data",
        device_id="device-123",
        summary="Sensitive scan found PAN ABCDE1234F and token secret_key=abc12345678901234567890",
    )

    log_text = log_path.read_text(encoding="utf-8")
    decrypted_summary = logger.decrypt_summary(_summary_token(log_text))
    assert event["action"] == "analysis.sensitive_data"
    assert "analysis.sensitive_data" in log_text
    assert "device=" in log_text
    assert "sig=" in log_text
    assert "ABCDE1234F" not in log_text
    assert "secret_key=" not in log_text
    assert "ABCDE1234F" not in decrypted_summary
    assert "[REDACTED]" in decrypted_summary


def test_audit_logger_redacts_otp_and_personal_info(tmp_path) -> None:
    log_path = tmp_path / "actions.log"
    logger = AuditLogger(log_path=log_path)

    logger.event(
        actor="api-key-client",
        action="analysis.message",
        device_id="device-123",
        summary="User shared OTP is 123456, email ashok@example.com, phone +91 98765 43210",
    )

    log_text = log_path.read_text(encoding="utf-8")
    decrypted_summary = logger.decrypt_summary(_summary_token(log_text))
    assert "123456" not in log_text
    assert "ashok@example.com" not in log_text
    assert "98765 43210" not in log_text
    assert "123456" not in decrypted_summary
    assert "[REDACTED]" in decrypted_summary


def test_audit_logger_encrypts_summary_at_rest(tmp_path) -> None:
    log_path = tmp_path / "actions.log"
    logger = AuditLogger(log_path=log_path)

    logger.event(
        actor="api-key-client",
        action="analysis.message",
        device_id="device-123",
        summary="plain summary text with no PII",
    )

    log_text = log_path.read_text(encoding="utf-8")
    assert "plain summary text" not in log_text
    assert logger.decrypt_summary(_summary_token(log_text)) == "plain summary text with no PII"


def test_audit_logger_drops_expired_entries_from_active_log(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("app.services.audit.settings.default_retention_days", 30)
    log_path = tmp_path / "actions.log"
    logger = AuditLogger(log_path=log_path)

    old_timestamp = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat(timespec="seconds")
    log_path.write_text(
        f"{old_timestamp} | actor=x | action=old.event | device=none | summary_enc=stale | sig=stale\n",
        encoding="utf-8",
    )

    logger.event(
        actor="api-key-client",
        action="analysis.message",
        device_id=None,
        summary="fresh event",
    )

    log_text = log_path.read_text(encoding="utf-8")
    assert "old.event" not in log_text
    assert "analysis.message" in log_text


def test_audit_logger_purges_expired_rotated_archives(tmp_path) -> None:
    log_path = tmp_path / "actions.log"
    old_archive = log_path.with_suffix(".log.20200101000000")
    old_archive.write_text("stale archived content\n", encoding="utf-8")

    logger = AuditLogger(log_path=log_path)
    logger.event(
        actor="api-key-client",
        action="analysis.message",
        device_id=None,
        summary="fresh event",
    )

    assert not old_archive.exists()
