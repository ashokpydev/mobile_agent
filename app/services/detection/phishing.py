from urllib.parse import urlparse

from app.schemas.analysis import UrlAnalysisRequest, UrlAnalysisResponse
from app.schemas.common import Finding
from app.services.detection.scoring import clamp_score, confidence_from_score, severity_from_score


SENSITIVE_BRANDS = ("bank", "sbi", "hdfc", "icici", "axis", "paytm", "phonepe", "gov", "income-tax")
SUSPICIOUS_TLDS = (".zip", ".mov", ".click", ".top", ".xyz", ".work")
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "cutt.ly", "is.gd"}


class PhishingDetector:
    def analyze(self, payload: UrlAnalysisRequest) -> UrlAnalysisResponse:
        url = str(payload.url)
        parsed = urlparse(url if "://" in url else f"https://{url}")
        domain = (parsed.hostname or "").lower()
        findings: list[Finding] = []
        score = 0

        def add(category: str, weight: int, explanation: str, recommendation: str) -> None:
            nonlocal score
            score += weight
            findings.append(
                Finding(
                    category=category,
                    severity=severity_from_score(weight * 3),
                    score=clamp_score(weight * 3),
                    explanation=explanation,
                    recommendation=recommendation,
                    evidence={"domain": domain},
                )
            )

        if parsed.scheme != "https":
            add("no_https", 22, "The URL does not use HTTPS.", "Avoid entering credentials on this page.")
        if "@" in url or "%2f" in url.lower() or "%40" in url.lower():
            add("url_obfuscation", 28, "The URL contains obfuscation characters.", "Treat the link as high risk.")
        if domain in SHORTENERS:
            add("shortened_url", 18, "Shortened URLs hide the final destination.", "Expand and inspect it first.")
        if any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS):
            add("suspicious_tld", 14, "The top-level domain is frequently abused.", "Verify the domain owner.")
        if any(brand in domain for brand in SENSITIVE_BRANDS) and "-" in domain:
            add("brand_typosquatting", 26, "The domain resembles a sensitive brand with extra separators.", "Use the official app or manually typed website.")
        if domain.count(".") >= 3:
            add("deep_subdomain", 12, "The URL uses multiple subdomains that may disguise ownership.", "Check the registered root domain.")
        if parsed.port:
            add("nonstandard_port", 10, "The URL uses an explicit port.", "Be cautious with login or payment pages.")

        score = clamp_score(score)
        return UrlAnalysisResponse(
            url=url,
            domain=domain,
            severity=severity_from_score(score),
            risk_score=score,
            confidence=confidence_from_score(score),
            findings=findings,
            recommended_actions=self._actions(score),
        )

    @staticmethod
    def _actions(score: int) -> list[str]:
        if score >= 65:
            return ["Do not open the link.", "Use the official app or type the website manually."]
        if score >= 30:
            return ["Open only after verifying the sender and domain.", "Do not enter credentials."]
        return ["No major phishing indicators detected."]

