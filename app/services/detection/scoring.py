from app.schemas.common import Severity


def luhn_check(digits: str) -> bool:
    """Validate a digit string against the Luhn checksum used by real payment cards.

    Any 13-19 digit run matches the card-number pattern, so this filters out phone
    numbers, order IDs, and other incidental digit sequences that aren't actual cards.
    """
    number = [int(d) for d in digits if d.isdigit()]
    if not (13 <= len(number) <= 19):
        return False
    total = 0
    for i, digit in enumerate(reversed(number)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


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

