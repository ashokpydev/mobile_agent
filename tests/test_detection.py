from app.schemas.analysis import (
    AppPermissionScanRequest,
    InstalledApp,
    MessageAnalysisRequest,
    MalwareScanRequest,
    AppBehaviorSignals,
    ContentItem,
    ContentSafetyScanRequest,
    DownloadGuardRequest,
    SensitiveDataScanRequest,
    UrlAnalysisRequest,
)
from app.schemas.common import Classification, Severity
from app.services.detection.fraud import FraudMessageDetector
from app.services.detection.content_safety import ContentSafetyDetector
from app.services.detection.download_guard import DownloadGuard
from app.services.detection.malware import MalwareIndicatorDetector
from app.services.detection.permissions import PermissionRiskAnalyzer
from app.services.detection.phishing import PhishingDetector
from app.services.detection.sensitive_data import SensitiveDataDetector


def test_permission_scan_flags_excessive_sensitive_access() -> None:
    payload = AppPermissionScanRequest(
        device_id="device-1",
        apps=[
            InstalledApp(
                package_name="com.example.flashlight",
                app_name="Flashlight",
                permissions=[
                    "android.permission.CAMERA",
                    "android.permission.RECORD_AUDIO",
                    "android.permission.READ_SMS",
                ],
                can_draw_overlays=True,
            )
        ],
    )

    result = PermissionRiskAnalyzer().scan(payload)

    assert result.privacy_score < 50
    assert result.risky_apps[0].severity in {Severity.high, Severity.critical}
    assert any(f.category == "dangerous_permission" for f in result.risky_apps[0].findings)


def test_fraud_detector_classifies_otp_bank_link_as_high_risk() -> None:
    result = FraudMessageDetector().analyze(
        MessageAnalysisRequest(
            source="sms",
            sender="BANK",
            text="Urgent KYC update required. Your bank account will be blocked. Share OTP at http://bit.ly/fix-now",
        )
    )

    assert result.risk_score >= 65
    assert result.classification in {Classification.high_risk, Classification.critical}
    assert result.recommended_actions


def test_phishing_detector_flags_obfuscated_non_https_url() -> None:
    result = PhishingDetector().analyze(
        UrlAnalysisRequest(url="http://sbi-login-secure.example.click@evil.test/login")
    )

    assert result.risk_score >= 50
    assert any(f.category == "url_obfuscation" for f in result.findings)


def test_sensitive_data_detector_masks_pii() -> None:
    result = SensitiveDataDetector().scan(
        SensitiveDataScanRequest(
            content="PAN ABCDE1234F and token secret_key=sk_test_1234567890abcdef123456",
            source_name="notes.txt",
        )
    )

    labels = {finding.label for finding in result.findings}
    assert {"pan", "api_key"} <= labels
    assert result.exposure_score >= 80
    assert all("..." in finding.masked_value for finding in result.findings)


def test_malware_detector_flags_known_bad_app_behavior() -> None:
    result = MalwareIndicatorDetector().scan(
        MalwareScanRequest(
            device_id="device-1",
            apps=[
                AppBehaviorSignals(
                    package_name="com.secure.bank.verify",
                    app_name="Bank Security Update",
                    permissions=[
                        "android.permission.READ_SMS",
                        "android.permission.REQUEST_INSTALL_PACKAGES",
                    ],
                    installer_source="unknown.store",
                    uses_accessibility_service=True,
                    can_draw_overlays=True,
                    sends_sms=True,
                    known_bad_domain_contacts=["malicious-example.test"],
                    suspicious_package_name=True,
                )
            ],
        )
    )

    assert result.malware_alert is True
    assert result.suspicious_apps[0].app_name == "Bank Security Update"
    assert result.suspicious_apps[0].risk_score >= 85


def test_content_safety_respects_off_toggle() -> None:
    result = ContentSafetyDetector().scan(
        ContentSafetyScanRequest(
            device_id="device-1",
            enabled=False,
            items=[
                ContentItem(
                    item_id="msg-1",
                    content_type="message",
                    text="attack public crowd",
                )
            ],
        )
    )

    assert result.enabled is False
    assert result.scanned_items == 0
    assert result.findings == []


def test_content_safety_flags_concrete_harmful_indicator_when_enabled() -> None:
    result = ContentSafetyDetector().scan(
        ContentSafetyScanRequest(
            device_id="device-1",
            enabled=True,
            items=[
                ContentItem(
                    item_id="msg-1",
                    content_type="message",
                    text="message says to attack a public crowd tomorrow",
                )
            ],
        )
    )

    assert result.alert is True
    assert result.findings[0].category == "explicit_threat"


def test_content_safety_flags_adult_video_from_media_labels() -> None:
    result = ContentSafetyDetector().scan(
        ContentSafetyScanRequest(
            device_id="device-1",
            enabled=True,
            items=[
                ContentItem(
                    item_id="video-1",
                    content_type="video",
                    source="gallery",
                    file_name="private_video.mp4",
                    media_labels=["adult", "nudity", "explicit sexual"],
                )
            ],
        )
    )

    assert result.alert is False
    assert result.findings[0].category == "adult_sexual_content"
    assert result.findings[0].severity == Severity.medium


def test_download_guard_blocks_adult_video_download() -> None:
    result = DownloadGuard().evaluate(
        DownloadGuardRequest(
            device_id="device-1",
            url="https://example.test/downloads/adult-video.mp4",
            file_name="adult-video.mp4",
            mime_type="video/mp4",
            source_app="Chrome",
            media_labels=["adult", "explicit sexual"],
        )
    )

    assert result.decision == "block"
    assert result.category == "adult_explicit_download"


def test_download_guard_allows_when_disabled() -> None:
    result = DownloadGuard().evaluate(
        DownloadGuardRequest(
            device_id="device-1",
            file_name="adult-video.mp4",
            policy={"enabled": False},
        )
    )

    assert result.enabled is False
    assert result.decision == "allow"
