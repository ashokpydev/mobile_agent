from __future__ import annotations

import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "mobile_privacy_guardian_functionality.pdf"
PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT = 54
RIGHT = 54
TOP = 66
BOTTOM = 56
CONTENT_WIDTH = PAGE_WIDTH - LEFT - RIGHT


def clean(text: str) -> str:
    text = text.replace("&", "and")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def escape_pdf(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class PdfWriter:
    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.current: list[str] = []
        self.y = PAGE_HEIGHT - TOP

    def new_page(self) -> None:
        if self.current:
            self.pages.append(self.current)
        self.current = []
        self.y = PAGE_HEIGHT - TOP

    def ensure(self, height: int) -> None:
        if self.y - height < BOTTOM:
            self.new_page()

    def text(self, value: str, size: int = 10, bold: bool = False, indent: int = 0, leading: int | None = None) -> None:
        value = clean(value)
        if not value:
            return
        font = "F2" if bold else "F1"
        leading = leading or int(size * 1.35)
        max_chars = max(24, int((CONTENT_WIDTH - indent) / (size * 0.48)))
        lines = textwrap.wrap(value, width=max_chars)
        self.ensure(len(lines) * leading + 4)
        for line in lines:
            self.current.append(f"BT /{font} {size} Tf {LEFT + indent} {self.y} Td ({escape_pdf(line)}) Tj ET")
            self.y -= leading
        self.y -= 2

    def title(self, value: str) -> None:
        self.ensure(42)
        self.text(value, size=20, bold=True, leading=26)
        self.y -= 8

    def h1(self, value: str) -> None:
        self.ensure(34)
        self.y -= 4
        self.text(value, size=14, bold=True, leading=19)

    def h2(self, value: str) -> None:
        self.ensure(26)
        self.text(value, size=11, bold=True, leading=15)

    def bullet(self, value: str) -> None:
        self.text(f"- {value}", size=9, indent=12, leading=12)

    def function_block(self, name: str, location: str, purpose: str, details: list[str], outputs: list[str]) -> None:
        self.h2(name)
        self.text(f"Location: {location}", size=9, bold=True, leading=12)
        self.text(f"Purpose: {purpose}", size=9, leading=12)
        self.text("What it does:", size=9, bold=True, leading=12)
        for item in details:
            self.bullet(item)
        self.text("Returns or produces:", size=9, bold=True, leading=12)
        for item in outputs:
            self.bullet(item)
        self.y -= 6

    def finish(self) -> None:
        if self.current:
            self.pages.append(self.current)

    def save(self, path: Path) -> None:
        self.finish()
        path.parent.mkdir(parents=True, exist_ok=True)
        objects: list[bytes] = []
        catalog_id = 1
        pages_id = 2
        font_regular_id = 3
        font_bold_id = 4
        first_page_id = 5
        page_ids = []
        content_ids = []
        next_id = first_page_id

        for _ in self.pages:
            page_ids.append(next_id)
            content_ids.append(next_id + 1)
            next_id += 2

        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        kids = " ".join(f"{pid} 0 R" for pid in page_ids)
        objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode())
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

        for page_index, lines in enumerate(self.pages, start=1):
            footer = [
                f"BT /F1 8 Tf 54 32 Td (Mobile Privacy Guardian - Functionality Document) Tj ET",
                f"BT /F1 8 Tf 512 32 Td (Page {page_index}) Tj ET",
            ]
            stream = "\n".join(lines + footer).encode("latin-1", errors="replace")
            page = (
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
                f"/Resources << /Font << /F1 {font_regular_id} 0 R /F2 {font_bold_id} 0 R >> >> "
                f"/Contents {content_ids[page_index - 1]} 0 R >>"
            )
            objects.append(page.encode())
            objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")

        pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for idx, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f"{idx} 0 obj\n".encode())
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")
        xref = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode())
        pdf.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
        )
        path.write_bytes(pdf)


def build() -> None:
    pdf = PdfWriter()
    pdf.title("Mobile Privacy Guardian")
    pdf.text(
        "Functionality explanation for the backend, Android app, privacy controls, deployment assets, and tests developed so far.",
        size=11,
        leading=15,
    )

    pdf.h1("Executive Summary")
    pdf.text(
        "The project is a first deployable slice of a privacy-first Android security assistant. It includes a FastAPI backend with deterministic detection endpoints, privacy guardrails, audit logging foundations, a native Android app scaffold with local scan flows, deployment artifacts, and automated tests.",
        size=10,
        leading=14,
    )
    for item in [
        "Backend: FastAPI app, analysis APIs, agent Q&A, privacy controls, API auth, consent checks, rate limiting, and audit helpers.",
        "Android: native scaffold, permission and camera-risk checks, SMS/media scan flows, shared-text scan, history/settings screens, and service scaffolds.",
        "Security posture: privacy-first defaults are in place, while production identity, cloud audit storage, APK sandboxing, OCR isolation, and signed feeds remain planned.",
    ]:
        pdf.bullet(item)

    pdf.new_page()
    pdf.h1("Backend API Functionality")

    backend_functions = [
        ("Root Service Status", "GET / in app/main.py", "Confirms that the backend application is loaded and ready.", ["Returns configured app name, app version, and ready status.", "Useful as a lightweight smoke test when the API process starts."], ["JSON object with service name, version, and status."]),
        ("Health Check", "GET /api/v1/health in app/api/v1/health.py", "Provides a simple uptime and load-balancer health endpoint.", ["Returns a stable ok response.", "Can be used by Docker, Kubernetes, monitoring, or manual checks."], ["JSON object where status equals ok."]),
        ("Permission Risk Analysis", "POST /api/v1/analysis/permissions in app/api/v1/analysis.py", "Analyzes Android app permissions and special capabilities for privacy risk.", ["Accepts installed app records with package name, app name, permissions, and special access flags.", "Flags dangerous permission groups including camera, microphone, SMS, location, contacts, storage, overlay, accessibility, and unknown installer capabilities.", "Raises risk for suspicious combinations such as camera plus microphone, SMS plus overlay, or accessibility plus notification access.", "Uses deterministic scoring so results are explainable and testable."], ["Per-app risk entries, severity, score, findings, and recommended actions."]),
        ("Message Scam and Fraud Analysis", "POST /api/v1/analysis/messages in app/api/v1/analysis.py", "Detects suspicious SMS, notification, email, and pasted-message content.", ["Looks for OTP theft, urgent KYC prompts, parcel delivery lures, bank impersonation, payment pressure, malware install prompts, and dangerous access requests.", "Combines social-engineering indicators with risk scoring.", "Returns specific findings that contributed to the score."], ["Classification, score, confidence, findings, explanation, and recommended user actions."]),
        ("Phishing URL Analysis", "POST /api/v1/analysis/urls in app/api/v1/analysis.py", "Evaluates URLs for phishing and unsafe-link indicators.", ["Checks unsafe transport, obfuscated hostnames, suspicious TLDs, shorteners, typosquatting-like patterns, and local threat-feed matches.", "Normalizes URL evidence into human-readable findings.", "Provides practical advice such as avoiding login or using official domains only."], ["URL score, severity, findings, explanation, and recommended actions."]),
        ("Sensitive Data Scan", "POST /api/v1/analysis/sensitive-data in app/api/v1/analysis.py", "Finds sensitive information in text while minimizing exposure.", ["Detects OTPs, PAN-like IDs, Aadhaar-like IDs, payment cards, CVV values, IFSC codes, API keys, tokens, recovery phrases, and wallet addresses.", "Masks detected values before returning them.", "Helps users identify accidental privacy leaks before sharing or storing text."], ["Detected sensitive-data categories, masked values, severity, and remediation guidance."]),
        ("Malware Indicator Scan", "POST /api/v1/analysis/malware in app/api/v1/analysis.py", "Detects suspicious app behavior signals without full APK reverse engineering.", ["Accepts app behavior signals such as accessibility usage, overlay capability, SMS permission, unknown installer source, suspicious package names, and known bad domain contact.", "Scores combinations that often appear in banking trojans, fake security updates, spyware, and abusive apps.", "Explains which indicators caused the alert."], ["Suspicious app findings, risk score, severity, explanation, and recommended action."]),
        ("Content Safety Scan", "POST /api/v1/analysis/content-safety in app/api/v1/analysis.py", "Runs opt-in safety checks on submitted text or minimized media labels.", ["Requires an enabled flag before scanning.", "Detects concrete indicators for threats, extremist recruitment, child-safety risks, financial crime, dangerous weapon instructions, targeted violence, and adult/nudity labels.", "For private media, expects on-device labels instead of raw images or videos.", "Supports private Delete or Skip user flows without showing explicit previews."], ["Safety findings, risk score, severity, and private recommendations."]),
        ("Download Guard", "POST /api/v1/analysis/download-guard in app/api/v1/analysis.py", "Evaluates a pending download before the device saves it.", ["Uses URL, filename, MIME type, source app, media labels, and user policy.", "Can block, warn, or allow adult/explicit video downloads based on policy.", "Designed to avoid uploading private videos; it uses minimized metadata and labels."], ["Decision, reason, risk score, explanation, and user-facing actions."]),
        ("Agent Question Answering", "POST /api/v1/agent/ask in app/api/v1/agent.py", "Provides an assistant-style security and privacy Q&A foundation.", ["Classifies whether a question is about a message, URL, or general privacy/security topic.", "Runs deterministic detection tools when relevant.", "Explains evidence in natural language.", "External AI is disabled by default to preserve privacy."], ["Answer text, supporting findings, and recommended next steps."]),
        ("Privacy Controls", "GET /api/v1/privacy/controls in app/api/v1/privacy.py", "Reports the service's privacy posture and safe runtime defaults.", ["Surfaces whether consent gates, redaction, raw-retention limits, and external AI restrictions are active.", "Gives clients and auditors a quick view of privacy controls."], ["Privacy control status model."]),
    ]
    for block in backend_functions:
        pdf.function_block(*block)

    pdf.new_page()
    pdf.h1("Core Services and Security Guardrails")
    core_functions = [
        ("API Key Authentication", "app/core/auth.py", "Provides the current service-to-service authentication foundation.", ["Reads the x-api-key header.", "Builds a principal with configured scopes.", "Provides a reusable require_scope dependency for protected routes."], ["Authenticated principal or HTTP authentication error."]),
        ("Consent Enforcement", "app/core/privacy.py", "Prevents analysis endpoints from processing user artifacts without explicit consent.", ["Requires the x-privacy-consent header to be granted.", "Applies to analysis and agent routes.", "Supports the product's consent-first design principle."], ["Allows request processing or returns a consent error."]),
        ("Rate Limiting", "app/core/rate_limit.py", "Reduces abuse of analysis and agent endpoints.", ["Uses a sliding-window in-memory limiter.", "Keys requests by device ID, API key, or client host.", "Enforces the configured requests-per-minute setting."], ["Allows request processing or returns HTTP 429."]),
        ("Security Headers Middleware", "app/core/middleware.py", "Adds browser and API response hardening headers.", ["Applies response headers when enabled.", "Supports safer defaults for production exposure."], ["HTTP responses with security headers."]),
        ("Configuration Validation", "app/core/config.py", "Centralizes runtime settings and production safety checks.", ["Loads settings from environment variables.", "Validates dangerous production combinations.", "Controls API prefix, CORS, trusted hosts, auth keys, rate limits, retention, and AI settings."], ["Typed settings object used across the backend."]),
        ("Privacy Helpers", "app/core/privacy.py", "Provides reusable privacy-safe helpers.", ["Pseudonymizes identifiers such as device IDs.", "Redacts sensitive text values.", "Builds retention policy metadata."], ["Pseudonymous IDs, redacted text, and retention-policy objects."]),
        ("Field Encryptor", "app/core/security.py", "Provides field encryption helpers for sensitive values.", ["Normalizes encryption keys.", "Encrypts and decrypts text values using symmetric encryption.", "Prepares the codebase for encrypted findings and evidence storage."], ["Encrypted tokens and decrypted values."]),
        ("Audit Logger", "app/services/audit.py", "Creates privacy-safe audit events and short local action logs.", ["Redacts summaries before logging.", "Pseudonymizes device IDs.", "Adds tamper-evident signatures by chaining against the previous signature.", "Rotates local logs when they exceed the configured size."], ["Audit event dictionaries and local short action log entries."]),
        ("Threat Intelligence Feed", "app/services/threat_intel/feed.py", "Provides local known-bad domain lookup support.", ["Stores threat indicators in memory.", "Looks up domains for phishing and malware checks.", "Acts as the placeholder for future signed feed ingestion."], ["Threat indicator matches with category and severity."]),
    ]
    for block in core_functions:
        pdf.function_block(*block)

    pdf.new_page()
    pdf.h1("Android App Functionality")
    android_functions = [
        ("Main Dashboard and Scan UI", "MainActivity.java", "Provides the main native Android experience.", ["Presents scan modes for permissions, messages, URLs, sensitive text, media, downloads, and browser privacy inputs.", "Runs local detector logic for immediate user feedback.", "Coordinates permission requests for SMS and media access.", "Shows findings, scores, explanations, and action suggestions."], ["On-device scan results and user-facing privacy/security recommendations."]),
        ("Installed App and Camera Permission Audit", "MainActivity.java plus Android package APIs", "Finds apps with camera permission and risky companion permissions.", ["Inventories installed apps where the OS allows it.", "Detects CAMERA permission and related sensitive permissions.", "Scores risky combinations such as camera plus microphone, SMS, overlays, accessibility, or location.", "Links users to Android privacy settings for remediation."], ["App camera-risk list with severity and recommended settings actions."]),
        ("SMS Threat Scan", "MainActivity.java", "Checks recent SMS messages for scams when the user grants permission.", ["Requests READ_SMS permission.", "Reads a limited number of recent messages.", "Uses local suspicious-pattern logic to flag OTP, KYC, parcel, bank, and malware-install lures.", "Keeps analysis local unless user-approved backend submission is added."], ["Message threat findings and action recommendations."]),
        ("Media Privacy Scan", "MainActivity.java", "Reviews recent images and videos using minimized local signals.", ["Requests Android media permissions.", "Scans recent media metadata/signals.", "Uses label-style indicators for adult or nudity review instead of uploading raw media.", "Supports private handling guidance such as review, delete, or skip."], ["Private media findings and local action suggestions."]),
        ("Shared Text Scanner", "ShareScanActivity.java", "Lets users send suspicious text from other apps into Privacy Guardian.", ["Registers for Android SEND intents with text MIME type.", "Receives shared messages, links, or copied content.", "Passes the text into the app's scan and history flow."], ["A recorded shared-text scan result."]),
        ("Scan History", "HistoryActivity.java and ScanHistory.java", "Stores and displays previous scan actions.", ["Records user scan actions with short summaries.", "Displays past activity in the History screen.", "Supports auditability for previous app actions."], ["Local scan history entries."]),
        ("Settings", "SettingsActivity.java and AppSettings.java", "Provides local configuration and preference storage.", ["Stores app settings locally.", "Gives a place to manage user preferences and future privacy toggles."], ["Persisted Android app preferences."]),
        ("Notification Monitor Scaffold", "NotificationMonitorService.java", "Provides the base for future notification protection.", ["Declares an Android notification listener service.", "Requires explicit user permission through Android settings.", "Can later support local redaction and notification threat scanning."], ["Service scaffold for notification-based monitoring."]),
        ("Realtime Monitor Scaffold", "RealtimeMonitorService.java", "Provides the base for background protection features.", ["Defines a service for future realtime scanning and alerts.", "Can be expanded to coordinate local detectors, user preferences, and notifications."], ["Background-service scaffold."]),
        ("Browser Privacy VPN Scaffold", "BrowserPrivacyVpnService.java and BrowserPrivacyFeed.java", "Provides the base for future browser/DNS privacy monitoring.", ["Declares a VPN service requiring Android VPN consent.", "Records consent and avoids packet forwarding in the current scaffold to prevent breaking browsing.", "Can later support DNS/domain-level privacy checks."], ["Consent-safe VPN scaffold and browser privacy feed structure."]),
        ("Boot Receiver", "BootReceiver.java", "Provides startup integration after device reboot.", ["Receives BOOT_COMPLETED when permitted.", "Can later restart enabled background protection services."], ["Boot event handling scaffold."]),
        ("Backend Client", "BackendClient.java", "Provides Android-side backend communication structure.", ["Defines client-side support for calling the backend.", "Can connect local scan flows to privacy-consented cloud analysis endpoints."], ["Backend request/response integration foundation."]),
    ]
    for block in android_functions:
        pdf.function_block(*block)

    pdf.new_page()
    pdf.h1("Data Models, Deployment, and Tests")
    supporting_functions = [
        ("API Schemas", "app/schemas/*.py", "Define validated request and response contracts.", ["Uses Pydantic models for app permissions, messages, URLs, sensitive data, malware signals, content safety, download guard, privacy status, and agent Q&A.", "Keeps API payloads consistent and self-documenting in Swagger."], ["Typed request/response models and generated API documentation."]),
        ("Database Models", "app/models/security.py and app/db/*.py", "Provide the persistence foundation for future stored findings.", ["Defines security-related SQLAlchemy models.", "Configures async database session support.", "Current product behavior is mostly deterministic and request-response oriented."], ["Database model definitions and async session dependency."]),
        ("Docker Deployment", "Dockerfile and docker-compose.yml", "Packages and runs the FastAPI backend.", ["Defines container build steps.", "Provides local compose wiring for the service."], ["Containerized backend runtime."]),
        ("Kubernetes Deployment", "deploy/k8s/*.yaml", "Provides cluster deployment manifests.", ["Includes API deployment, service, and config map.", "Supports production-style deployment planning."], ["Kubernetes resources for the API service."]),
        ("Monitoring Rules", "deploy/monitoring/prometheus-rules.yaml", "Adds Prometheus alert/rule foundation.", ["Provides monitoring configuration for production readiness.", "Complements the documented observability architecture."], ["Prometheus rule definitions."]),
        ("Automated Tests", "tests/*.py", "Verify detection logic and API behavior.", ["Covers health, message analysis, consent enforcement, privacy controls, malware, content safety, download guard, permission risk, phishing, sensitive data masking, fraud detection, and audit logging.", "Last observed run showed 22 passing tests and 2 audit setup errors caused by Windows temp/cache permission issues."], ["Regression safety for backend API and detector behavior."]),
        ("Architecture and Security Documentation", "docs/**/*.md and README.md", "Documents the system design, mobile integration, API contracts, deployment approach, threat model, and hardening roadmap.", ["Explains first-slice implementation boundaries.", "Describes future microservice boundaries.", "Lists implemented guardrails and production controls still required."], ["Human-readable implementation, architecture, and security guidance."]),
    ]
    for block in supporting_functions:
        pdf.function_block(*block)

    pdf.new_page()
    pdf.h1("Current Pending Work")
    for item in [
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
    ]:
        pdf.bullet(item)

    pdf.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
