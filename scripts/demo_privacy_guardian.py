from __future__ import annotations

from textwrap import indent


def print_section(title: str, score: int, findings: list[str], actions: list[str]) -> None:
    print(f"\n{title}")
    print("=" * len(title))
    print(f"Risk score: {score}/100")
    print("Findings:")
    print(indent("\n".join(f"- {item}" for item in findings), "  "))
    print("Recommended actions:")
    print(indent("\n".join(f"- {item}" for item in actions), "  "))


def main() -> None:
    print("Mobile Privacy Guardian Agent demo")
    print("Privacy score: 49 | Security score: 44 | Threat score: 92 | Data exposure: 100")

    print_section(
        "Permission intelligence",
        78,
        [
            "Flashlight Pro requests camera, microphone, SMS read access, and overlay permission.",
            "Quick Cleaner has notification and all-files storage access.",
            "Ride Tracker uses precise location in the background.",
        ],
        [
            "Revoke SMS and microphone permissions from Flashlight Pro.",
            "Disable overlay permission for non-essential apps.",
            "Limit location access to while-in-use.",
        ],
    )

    print_section(
        "Fraud message detection",
        92,
        [
            "Urgent KYC and account-blocking pressure detected.",
            "OTP-sharing request detected.",
            "Shortened URL hides the destination.",
        ],
        [
            "Do not click the link or share OTPs.",
            "Verify through the official bank app.",
            "Report and block the sender.",
        ],
    )

    print_section(
        "Phishing URL detection",
        74,
        [
            "Unsafe HTTP URL.",
            "Obfuscation via at-sign pattern.",
            "Bank-like login text points to a different domain.",
        ],
        [
            "Do not open the link.",
            "Type the official domain manually.",
            "Warn the sender their account may be compromised.",
        ],
    )

    print_section(
        "Sensitive data discovery",
        100,
        [
            "PAN-like identifier found.",
            "Aadhaar-like 12-digit identifier found.",
            "Secret key and CVV found in plain text.",
        ],
        [
            "Move identity files to an encrypted vault.",
            "Rotate exposed API keys.",
            "Delete CVV values from stored files.",
        ],
    )

    print_section(
        "Malware app alert",
        96,
        [
            "Bank Security Update uses accessibility, overlay, and SMS access.",
            "The app contacted malicious-example.test.",
            "The app was installed from an unknown source.",
        ],
        [
            "Uninstall Bank Security Update immediately.",
            "Revoke accessibility, overlay, and SMS access before uninstalling if possible.",
            "Change banking passwords from a clean device.",
        ],
    )

    print_section(
        "Opt-in content safety scan",
        85,
        [
            "Feature toggle is ON.",
            "A message contains an explicit threat indicator.",
            "A gallery image is labeled nudity by on-device media analysis.",
            "No broad political or opinion-based labeling is performed.",
        ],
        [
            "Do not forward the content.",
            "Show a private popup with Delete and Skip without explicit thumbnails.",
            "Preserve evidence and report through lawful safety channels.",
            "Keep scanning off unless the user explicitly enables it.",
        ],
    )

    print_section(
        "Adult download guard",
        55,
        [
            "Download Guard is ON.",
            "adult-video.mp4 matched adult or explicit media indicators.",
            "The policy action is block, so the file is not saved.",
        ],
        [
            "Block the download before storage.",
            "Show a private notification without explicit preview.",
            "Allow policy owner to choose block, warn, or allow.",
        ],
    )


if __name__ == "__main__":
    main()
