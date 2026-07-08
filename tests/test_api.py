from fastapi.testclient import TestClient

import app.api.v1.analysis as analysis_module
from app.main import app
from app.services.audit import AuditLogger


client = TestClient(app)
AUTH_HEADERS = {"x-api-key": "dev-local-api-key", "x-privacy-consent": "granted"}


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_message_analysis_endpoint() -> None:
    response = client.post(
        "/api/v1/analysis/messages",
        headers=AUTH_HEADERS,
        json={
            "source": "sms",
            "sender": "unknown",
            "text": "Final warning: verify KYC and login at http://bit.ly/account-now",
        },
    )

    assert response.status_code == 200
    assert response.json()["risk_score"] >= 30


def test_analysis_requires_consent() -> None:
    response = client.post(
        "/api/v1/analysis/messages",
        headers={"x-api-key": "dev-local-api-key"},
        json={"source": "sms", "text": "hello"},
    )

    assert response.status_code == 428


def test_privacy_controls_report_safe_defaults() -> None:
    response = client.get("/api/v1/privacy/controls", headers={"x-api-key": "dev-local-api-key"})

    assert response.status_code == 200
    body = response.json()
    assert body["consent_required"] is True
    assert body["raw_artifact_storage"] is False
    assert body["external_ai_enabled"] is False


def test_malware_endpoint_returns_alert() -> None:
    response = client.post(
        "/api/v1/analysis/malware",
        headers=AUTH_HEADERS,
        json={
            "device_id": "device-1",
            "apps": [
                {
                    "package_name": "com.secure.bank.verify",
                    "app_name": "Bank Security Update",
                    "permissions": ["android.permission.READ_SMS"],
                    "uses_accessibility_service": True,
                    "can_draw_overlays": True,
                    "known_bad_domain_contacts": ["malicious-example.test"],
                    "suspicious_package_name": True,
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["malware_alert"] is True


def test_content_safety_endpoint_uses_enabled_toggle() -> None:
    response = client.post(
        "/api/v1/analysis/content-safety",
        headers=AUTH_HEADERS,
        json={
            "device_id": "device-1",
            "enabled": False,
            "items": [
                {
                    "item_id": "msg-1",
                    "content_type": "message",
                    "source": "sms",
                    "text": "attack public crowd",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["scanned_items"] == 0


def test_content_safety_endpoint_flags_adult_video_label() -> None:
    response = client.post(
        "/api/v1/analysis/content-safety",
        headers=AUTH_HEADERS,
        json={
            "device_id": "device-1",
            "enabled": True,
            "items": [
                {
                    "item_id": "video-1",
                    "content_type": "video",
                    "source": "gallery",
                    "file_name": "private_video.mp4",
                    "media_labels": ["adult", "nudity", "explicit sexual"],
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["findings"][0]["category"] == "adult_sexual_content"


def test_content_safety_endpoint_writes_critical_escalation_audit_event(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(analysis_module, "audit_logger", AuditLogger(log_path=tmp_path / "actions.log"))

    response = client.post(
        "/api/v1/analysis/content-safety",
        headers=AUTH_HEADERS,
        json={
            "device_id": "device-1",
            "enabled": True,
            "items": [
                {
                    "item_id": "chat-1",
                    "content_type": "message",
                    "source": "sms",
                    "text": "sharing minor explicit content link",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["findings"][0]["category"] == "child_safety_risk"
    log_text = (tmp_path / "actions.log").read_text(encoding="utf-8")
    assert "content_safety.critical_escalation" in log_text


def test_download_guard_endpoint_blocks_adult_download() -> None:
    response = client.post(
        "/api/v1/analysis/download-guard",
        headers=AUTH_HEADERS,
        json={
            "device_id": "device-1",
            "url": "https://example.test/adult-video.mp4",
            "file_name": "adult-video.mp4",
            "mime_type": "video/mp4",
            "source_app": "Chrome",
            "media_labels": ["adult", "explicit sexual"],
            "policy": {"enabled": True, "adult_content_action": "block"},
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "block"
