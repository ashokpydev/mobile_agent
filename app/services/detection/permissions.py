from app.schemas.analysis import AppPermissionScanRequest, AppPermissionScanResponse, AppRisk, InstalledApp
from app.schemas.common import Finding
from app.services.detection.scoring import clamp_score, severity_from_score


DANGEROUS_PERMISSIONS: dict[str, tuple[int, str]] = {
    "android.permission.CAMERA": (14, "Camera access can capture images or video."),
    "android.permission.RECORD_AUDIO": (18, "Microphone access can capture private conversations."),
    "android.permission.ACCESS_FINE_LOCATION": (18, "Precise location can reveal home, work, and routines."),
    "android.permission.READ_CONTACTS": (12, "Contacts expose your social graph."),
    "android.permission.READ_SMS": (22, "SMS access can expose OTPs and banking messages."),
    "android.permission.SEND_SMS": (20, "SMS sending can trigger fraud or premium-message abuse."),
    "android.permission.READ_CALL_LOG": (16, "Call logs expose sensitive relationship metadata."),
    "android.permission.READ_EXTERNAL_STORAGE": (10, "Storage access can expose documents and photos."),
    "android.permission.MANAGE_EXTERNAL_STORAGE": (20, "All-files access can expose most user documents."),
}

SPECIAL_ACCESS: dict[str, tuple[int, str, str]] = {
    "has_accessibility_service": (
        28,
        "Accessibility service",
        "Accessibility can read screens and automate taps.",
    ),
    "has_notification_access": (
        18,
        "Notification access",
        "Notifications can expose OTPs, chats, and private alerts.",
    ),
    "has_vpn_service": (18, "VPN access", "VPN services can inspect or route network traffic."),
    "can_draw_overlays": (16, "Overlay permission", "Overlays can hide phishing prompts over apps."),
}


class PermissionRiskAnalyzer:
    def scan(self, payload: AppPermissionScanRequest) -> AppPermissionScanResponse:
        risks = [self._analyze_app(app) for app in payload.apps]
        risky_apps = [risk for risk in risks if risk.risk_score >= 25]
        average_risk = int(sum(r.risk_score for r in risks) / max(len(risks), 1))
        privacy_score = clamp_score(100 - average_risk)
        return AppPermissionScanResponse(
            device_id=payload.device_id,
            privacy_score=privacy_score,
            risky_apps=sorted(risky_apps, key=lambda risk: risk.risk_score, reverse=True),
        )

    def _analyze_app(self, app: InstalledApp) -> AppRisk:
        score = 0
        findings: list[Finding] = []
        recommendations: list[str] = []

        for permission in app.permissions:
            if permission in DANGEROUS_PERMISSIONS:
                weight, explanation = DANGEROUS_PERMISSIONS[permission]
                score += weight
                recommendation = f"Review and revoke {permission} if {app.app_name} does not need it."
                findings.append(
                    Finding(
                        category="dangerous_permission",
                        severity=severity_from_score(weight * 4),
                        score=clamp_score(weight * 4),
                        explanation=explanation,
                        recommendation=recommendation,
                        evidence={"permission": permission},
                    )
                )
                recommendations.append(recommendation)

        for attr, (weight, label, explanation) in SPECIAL_ACCESS.items():
            if getattr(app, attr):
                score += weight
                recommendation = f"Disable {label.lower()} for {app.app_name} unless it is essential."
                findings.append(
                    Finding(
                        category="special_access",
                        severity=severity_from_score(weight * 3),
                        score=clamp_score(weight * 3),
                        explanation=explanation,
                        recommendation=recommendation,
                        evidence={"access": label},
                    )
                )
                recommendations.append(recommendation)

        if len(app.permissions) >= 12:
            score += 12
            recommendations.append(f"Audit {app.app_name}; it requests an unusually broad permission set.")

        score = clamp_score(score)
        return AppRisk(
            package_name=app.package_name,
            app_name=app.app_name,
            risk_score=score,
            severity=severity_from_score(score),
            findings=findings,
            recommendations=list(dict.fromkeys(recommendations)),
        )

