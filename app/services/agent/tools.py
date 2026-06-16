from app.schemas.analysis import MessageAnalysisRequest, UrlAnalysisRequest
from app.services.detection.fraud import FraudMessageDetector
from app.services.detection.phishing import PhishingDetector


def analyze_message_tool(payload: MessageAnalysisRequest) -> dict:
    result = FraudMessageDetector().analyze(payload)
    return result.model_dump(mode="json")


def analyze_url_tool(payload: UrlAnalysisRequest) -> dict:
    result = PhishingDetector().analyze(payload)
    return result.model_dump(mode="json")

