import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Header, HTTPException, status

from app.core.config import settings


SENSITIVE_PATTERNS = [
    re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    re.compile(r"\b(?:api[_-]?key|token|secret)[\w\s:=.-]{0,20}[A-Za-z0-9_\-]{16,}\b", re.I),
]


@dataclass(frozen=True)
class RetentionPolicy:
    findings_delete_after: datetime
    raw_artifacts_delete_after: datetime
    store_raw_artifacts: bool


def pseudonymize(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def redact_text(value: str) -> str:
    redacted = value
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def build_retention_policy() -> RetentionPolicy:
    now = datetime.now(timezone.utc)
    return RetentionPolicy(
        findings_delete_after=now + timedelta(days=settings.default_retention_days),
        raw_artifacts_delete_after=now + timedelta(hours=settings.raw_artifact_retention_hours),
        store_raw_artifacts=settings.raw_artifact_retention_hours > 0,
    )


async def require_privacy_consent(
    x_privacy_consent: str | None = Header(default=None),
) -> None:
    if settings.require_user_consent and x_privacy_consent != "granted":
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="Explicit privacy consent is required for analysis.",
        )

