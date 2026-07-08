from __future__ import annotations

from create_functionality_pdf_manual import build

if __name__ == "__main__":
    build()
    raise SystemExit(0)

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "mobile_privacy_guardian_functionality.pdf"


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, style), leftIndent=14) for item in items],
        bulletType="bullet",
        leftIndent=18,
        bulletFontName="Helvetica",
        bulletFontSize=8,
    )


def add_section(story: list, title: str, body: list[str], styles: dict[str, ParagraphStyle]) -> None:
    story.append(p(title, styles["Heading2"]))
    for paragraph in body:
        story.append(p(paragraph, styles["Body"]))
        story.append(Spacer(1, 0.05 * inch))
    story.append(Spacer(1, 0.12 * inch))


def add_function(
    story: list,
    name: str,
    location: str,
    purpose: str,
    details: list[str],
    outputs: list[str],
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(p(name, styles["Heading3"]))
    data = [
        [p("Location", styles["TableHead"]), p(location, styles["TableBody"])],
        [p("Purpose", styles["TableHead"]), p(purpose, styles["TableBody"])],
    ]
    table = Table(data, colWidths=[1.25 * inch, 5.45 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2F7")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#172033")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.06 * inch))
    story.append(p("What it does", styles["SmallHeading"]))
    story.append(bullets(details, styles["Bullet"]))
    story.append(p("Returns or produces", styles["SmallHeading"]))
    story.append(bullets(outputs, styles["Bullet"]))
    story.append(Spacer(1, 0.14 * inch))


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(0.72 * inch, 0.45 * inch, "Mobile Privacy Guardian - Functionality Document")
    canvas.drawRightString(7.55 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#0F172A"),
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor("#475569"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "Heading1": ParagraphStyle(
            "Heading1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=10,
            spaceAfter=8,
        ),
        "Heading2": ParagraphStyle(
            "Heading2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=16,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=8,
            spaceAfter=6,
        ),
        "Heading3": ParagraphStyle(
            "Heading3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=8,
            spaceAfter=5,
        ),
        "SmallHeading": ParagraphStyle(
            "SmallHeading",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.8,
            leading=11,
            textColor=colors.HexColor("#334155"),
            spaceBefore=5,
            spaceAfter=3,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            textColor=colors.HexColor("#263244"),
            alignment=TA_LEFT,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor("#263244"),
        ),
        "TableHead": ParagraphStyle(
            "TableHead",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#172033"),
        ),
        "TableBody": ParagraphStyle(
            "TableBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#263244"),
        ),
    }

    story: list = []
    story.append(p("Mobile Privacy Guardian", styles["Title"]))
    story.append(
        p(
            "Functionality explanation for the backend, Android app, privacy controls, deployment assets, and tests developed so far.",
            styles["Subtitle"],
        )
    )

    story.append(p("Executive Summary", styles["Heading1"]))
    story.append(
        p(
            "The project is a first deployable slice of a privacy-first Android security assistant. It includes a FastAPI backend with deterministic detection endpoints, privacy guardrails, audit logging foundations, a native Android app scaffold with local scan flows, deployment artifacts, and automated tests.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 0.1 * inch))
    story.append(
        bullets(
            [
                "Backend: implemented FastAPI app, analysis APIs, agent Q&A, privacy controls, API auth, consent checks, rate limiting, and audit helpers.",
                "Android: implemented native scaffold, permission and camera-risk checks, SMS/media scan flows, shared-text scan, history/settings screens, and service scaffolds.",
                "Security posture: privacy-first defaults are in place, while production identity, cloud audit storage, APK sandboxing, OCR isolation, and signed feeds remain planned.",
            ],
            styles["Bullet"],
        )
    )

    story.append(PageBreak())
    story.append(p("Backend API Functionality", styles["Heading1"]))

    backend_functions = [
        (
            "Root Service Status",
            "GET / in app/main.py",
            "Confirms that the backend application is loaded and ready.",
            [
                "Returns the configured app name, app version, and ready status.",
                "Useful as a lightweight smoke test when the API process starts.",
            ],
            ["JSON object with service name, version, and status."],
        ),
        (
            "Health Check",
            "GET /api/v1/health in app/api/v1/health.py",
            "Provides a simple uptime and load-balancer health endpoint.",
            [
                "Returns a stable ok response.",
                "Can be used by Docker, Kubernetes, monitoring, or manual checks.",
            ],
            ["JSON object: status equals ok."],
        ),
        (
            "Permission Risk Analysis",
            "POST /api/v1/analysis/permissions in app/api/v1/analysis.py",
            "Analyzes Android app permissions and special capabilities for privacy risk.",
            [
                "Accepts installed app records with package name, app name, permissions, and special access flags.",
                "Flags dangerous permission groups including camera, microphone, SMS, location, contacts, storage, overlay, accessibility, and unknown installer capabilities.",
                "Raises risk for suspicious combinations such as camera plus microphone, SMS plus overlay, or accessibility plus notification access.",
                "Uses deterministic scoring so results are explainable and testable.",
            ],
            ["Per-app risk entries, severity, score, findings, and recommended actions."],
        ),
        (
            "Message Scam and Fraud Analysis",
            "POST /api/v1/analysis/messages in app/api/v1/analysis.py",
            "Detects suspicious SMS, notification, email, and pasted-message content.",
            [
                "Looks for OTP theft, urgent KYC prompts, parcel delivery lures, bank impersonation, payment pressure, malware install prompts, and dangerous access requests.",
                "Combines social-engineering indicators with risk scoring.",
                "Keeps output explainable by returning the specific findings that contributed to the score.",
            ],
            ["Classification, score, confidence, findings, explanation, and recommended user actions."],
        ),
        (
            "Phishing URL Analysis",
            "POST /api/v1/analysis/urls in app/api/v1/analysis.py",
            "Evaluates URLs for phishing and unsafe-link indicators.",
            [
                "Checks unsafe transport, obfuscated hostnames, suspicious TLDs, shorteners, typosquatting-like patterns, and local threat-feed matches.",
                "Normalizes URL evidence into human-readable findings.",
                "Provides practical advice such as avoiding login, not sharing OTPs, or opening only official domains.",
            ],
            ["URL score, severity, findings, explanation, and recommended actions."],
        ),
        (
            "Sensitive Data Scan",
            "POST /api/v1/analysis/sensitive-data in app/api/v1/analysis.py",
            "Finds sensitive information in text while minimizing exposure.",
            [
                "Detects OTPs, PAN-like IDs, Aadhaar-like IDs, payment cards, CVV values, IFSC codes, API keys, tokens, recovery phrases, and wallet addresses.",
                "Masks detected values before returning them.",
                "Helps users identify accidental privacy leaks before sharing or storing text.",
            ],
            ["Detected sensitive-data categories, masked values, severity, and remediation guidance."],
        ),
        (
            "Malware Indicator Scan",
            "POST /api/v1/analysis/malware in app/api/v1/analysis.py",
            "Detects suspicious app behavior signals without full APK reverse engineering.",
            [
                "Accepts app behavior signals such as accessibility usage, overlay capability, SMS permission, unknown installer source, suspicious package names, and known bad domain contact.",
                "Scores combinations that often appear in banking trojans, fake security updates, spyware, and abusive apps.",
                "Explains which indicators caused the alert.",
            ],
            ["Suspicious app findings, risk score, severity, explanation, and recommended action."],
        ),
        (
            "Content Safety Scan",
            "POST /api/v1/analysis/content-safety in app/api/v1/analysis.py",
            "Runs opt-in safety checks on submitted text or minimized media labels.",
            [
                "Requires an enabled flag before scanning.",
                "Detects concrete indicators for threats, extremist recruitment, child-safety risks, financial crime, dangerous weapon instructions, targeted violence, and adult/nudity labels.",
                "For private media, expects on-device labels instead of raw images or videos.",
                "Supports private Delete or Skip user flows without showing explicit previews.",
            ],
            ["Safety findings, risk score, severity, and private recommendations."],
        ),
        (
            "Download Guard",
            "POST /api/v1/analysis/download-guard in app/api/v1/analysis.py",
            "Evaluates a pending download before the device saves it.",
            [
                "Uses URL, filename, MIME type, source app, media labels, and user policy.",
                "Can block, warn, or allow adult/explicit video downloads based on policy.",
                "Designed to avoid uploading private videos; it uses minimized metadata and labels.",
            ],
            ["Decision, reason, risk score, explanation, and user-facing actions."],
        ),
        (
            "Agent Question Answering",
            "POST /api/v1/agent/ask in app/api/v1/agent.py",
            "Provides an assistant-style security and privacy Q&A foundation.",
            [
                "Classifies whether a question is about a message, URL, or general privacy/security topic.",
                "Runs deterministic detection tools when relevant.",
                "Explains evidence in natural language.",
                "External AI is disabled by default to preserve privacy.",
            ],
            ["Answer text, supporting findings, and recommended next steps."],
        ),
        (
            "Privacy Controls",
            "GET /api/v1/privacy/controls in app/api/v1/privacy.py",
            "Reports the service's privacy posture and safe runtime defaults.",
            [
                "Surfaces whether consent gates, redaction, raw-retention limits, and external AI restrictions are active.",
                "Gives clients and auditors a quick view of privacy controls.",
            ],
            ["Privacy control status model."],
        ),
    ]

    for item in backend_functions:
        add_function(story, item[0], item[1], item[2], item[3], item[4], styles)

    story.append(PageBreak())
    story.append(p("Core Services and Security Guardrails", styles["Heading1"]))

    core_functions = [
        (
            "API Key Authentication",
            "app/core/auth.py",
            "Provides the current service-to-service authentication foundation.",
            [
                "Reads the x-api-key header.",
                "Builds a principal with configured scopes.",
                "Provides a reusable require_scope dependency for protected routes.",
            ],
            ["Authenticated principal or HTTP authentication error."],
        ),
        (
            "Consent Enforcement",
            "app/core/privacy.py",
            "Prevents analysis endpoints from processing user artifacts without explicit consent.",
            [
                "Requires the x-privacy-consent header to be granted.",
                "Applies to analysis and agent routes.",
                "Supports the product's consent-first design principle.",
            ],
            ["Allows request processing or returns a consent error."],
        ),
        (
            "Rate Limiting",
            "app/core/rate_limit.py",
            "Reduces abuse of analysis and agent endpoints.",
            [
                "Uses a sliding-window in-memory limiter.",
                "Keys requests by device ID, API key, or client host.",
                "Enforces the configured requests-per-minute setting.",
            ],
            ["Allows request processing or returns HTTP 429."],
        ),
        (
            "Security Headers Middleware",
            "app/core/middleware.py",
            "Adds browser and API response hardening headers.",
            [
                "Applies response headers when enabled.",
                "Supports safer defaults for production exposure.",
            ],
            ["HTTP responses with security headers."],
        ),
        (
            "Configuration Validation",
            "app/core/config.py",
            "Centralizes runtime settings and production safety checks.",
            [
                "Loads settings from environment variables.",
                "Validates dangerous production combinations.",
                "Controls API prefix, CORS, trusted hosts, auth keys, rate limits, retention, and AI settings.",
            ],
            ["Typed settings object used across the backend."],
        ),
        (
            "Privacy Helpers",
            "app/core/privacy.py",
            "Provides reusable privacy-safe helpers.",
            [
                "Pseudonymizes identifiers such as device IDs.",
                "Redacts sensitive text values.",
                "Builds retention policy metadata.",
            ],
            ["Pseudonymous IDs, redacted text, and retention-policy objects."],
        ),
        (
            "Field Encryptor",
            "app/core/security.py",
            "Provides field encryption helpers for sensitive values.",
            [
                "Normalizes encryption keys.",
                "Encrypts and decrypts text values using symmetric encryption.",
                "Prepares the codebase for encrypted findings and evidence storage.",
            ],
            ["Encrypted tokens and decrypted values."],
        ),
        (
            "Audit Logger",
            "app/services/audit.py",
            "Creates privacy-safe audit events and short local action logs.",
            [
                "Redacts summaries before logging.",
                "Pseudonymizes device IDs.",
                "Adds tamper-evident signatures by chaining against the previous signature.",
                "Rotates local logs when they exceed the configured size.",
            ],
            ["Audit event dictionaries and local short action log entries."],
        ),
        (
            "Threat Intelligence Feed",
            "app/services/threat_intel/feed.py",
            "Provides local known-bad domain lookup support.",
            [
                "Stores threat indicators in memory.",
                "Looks up domains for phishing and malware checks.",
                "Acts as the placeholder for future signed feed ingestion.",
            ],
            ["Threat indicator matches with category and severity."],
        ),
    ]

    for item in core_functions:
        add_function(story, item[0], item[1], item[2], item[3], item[4], styles)

    story.append(PageBreak())
    story.append(p("Android App Functionality", styles["Heading1"]))

    android_functions = [
        (
            "Main Dashboard and Scan UI",
            "android-app/app/src/main/java/com/privacyguardian/mobile/MainActivity.java",
            "Provides the main native Android experience.",
            [
                "Presents scan modes for permissions, messages, URLs, sensitive text, media, downloads, and browser privacy inputs.",
                "Runs local detector logic for immediate user feedback.",
                "Coordinates permission requests for SMS and media access.",
                "Shows findings, scores, explanations, and action suggestions.",
            ],
            ["On-device scan results and user-facing privacy/security recommendations."],
        ),
        (
            "Installed App and Camera Permission Audit",
            "MainActivity.java plus Android package APIs",
            "Finds apps with camera permission and risky companion permissions.",
            [
                "Inventories installed apps where the OS allows it.",
                "Detects CAMERA permission and related sensitive permissions.",
                "Scores risky combinations such as camera plus microphone, SMS, overlays, accessibility, or location.",
                "Links users to Android privacy settings for remediation.",
            ],
            ["App camera-risk list with severity and recommended settings actions."],
        ),
        (
            "SMS Threat Scan",
            "MainActivity.java",
            "Checks recent SMS messages for scams when the user grants permission.",
            [
                "Requests READ_SMS permission.",
                "Reads a limited number of recent messages.",
                "Uses local suspicious-pattern logic to flag OTP, KYC, parcel, bank, and malware-install lures.",
                "Keeps analysis local unless user-approved backend submission is added.",
            ],
            ["Message threat findings and action recommendations."],
        ),
        (
            "Media Privacy Scan",
            "MainActivity.java",
            "Reviews recent images and videos using minimized local signals.",
            [
                "Requests Android media permissions.",
                "Scans recent media metadata/signals.",
                "Uses label-style indicators for adult or nudity review instead of uploading raw media.",
                "Supports private handling guidance such as review, delete, or skip.",
            ],
            ["Private media findings and local action suggestions."],
        ),
        (
            "Shared Text Scanner",
            "ShareScanActivity.java",
            "Lets users send suspicious text from other apps into Privacy Guardian.",
            [
                "Registers for Android SEND intents with text MIME type.",
                "Receives shared messages, links, or copied content.",
                "Passes the text into the app's scan and history flow.",
            ],
            ["A recorded shared-text scan result."],
        ),
        (
            "Scan History",
            "HistoryActivity.java and ScanHistory.java",
            "Stores and displays previous scan actions.",
            [
                "Records user scan actions with short summaries.",
                "Displays past activity in the History screen.",
                "Supports auditability for previous app actions.",
            ],
            ["Local scan history entries."],
        ),
        (
            "Settings",
            "SettingsActivity.java and AppSettings.java",
            "Provides local configuration and preference storage.",
            [
                "Stores app settings locally.",
                "Gives a place to manage user preferences and future privacy toggles.",
            ],
            ["Persisted Android app preferences."],
        ),
        (
            "Notification Monitor Scaffold",
            "NotificationMonitorService.java",
            "Provides the base for future notification protection.",
            [
                "Declares an Android notification listener service.",
                "Requires explicit user permission through Android settings.",
                "Can later support local redaction and notification threat scanning.",
            ],
            ["Service scaffold for notification-based monitoring."],
        ),
        (
            "Realtime Monitor Scaffold",
            "RealtimeMonitorService.java",
            "Provides the base for background protection features.",
            [
                "Defines a service for future realtime scanning and alerts.",
                "Can be expanded to coordinate local detectors, user preferences, and notifications.",
            ],
            ["Background-service scaffold."],
        ),
        (
            "Browser Privacy VPN Scaffold",
            "BrowserPrivacyVpnService.java and BrowserPrivacyFeed.java",
            "Provides the base for future browser/DNS privacy monitoring.",
            [
                "Declares a VPN service requiring Android VPN consent.",
                "Records consent and avoids packet forwarding in the current scaffold to prevent breaking browsing.",
                "Can later support DNS/domain-level privacy checks.",
            ],
            ["Consent-safe VPN scaffold and browser privacy feed structure."],
        ),
        (
            "Boot Receiver",
            "BootReceiver.java",
            "Provides startup integration after device reboot.",
            [
                "Receives BOOT_COMPLETED when permitted.",
                "Can later restart enabled background protection services.",
            ],
            ["Boot event handling scaffold."],
        ),
        (
            "Backend Client",
            "BackendClient.java",
            "Provides Android-side backend communication structure.",
            [
                "Defines client-side support for calling the backend.",
                "Can connect local scan flows to privacy-consented cloud analysis endpoints.",
            ],
            ["Backend request/response integration foundation."],
        ),
    ]

    for item in android_functions:
        add_function(story, item[0], item[1], item[2], item[3], item[4], styles)

    story.append(PageBreak())
    story.append(p("Data Models, Deployment, and Tests", styles["Heading1"]))

    supporting_functions = [
        (
            "API Schemas",
            "app/schemas/*.py",
            "Define validated request and response contracts.",
            [
                "Uses Pydantic models for app permissions, messages, URLs, sensitive data, malware signals, content safety, download guard, privacy status, and agent Q&A.",
                "Keeps API payloads consistent and self-documenting in Swagger.",
            ],
            ["Typed request/response models and generated API documentation."],
        ),
        (
            "Database Models",
            "app/models/security.py and app/db/*.py",
            "Provide the persistence foundation for future stored findings.",
            [
                "Defines security-related SQLAlchemy models.",
                "Configures async database session support.",
                "Current product behavior is mostly deterministic and request-response oriented.",
            ],
            ["Database model definitions and async session dependency."],
        ),
        (
            "Docker Deployment",
            "Dockerfile and docker-compose.yml",
            "Packages and runs the FastAPI backend.",
            [
                "Defines container build steps.",
                "Provides local compose wiring for the service.",
            ],
            ["Containerized backend runtime."],
        ),
        (
            "Kubernetes Deployment",
            "deploy/k8s/*.yaml",
            "Provides cluster deployment manifests.",
            [
                "Includes API deployment, service, and config map.",
                "Supports production-style deployment planning.",
            ],
            ["Kubernetes resources for the API service."],
        ),
        (
            "Monitoring Rules",
            "deploy/monitoring/prometheus-rules.yaml",
            "Adds Prometheus alert/rule foundation.",
            [
                "Provides monitoring configuration for production readiness.",
                "Complements the documented observability architecture.",
            ],
            ["Prometheus rule definitions."],
        ),
        (
            "Automated Tests",
            "tests/*.py",
            "Verify detection logic and API behavior.",
            [
                "Covers health, message analysis, consent enforcement, privacy controls, malware, content safety, download guard, permission risk, phishing, sensitive data masking, fraud detection, and audit logging.",
                "Last observed run showed 22 passing tests and 2 audit setup errors caused by Windows temp/cache permission issues.",
            ],
            ["Regression safety for backend API and detector behavior."],
        ),
        (
            "Architecture and Security Documentation",
            "docs/**/*.md and README.md",
            "Documents the system design, mobile integration, API contracts, deployment approach, threat model, and hardening roadmap.",
            [
                "Explains first-slice implementation boundaries.",
                "Describes future microservice boundaries.",
                "Lists implemented guardrails and production controls still required.",
            ],
            ["Human-readable implementation, architecture, and security guidance."],
        ),
    ]

    for item in supporting_functions:
        add_function(story, item[0], item[1], item[2], item[3], item[4], styles)

    story.append(PageBreak())
    story.append(p("Current Pending Work", styles["Heading1"]))
    story.append(
        bullets(
            [
                "Start and keep the backend running on the expected local port when demoing the API.",
                "Resolve the local Windows temp/cache permission issue that blocks two audit tests from setting up.",
                "Replace API-key auth with production OIDC/OAuth2, short-lived JWTs, refresh rotation, and device attestation.",
                "Move audit logs to append-only production storage with tamper-evident verification.",
                "Add field-level encryption for stored findings and evidence columns.",
                "Add user-controlled export, delete, and retention workflows.",
                "Add signed threat-feed ingestion and feed provenance verification.",
                "Add APK static analysis sandboxing and OCR isolation.",
                "Add SAST, DAST, dependency, container, and IaC scans in CI.",
                "Complete Android offline cache, richer background monitoring, biometric gates, and production-ready browser/DNS protection.",
                "Split the monolithic FastAPI process into services only when scale and team ownership require it.",
            ],
            styles["Bullet"],
        )
    )

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.72 * inch,
        title="Mobile Privacy Guardian Functionality",
        author="Mobile Privacy Guardian",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
