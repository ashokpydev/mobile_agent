from app.services.audit import AuditLogger


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
    assert event["action"] == "analysis.sensitive_data"
    assert "analysis.sensitive_data" in log_text
    assert "device=" in log_text
    assert "ABCDE1234F" not in log_text
    assert "secret_key=" not in log_text
    assert "[REDACTED]" in log_text
    assert "sig=" in log_text
