from datetime import datetime

from pydantic import BaseModel


class PrivacyControlStatus(BaseModel):
    consent_required: bool
    raw_artifact_storage: bool
    findings_delete_after: datetime
    raw_artifacts_delete_after: datetime
    external_ai_enabled: bool
    guarantees: list[str]

