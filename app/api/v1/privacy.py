from fastapi import APIRouter, Depends

from app.core.auth import require_scope
from app.core.config import settings
from app.core.privacy import build_retention_policy
from app.schemas.privacy import PrivacyControlStatus

router = APIRouter()


@router.get(
    "/controls",
    response_model=PrivacyControlStatus,
    dependencies=[Depends(require_scope("privacy:admin"))],
)
async def privacy_controls() -> PrivacyControlStatus:
    retention = build_retention_policy()
    return PrivacyControlStatus(
        consent_required=settings.require_user_consent,
        raw_artifact_storage=retention.store_raw_artifacts,
        findings_delete_after=retention.findings_delete_after,
        raw_artifacts_delete_after=retention.raw_artifacts_delete_after,
        external_ai_enabled=settings.enable_external_ai,
        guarantees=[
            "Explicit consent is required before cloud analysis.",
            "Raw artifact storage is disabled by default.",
            "Audit events pseudonymize device identifiers.",
            "Sensitive values are redacted before audit logging.",
            "External AI providers are disabled by default.",
        ],
    )
