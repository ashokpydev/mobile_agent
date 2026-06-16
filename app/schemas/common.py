from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(str, StrEnum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class Classification(str, StrEnum):
    safe = "Safe"
    suspicious = "Suspicious"
    high_risk = "High Risk"
    critical = "Critical"


class Finding(BaseModel):
    category: str
    severity: Severity
    score: int = Field(ge=0, le=100)
    explanation: str
    recommendation: str
    evidence: dict[str, str | int | float | bool | list[str]] = Field(default_factory=dict)

