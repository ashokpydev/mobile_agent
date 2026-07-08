import re
import unicodedata

from app.schemas.analysis import (
    ContentItem,
    ContentSafetyFinding,
    ContentSafetyScanRequest,
    ContentSafetyScanResponse,
)
from app.schemas.common import Severity
from app.services.detection.scoring import confidence_from_score, severity_from_score


CONTENT_PATTERNS: list[tuple[str, re.Pattern[str], int, str, str]] = [
    (
        "adult_sexual_content",
        re.compile(r"\b(adult video|porn|pornographic|explicit sexual|nudity|nude video|sexually explicit)\b", re.I),
        55,
        "The content appears to contain adult or sexually explicit material.",
        "Show a private warning, avoid opening in public, and move or delete the file if it should not be on this device.",
    ),
    (
        "explicit_threat",
        re.compile(r"\b(kill|attack|bomb|shoot|stab)\b.{0,60}\b(school|office|station|airport|public|crowd|person|people)\b", re.I),
        85,
        "The content appears to contain an explicit threat toward people or a public place.",
        "Preserve evidence, avoid forwarding it, and report it to the appropriate authority or platform.",
    ),
    (
        "violent_extremism_indicator",
        re.compile(r"\b(join|recruit|pledge|training|martyrdom|manifesto)\b.{0,80}\b(terror|extremist|militant|jihad|insurgent)\b", re.I),
        78,
        "The content contains violent extremist recruitment or propaganda indicators.",
        "Do not share it. Report the item through official safety channels.",
    ),
    (
        "child_safety_risk",
        re.compile(r"\b(child|minor|underage)\b.{0,80}\b(explicit|abuse|exploit|sexual|nude)\b", re.I),
        95,
        "The content may indicate child-safety exploitation risk.",
        "Do not open, copy, or forward it. Report immediately using lawful child-safety reporting channels.",
    ),
    (
        "weapons_or_explosives_instruction",
        re.compile(r"\b(how to make|recipe|instructions|assemble)\b.{0,80}\b(explosive|bomb|detonator|improvised weapon)\b", re.I),
        88,
        "The content appears to include dangerous weapon or explosive instruction indicators.",
        "Do not follow or share the instructions. Report the source if it was sent to you.",
    ),
    (
        "financial_crime",
        re.compile(r"\b(fake id|stolen card|carding|cashout|money mule|launder)\b", re.I),
        72,
        "The content contains financial crime or identity abuse indicators.",
        "Avoid engagement, preserve context, and report the sender or file.",
    ),
    (
        "hate_or_targeted_violence",
        re.compile(r"\b(exterminate|wipe out|violent action against)\b.{0,80}\b(group|community|religion|ethnicity|caste)\b", re.I),
        82,
        "The content may encourage targeted violence against a group.",
        "Do not amplify it. Report through platform or lawful safety channels.",
    ),
]


_ZERO_WIDTH_CODEPOINTS = (0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF)
_ZERO_WIDTH_CHARS = re.compile("[" + "".join(chr(cp) for cp in _ZERO_WIDTH_CODEPOINTS) + "]")
_LEET_TRANSLATION = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})
_SPACED_LETTERS = re.compile(r"\b(?:[A-Za-z][\s.\-_*]){2,}[A-Za-z]\b")


def _normalize_for_matching(text: str) -> str:
    """Produce a second, de-obfuscated copy of text to run patterns against.

    Catches the cheapest common evasions against the keyword patterns below: unicode
    homoglyph/fullwidth tricks (NFKC), zero-width joiners inserted mid-word, basic
    leetspeak substitution, and spelling a keyword out as single letters separated by
    spaces or punctuation (e.g. "n u d e" or "n.u.d.e"). It does not defeat a
    determined adversary or replace a real classifier on image/video/audio content.
    """
    normalized = unicodedata.normalize("NFKC", text)
    normalized = _ZERO_WIDTH_CHARS.sub("", normalized)
    normalized = _SPACED_LETTERS.sub(lambda m: re.sub(r"[\s.\-_*]", "", m.group(0)), normalized)
    normalized = normalized.translate(_LEET_TRANSLATION)
    return normalized


class ContentSafetyDetector:
    """Opt-in detector for concrete harmful or illegal content indicators.

    Image and video support should pass OCR text, captions, audio transcripts, or model labels into
    `ContentItem.text`. The detector intentionally avoids judging broad political opinions.

    This remains keyword/phrase matching, not a real classifier: it is run against both the raw
    text and a de-obfuscated copy (see `_normalize_for_matching`) to resist trivial evasion, but
    it is not a substitute for actual image/video/audio content analysis upstream.
    """

    def scan(self, payload: ContentSafetyScanRequest) -> ContentSafetyScanResponse:
        if not payload.enabled:
            return ContentSafetyScanResponse(
                device_id=payload.device_id,
                enabled=False,
                scanned_items=0,
                alert=False,
                highest_severity=Severity.low,
                findings=[],
                privacy_note="Content safety scanning is off. No items were analyzed.",
            )

        findings: list[ContentSafetyFinding] = []
        for item in payload.items:
            findings.extend(self._scan_item(item))

        highest_score = max((self._score_for_severity(f.severity) for f in findings), default=0)
        return ContentSafetyScanResponse(
            device_id=payload.device_id,
            enabled=True,
            scanned_items=len(payload.items),
            alert=any(f.severity in {Severity.high, Severity.critical} for f in findings),
            highest_severity=severity_from_score(highest_score),
            findings=findings,
            privacy_note=(
                "Only opt-in submitted content was analyzed. Raw content should stay on-device or be "
                "redacted before cloud processing."
            ),
        )

    def _scan_item(self, item: ContentItem) -> list[ContentSafetyFinding]:
        findings: list[ContentSafetyFinding] = []
        searchable_text = " ".join(
            value
            for value in [
                item.text or "",
                item.file_name or "",
                " ".join(item.media_labels),
            ]
            if value
        )
        if not searchable_text:
            return findings

        normalized_text = _normalize_for_matching(searchable_text)

        for category, pattern, score, explanation, action in CONTENT_PATTERNS:
            if pattern.search(searchable_text) or pattern.search(normalized_text):
                findings.append(
                    ContentSafetyFinding(
                        item_id=item.item_id,
                        content_type=item.content_type,
                        category=category,
                        severity=severity_from_score(score),
                        confidence=confidence_from_score(score),
                        explanation=explanation,
                        recommended_action=action,
                    )
                )
        return findings

    @staticmethod
    def _score_for_severity(severity: Severity) -> int:
        return {
            Severity.low: 10,
            Severity.medium: 45,
            Severity.high: 75,
            Severity.critical: 95,
        }[severity]
