from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, Enum, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Severity(StrEnum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class DeviceAppRisk(Base):
    __tablename__ = "device_app_risks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    device_id: Mapped[str] = mapped_column(String(128), index=True)
    package_name: Mapped[str] = mapped_column(String(256), index=True)
    app_name: Mapped[str] = mapped_column(String(256))
    risk_score: Mapped[int] = mapped_column(Integer)
    severity: Mapped[Severity] = mapped_column(Enum(Severity))
    permissions: Mapped[list[str]] = mapped_column(JSON)
    findings: Mapped[list[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ThreatFinding(Base):
    __tablename__ = "threat_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    device_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[Severity] = mapped_column(Enum(Severity), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    title: Mapped[str] = mapped_column(String(256))
    explanation: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

