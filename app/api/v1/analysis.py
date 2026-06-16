from fastapi import APIRouter, Depends

from app.core.auth import Principal, require_scope
from app.core.privacy import require_privacy_consent
from app.core.rate_limit import enforce_rate_limit
from app.schemas.analysis import (
    AppPermissionScanRequest,
    ContentSafetyScanRequest,
    ContentSafetyScanResponse,
    DownloadGuardRequest,
    DownloadGuardResponse,
    AppPermissionScanResponse,
    MessageAnalysisRequest,
    MessageAnalysisResponse,
    MalwareScanRequest,
    MalwareScanResponse,
    SensitiveDataScanRequest,
    SensitiveDataScanResponse,
    UrlAnalysisRequest,
    UrlAnalysisResponse,
)
from app.services.audit import AuditLogger
from app.services.detection.content_safety import ContentSafetyDetector
from app.services.detection.download_guard import DownloadGuard
from app.services.detection.fraud import FraudMessageDetector
from app.services.detection.malware import MalwareIndicatorDetector
from app.services.detection.permissions import PermissionRiskAnalyzer
from app.services.detection.phishing import PhishingDetector
from app.services.detection.sensitive_data import SensitiveDataDetector

router = APIRouter(dependencies=[Depends(enforce_rate_limit), Depends(require_privacy_consent)])
audit_logger = AuditLogger()


@router.post("/permissions", response_model=AppPermissionScanResponse)
async def analyze_permissions(
    payload: AppPermissionScanRequest,
    principal: Principal = Depends(require_scope("analysis:write")),
) -> AppPermissionScanResponse:
    result = PermissionRiskAnalyzer().scan(payload)
    audit_logger.event(
        actor=principal.subject,
        action="analysis.permissions",
        device_id=payload.device_id,
        summary=f"Scanned {len(payload.apps)} apps; risky apps={len(result.risky_apps)}",
    )
    return result


@router.post("/messages", response_model=MessageAnalysisResponse)
async def analyze_message(
    payload: MessageAnalysisRequest,
    principal: Principal = Depends(require_scope("analysis:write")),
) -> MessageAnalysisResponse:
    result = FraudMessageDetector().analyze(payload)
    audit_logger.event(
        actor=principal.subject,
        action="analysis.message",
        device_id=None,
        summary=f"Message source={payload.source}; classification={result.classification}",
    )
    return result


@router.post("/urls", response_model=UrlAnalysisResponse)
async def analyze_url(
    payload: UrlAnalysisRequest,
    principal: Principal = Depends(require_scope("analysis:write")),
) -> UrlAnalysisResponse:
    result = PhishingDetector().analyze(payload)
    audit_logger.event(
        actor=principal.subject,
        action="analysis.url",
        device_id=None,
        summary=f"URL domain={result.domain}; severity={result.severity}",
    )
    return result


@router.post("/sensitive-data", response_model=SensitiveDataScanResponse)
async def scan_sensitive_data(
    payload: SensitiveDataScanRequest,
    principal: Principal = Depends(require_scope("analysis:write")),
) -> SensitiveDataScanResponse:
    result = SensitiveDataDetector().scan(payload)
    audit_logger.event(
        actor=principal.subject,
        action="analysis.sensitive_data",
        device_id=None,
        summary=f"Sensitive scan source={payload.source_name}; findings={len(result.findings)}",
    )
    return result


@router.post("/malware", response_model=MalwareScanResponse)
async def scan_malware_indicators(
    payload: MalwareScanRequest,
    principal: Principal = Depends(require_scope("analysis:write")),
) -> MalwareScanResponse:
    result = MalwareIndicatorDetector().scan(payload)
    audit_logger.event(
        actor=principal.subject,
        action="analysis.malware",
        device_id=payload.device_id,
        summary=f"Malware indicator scan apps={len(payload.apps)} alert={result.malware_alert}",
    )
    return result


@router.post("/content-safety", response_model=ContentSafetyScanResponse)
async def scan_content_safety(
    payload: ContentSafetyScanRequest,
    principal: Principal = Depends(require_scope("analysis:write")),
) -> ContentSafetyScanResponse:
    result = ContentSafetyDetector().scan(payload)
    audit_logger.event(
        actor=principal.subject,
        action="analysis.content_safety",
        device_id=payload.device_id,
        summary=(
            f"Content safety enabled={payload.enabled}; items={len(payload.items)}; "
            f"findings={len(result.findings)}"
        ),
    )
    return result


@router.post("/download-guard", response_model=DownloadGuardResponse)
async def evaluate_download_guard(
    payload: DownloadGuardRequest,
    principal: Principal = Depends(require_scope("analysis:write")),
) -> DownloadGuardResponse:
    result = DownloadGuard().evaluate(payload)
    audit_logger.event(
        actor=principal.subject,
        action="analysis.download_guard",
        device_id=payload.device_id,
        summary=f"Download guard decision={result.decision}; category={result.category}",
    )
    return result
