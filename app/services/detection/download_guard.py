import re

from app.schemas.analysis import DownloadDecision, DownloadGuardRequest, DownloadGuardResponse
from app.schemas.common import Severity


ADULT_DOWNLOAD_PATTERN = re.compile(
    r"\b(porn|xxx|adult|nudity|nude|explicit|sexually[-_\s]?explicit)\b",
    re.IGNORECASE,
)


class DownloadGuard:
    """Opt-in download policy engine for adult/explicit media restrictions."""

    def evaluate(self, payload: DownloadGuardRequest) -> DownloadGuardResponse:
        if not payload.policy.enabled:
            return DownloadGuardResponse(
                device_id=payload.device_id,
                enabled=False,
                decision=DownloadDecision.allow,
                category=None,
                severity=Severity.low,
                explanation="Download Guard is off, so the download was not inspected.",
                recommended_action="Turn on Download Guard to restrict adult downloads.",
                privacy_note="No download metadata was evaluated while the feature was off.",
            )

        evidence_text = " ".join(
            value
            for value in [
                payload.url or "",
                payload.file_name or "",
                payload.mime_type or "",
                payload.source_app or "",
                " ".join(payload.media_labels),
            ]
            if value
        )
        adult_match = ADULT_DOWNLOAD_PATTERN.search(evidence_text)
        unknown_source = payload.policy.block_unknown_sources and self._is_unknown_source(payload.source_app)

        if adult_match:
            return DownloadGuardResponse(
                device_id=payload.device_id,
                enabled=True,
                decision=payload.policy.adult_content_action,
                category="adult_explicit_download",
                severity=Severity.medium,
                explanation="The download metadata or media labels indicate adult or sexually explicit content.",
                recommended_action=self._action_text(payload.policy.adult_content_action),
                privacy_note="Only metadata and classifier labels were inspected; no explicit preview is shown.",
            )

        if unknown_source:
            return DownloadGuardResponse(
                device_id=payload.device_id,
                enabled=True,
                decision=DownloadDecision.block,
                category="unknown_download_source",
                severity=Severity.medium,
                explanation="The download source is not trusted by the current policy.",
                recommended_action="Block the download or retry from a trusted store or official website.",
                privacy_note="Only source metadata was inspected.",
            )

        return DownloadGuardResponse(
            device_id=payload.device_id,
            enabled=True,
            decision=DownloadDecision.allow,
            category=None,
            severity=Severity.low,
            explanation="No adult download indicators were detected.",
            recommended_action="Allow the download.",
            privacy_note="Only minimized download metadata was inspected.",
        )

    @staticmethod
    def _is_unknown_source(source_app: str | None) -> bool:
        if not source_app:
            return True
        trusted_sources = {"chrome", "play store", "com.android.vending", "files"}
        return source_app.lower() not in trusted_sources

    @staticmethod
    def _action_text(decision: DownloadDecision) -> str:
        if decision == DownloadDecision.block:
            return "Block the download and show a private notification to the user."
        if decision == DownloadDecision.warn:
            return "Warn the user before allowing them to continue."
        return "Allow the download but record a local policy event."
