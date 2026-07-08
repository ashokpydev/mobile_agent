from pathlib import Path

from app.services.detection.sensitive_data import PII_PATTERNS

JAVA_GUARD_PATH = (
    Path(__file__).resolve().parents[1]
    / "android-app"
    / "app"
    / "src"
    / "main"
    / "java"
    / "com"
    / "privacyguardian"
    / "mobile"
    / "SensitiveTextGuard.java"
)

# Maps each server-side PII category to a token that must appear in the on-device Java
# guard, so the two independently-maintained pattern lists can't silently drift apart:
# a category added/removed on one side without the other fails this test.
EXPECTED_JAVA_TOKENS = {
    "otp": "OTP",
    "email": "EMAIL",
    "phone_number": "PHONE",
    "aadhaar_like": "AADHAAR",
    "pan": "PAN",
    "credit_card": "CARD",
    "cvv": "cvv",
    "ifsc": "IFSC",
    "api_key": "api[_-]?key",
    "recovery_phrase": "recovery phrase",
    "crypto_wallet": "CRYPTO_WALLET",
}


def test_every_python_pii_category_has_a_java_counterpart() -> None:
    python_labels = {label for label, *_ in PII_PATTERNS}
    assert python_labels == set(EXPECTED_JAVA_TOKENS), (
        "PII_PATTERNS changed in sensitive_data.py without updating EXPECTED_JAVA_TOKENS "
        "in this test -- add the new category's Java-side token."
    )

    java_source = JAVA_GUARD_PATH.read_text(encoding="utf-8")
    missing = [
        label
        for label, token in EXPECTED_JAVA_TOKENS.items()
        if token not in java_source
    ]
    assert not missing, (
        f"SensitiveTextGuard.java is missing on-device detection for: {missing}. "
        "The Python and Java PII pattern lists must stay in sync."
    )
