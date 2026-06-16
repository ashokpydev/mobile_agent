import re

from app.schemas.analysis import MessageAnalysisRequest, MessageAnalysisResponse
from app.schemas.common import Classification, Finding
from app.services.detection.scoring import clamp_score, confidence_from_score, severity_from_score


FRAUD_PATTERNS: list[tuple[str, int, str, str]] = [
    (r"\b(otp|one time password|verification code)\b", 18, "otp_context", "OTP language is often abused in account-takeover scams."),
    (r"\b(kyc|account blocked|suspend(ed)?|verify now)\b", 22, "kyc_pressure", "Urgent account verification language is a common fraud pattern."),
    (r"\b(upi|bank|debit card|credit card|netbanking)\b", 16, "financial_context", "Banking context increases harm if the message is fraudulent."),
    (r"\b(lottery|prize|winner|reward)\b", 18, "prize_scam", "Unexpected prize claims are strongly associated with scams."),
    (r"\b(investment|crypto|guaranteed returns|double your money)\b", 24, "investment_scam", "Guaranteed-return language is a high-risk investment scam signal."),
    (r"\b(remote access|anydesk|teamviewer|support agent)\b", 28, "remote_access", "Remote-support requests can enable device takeover."),
    (r"\b(click|open|login|update|pay)\b.*\b(link|url|http)", 18, "link_pressure", "The message pressures the user to open a link."),
    (r"\b(urgent|immediately|within \d+ minutes|final warning)\b", 14, "urgency", "Artificial urgency is a social engineering indicator."),
]


class FraudMessageDetector:
    def analyze(self, payload: MessageAnalysisRequest) -> MessageAnalysisResponse:
        text = payload.text.lower()
        findings: list[Finding] = []
        score = 0

        for pattern, weight, category, explanation in FRAUD_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                score += weight
                findings.append(
                    Finding(
                        category=category,
                        severity=severity_from_score(weight * 3),
                        score=clamp_score(weight * 3),
                        explanation=explanation,
                        recommendation="Do not tap links or share codes until you verify via an official channel.",
                        evidence={"pattern": category},
                    )
                )

        if re.search(r"https?://|www\.|bit\.ly|tinyurl|t\.co", text):
            score += 18
            findings.append(
                Finding(
                    category="embedded_url",
                    severity=severity_from_score(54),
                    score=54,
                    explanation="Messages containing links can redirect to credential-harvesting pages.",
                    recommendation="Inspect the URL separately before opening it.",
                    evidence={"contains_url": True},
                )
            )

        score = clamp_score(score)
        classification = self._classification(score)
        explanation = self._explain(classification, findings)
        actions = self._actions(classification)
        return MessageAnalysisResponse(
            classification=classification,
            risk_score=score,
            confidence=confidence_from_score(score),
            findings=findings,
            explanation=explanation,
            recommended_actions=actions,
        )

    @staticmethod
    def _classification(score: int) -> Classification:
        if score >= 85:
            return Classification.critical
        if score >= 65:
            return Classification.high_risk
        if score >= 30:
            return Classification.suspicious
        return Classification.safe

    @staticmethod
    def _explain(classification: Classification, findings: list[Finding]) -> str:
        if not findings:
            return "No strong fraud indicators were detected in the supplied content."
        reasons = ", ".join(f.category.replace("_", " ") for f in findings[:3])
        return f"Classified as {classification.value} because it contains {reasons} signals."

    @staticmethod
    def _actions(classification: Classification) -> list[str]:
        if classification in {Classification.critical, Classification.high_risk}:
            return [
                "Do not reply, click links, install apps, or share OTPs.",
                "Contact the organization using its official app, website, or phone number.",
                "Report and block the sender.",
            ]
        if classification == Classification.suspicious:
            return ["Verify the sender independently before taking action.", "Analyze any URLs separately."]
        return ["No immediate action required."]

