import re

from app.schemas.analysis import (
    SensitiveDataFinding,
    SensitiveDataScanRequest,
    SensitiveDataScanResponse,
)
from app.schemas.common import Severity
from app.services.detection.scoring import clamp_score


PII_PATTERNS: list[tuple[str, str, Severity, str]] = [
    ("otp", r"\b(?:otp|one[-\s]?time password|verification code)\s*(?:is|:|=)?\s*\d{4,8}\b", Severity.critical, "Never share OTPs unless you initiated the action and authenticated the request."),
    ("email", r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", Severity.medium, "Share email addresses only with trusted, authenticated services."),
    ("phone_number", r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{10}|\d{5}[-.\s]\d{5})\b", Severity.medium, "Avoid sharing phone numbers without user confirmation."),
    ("aadhaar_like", r"\b\d{4}\s?\d{4}\s?\d{4}\b", Severity.high, "Move Aadhaar-like identifiers to a secure vault."),
    ("pan", r"\b[A-Z]{5}\d{4}[A-Z]\b", Severity.high, "Avoid storing PAN numbers in plain text."),
    ("credit_card", r"\b(?:\d[ -]*?){13,19}\b", Severity.critical, "Remove exposed payment-card data immediately."),
    ("cvv", r"\bCVV\s*[:=]?\s*\d{3,4}\b", Severity.critical, "Delete CVV values; they should never be stored."),
    ("ifsc", r"\b[A-Z]{4}0[A-Z0-9]{6}\b", Severity.medium, "Keep banking metadata in encrypted storage."),
    ("api_key", r"\b(?:api[_-]?key|token|secret)[\w\s:=.-]{0,20}([A-Za-z0-9_\-]{20,})\b", Severity.critical, "Rotate exposed API keys or tokens."),
    ("recovery_phrase", r"\b(?:seed phrase|recovery phrase)\b.{0,80}\b(\w+\s+){11,23}\w+\b", Severity.critical, "Move recovery phrases offline and rotate wallets if exposed."),
    ("crypto_wallet", r"\b(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b", Severity.medium, "Avoid sharing wallet addresses with private recovery material."),
]

SEVERITY_WEIGHT = {
    Severity.low: 10,
    Severity.medium: 20,
    Severity.high: 34,
    Severity.critical: 50,
}


class SensitiveDataDetector:
    def scan(self, payload: SensitiveDataScanRequest) -> SensitiveDataScanResponse:
        findings: list[SensitiveDataFinding] = []
        for label, pattern, severity, recommendation in PII_PATTERNS:
            for match in re.finditer(pattern, payload.content, flags=re.IGNORECASE | re.DOTALL):
                value = match.group(0)
                findings.append(
                    SensitiveDataFinding(
                        label=label,
                        severity=severity,
                        masked_value=self._mask(value),
                        start=match.start(),
                        end=match.end(),
                        recommendation=recommendation,
                    )
                )

        exposure_score = clamp_score(sum(SEVERITY_WEIGHT[f.severity] for f in findings))
        recommendations = list(dict.fromkeys(f.recommendation for f in findings))
        return SensitiveDataScanResponse(
            source_name=payload.source_name,
            exposure_score=exposure_score,
            findings=findings,
            recommendations=recommendations,
        )

    @staticmethod
    def _mask(value: str) -> str:
        compact = value.strip()
        if len(compact) <= 8:
            return "*" * len(compact)
        return f"{compact[:3]}...{compact[-3:]}"

