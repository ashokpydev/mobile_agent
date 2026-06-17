from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import Classification, Finding, Severity


class InstalledApp(BaseModel):
    package_name: str
    app_name: str
    permissions: list[str] = Field(default_factory=list)
    has_accessibility_service: bool = False
    has_notification_access: bool = False
    has_vpn_service: bool = False
    can_draw_overlays: bool = False


class AppPermissionScanRequest(BaseModel):
    device_id: str
    apps: list[InstalledApp]


class AppRisk(BaseModel):
    package_name: str
    app_name: str
    risk_score: int = Field(ge=0, le=100)
    severity: Severity
    findings: list[Finding]
    recommendations: list[str]


class AppPermissionScanResponse(BaseModel):
    device_id: str
    privacy_score: int = Field(ge=0, le=100)
    risky_apps: list[AppRisk]


class MessageAnalysisRequest(BaseModel):
    source: str = Field(examples=["sms", "whatsapp", "telegram", "email", "notification"])
    sender: str | None = None
    text: str


class MessageAnalysisResponse(BaseModel):
    classification: Classification
    risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    findings: list[Finding]
    explanation: str
    recommended_actions: list[str]


class UrlAnalysisRequest(BaseModel):
    url: HttpUrl | str
    source: str | None = None


class UrlAnalysisResponse(BaseModel):
    url: str
    domain: str
    severity: Severity
    risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    findings: list[Finding]
    recommended_actions: list[str]


class SensitiveDataScanRequest(BaseModel):
    content: str
    source_name: str | None = None
    content_type: str = "text"


class SensitiveDataFinding(BaseModel):
    label: str
    severity: Severity
    masked_value: str
    start: int
    end: int
    recommendation: str


class SensitiveDataScanResponse(BaseModel):
    source_name: str | None
    exposure_score: int = Field(ge=0, le=100)
    findings: list[SensitiveDataFinding]
    recommendations: list[str]


class AppBehaviorSignals(BaseModel):
    package_name: str
    app_name: str
    permissions: list[str] = Field(default_factory=list)
    installer_source: str | None = None
    apk_sha256: str | None = None
    uses_accessibility_service: bool = False
    can_install_unknown_apps: bool = False
    can_draw_overlays: bool = False
    sends_sms: bool = False
    reads_notifications: bool = False
    background_network_connections: int = 0
    known_bad_domain_contacts: list[str] = Field(default_factory=list)
    suspicious_package_name: bool = False


class MalwareScanRequest(BaseModel):
    device_id: str
    apps: list[AppBehaviorSignals]


class MalwareAppFinding(BaseModel):
    package_name: str
    app_name: str
    risk_score: int = Field(ge=0, le=100)
    severity: Severity
    indicators: list[str]
    explanation: str
    recommended_action: str


class MalwareScanResponse(BaseModel):
    device_id: str
    malware_alert: bool
    highest_severity: Severity
    suspicious_apps: list[MalwareAppFinding]


class ContentItem(BaseModel):
    item_id: str
    content_type: str = Field(examples=["message", "text", "image_ocr", "video_transcript"])
    source: str | None = Field(default=None, examples=["sms", "gallery", "download", "whatsapp_export"])
    text: str | None = None
    media_labels: list[str] = Field(
        default_factory=list,
        description="On-device image/video classifier labels, such as adult, nudity, explicit, weapon.",
    )
    file_name: str | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class ContentSafetyScanRequest(BaseModel):
    device_id: str
    enabled: bool
    items: list[ContentItem]


class ContentSafetyFinding(BaseModel):
    item_id: str
    content_type: str
    category: str
    severity: Severity
    confidence: float = Field(ge=0, le=1)
    explanation: str
    recommended_action: str


class ContentSafetyScanResponse(BaseModel):
    device_id: str
    enabled: bool
    scanned_items: int
    alert: bool
    highest_severity: Severity
    findings: list[ContentSafetyFinding]
    privacy_note: str


class DownloadDecision(StrEnum):
    allow = "allow"
    warn = "warn"
    block = "block"


class DownloadGuardPolicy(BaseModel):
    enabled: bool = True
    adult_content_action: DownloadDecision = DownloadDecision.block
    block_unknown_sources: bool = False


class DownloadGuardRequest(BaseModel):
    device_id: str
    url: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    source_app: str | None = None
    media_labels: list[str] = Field(default_factory=list)
    policy: DownloadGuardPolicy = Field(default_factory=DownloadGuardPolicy)


class DownloadGuardResponse(BaseModel):
    device_id: str
    enabled: bool
    decision: DownloadDecision
    category: str | None
    severity: Severity
    explanation: str
    recommended_action: str
    privacy_note: str
