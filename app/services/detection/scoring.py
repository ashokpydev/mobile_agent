from app.schemas.common import Severity


def clamp_score(score: int) -> int:
    return max(0, min(100, score))


def severity_from_score(score: int) -> Severity:
    if score >= 85:
        return Severity.critical
    if score >= 65:
        return Severity.high
    if score >= 35:
        return Severity.medium
    return Severity.low


def confidence_from_score(score: int) -> float:
    return round(min(0.99, max(0.2, score / 100)), 2)

