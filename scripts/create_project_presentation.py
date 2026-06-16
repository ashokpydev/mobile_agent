from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


OUT = Path("SentryNet_Project_Presentation.pptx")

SLIDE_W = 13_333_333
SLIDE_H = 7_500_000

COLORS = {
    "bg": "F4F7FA",
    "ink": "0B1726",
    "muted": "516174",
    "line": "CBD5E1",
    "teal": "0D9488",
    "teal_dark": "0F766E",
    "blue": "2563EB",
    "amber": "B45309",
    "red": "B91C1C",
    "green": "166534",
    "panel": "FFFFFF",
    "dark": "071426",
}


def emu(inches: float) -> int:
    return int(inches * 914400)


def tx(text: str) -> str:
    return escape(text)


def shape_id() -> int:
    shape_id.counter += 1
    return shape_id.counter


shape_id.counter = 1


def solid_fill(color: str) -> str:
    return f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'


def line(color: str = "FFFFFF", width: int = 0) -> str:
    if width <= 0:
        return "<a:ln><a:noFill/></a:ln>"
    return f'<a:ln w="{width}">{solid_fill(color)}</a:ln>'


def rect(x: int, y: int, w: int, h: int, color: str, name: str = "Shape", stroke: str | None = None) -> str:
    sid = shape_id()
    ln = line(stroke, 9525) if stroke else line()
    return f"""
      <p:sp>
        <p:nvSpPr><p:cNvPr id="{sid}" name="{tx(name)}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
          <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 9000"/></a:avLst></a:prstGeom>
          {solid_fill(color)}
          {ln}
        </p:spPr>
        <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-US"/></a:p></p:txBody>
      </p:sp>
    """


def text_box(
    x: int,
    y: int,
    w: int,
    h: int,
    text: str,
    size: int = 24,
    color: str = "0B1726",
    bold: bool = False,
    name: str = "Text",
    align: str = "l",
) -> str:
    sid = shape_id()
    b = ' b="1"' if bold else ""
    paras = text.split("\n")
    p_xml = []
    for para in paras:
        p_xml.append(
            f"""
            <a:p>
              <a:pPr algn="{align}"/>
              <a:r><a:rPr lang="en-US" sz="{size * 100}"{b}>{solid_fill(color)}<a:latin typeface="Aptos"/></a:rPr><a:t>{tx(para)}</a:t></a:r>
              <a:endParaRPr lang="en-US" sz="{size * 100}"/>
            </a:p>
            """
        )
    return f"""
      <p:sp>
        <p:nvSpPr><p:cNvPr id="{sid}" name="{tx(name)}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
          {line()}
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0"/>
          <a:lstStyle/>
          {''.join(p_xml)}
        </p:txBody>
      </p:sp>
    """


def bullet_list(x: int, y: int, w: int, h: int, items: list[str], size: int = 18, color: str = "0B1726") -> str:
    sid = shape_id()
    paras = []
    for item in items:
        paras.append(
            f"""
            <a:p>
              <a:pPr marL="285750" indent="-171450">
                <a:buFont typeface="Aptos"/>
                <a:buChar char="&#8226;"/>
              </a:pPr>
              <a:r><a:rPr lang="en-US" sz="{size * 100}">{solid_fill(color)}<a:latin typeface="Aptos"/></a:rPr><a:t>{tx(item)}</a:t></a:r>
              <a:endParaRPr lang="en-US" sz="{size * 100}"/>
            </a:p>
            """
        )
    return f"""
      <p:sp>
        <p:nvSpPr><p:cNvPr id="{sid}" name="Bullets"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
          {line()}
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0"/>
          <a:lstStyle/>
          {''.join(paras)}
        </p:txBody>
      </p:sp>
    """


def header(title: str, subtitle: str = "") -> str:
    return (
        rect(0, 0, SLIDE_W, emu(0.22), COLORS["teal"], "Top Bar")
        + text_box(emu(0.55), emu(0.48), emu(8.8), emu(0.45), title, 28, COLORS["ink"], True, "Title")
        + (
            text_box(emu(0.57), emu(0.95), emu(8.8), emu(0.34), subtitle, 12, COLORS["muted"], False, "Subtitle")
            if subtitle
            else ""
        )
    )


def card(x: float, y: float, w: float, h: float, title: str, body: str, accent: str = "0D9488") -> str:
    return (
        rect(emu(x), emu(y), emu(w), emu(h), COLORS["panel"], "Card", COLORS["line"])
        + rect(emu(x), emu(y), emu(0.08), emu(h), accent, "Accent")
        + text_box(emu(x + 0.22), emu(y + 0.18), emu(w - 0.42), emu(0.28), title, 15, COLORS["ink"], True)
        + text_box(emu(x + 0.22), emu(y + 0.58), emu(w - 0.42), emu(h - 0.7), body, 12, COLORS["muted"])
    )


def flow_node(x: float, y: float, label: str, color: str) -> str:
    return rect(emu(x), emu(y), emu(1.85), emu(0.7), color, "Flow Node") + text_box(
        emu(x + 0.12), emu(y + 0.2), emu(1.6), emu(0.28), label, 13, "FFFFFF", True, align="ctr"
    )


def arrow(x1: float, y1: float, x2: float, y2: float, color: str = "64748B") -> str:
    sid = shape_id()
    return f"""
      <p:cxnSp>
        <p:nvCxnSpPr><p:cNvPr id="{sid}" name="Arrow"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{emu(x1)}" y="{emu(y1)}"/><a:ext cx="{emu(x2 - x1)}" cy="{emu(y2 - y1)}"/></a:xfrm>
          <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
          <a:ln w="25400">{solid_fill(color)}<a:tailEnd type="none"/><a:headEnd type="triangle"/></a:ln>
        </p:spPr>
      </p:cxnSp>
    """


def slide_xml(elements: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr>{solid_fill(COLORS["bg"])}<a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {elements}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def slides() -> list[str]:
    data: list[str] = []
    data.append(
        slide_xml(
            rect(0, 0, SLIDE_W, SLIDE_H, COLORS["dark"], "Dark Background")
            + rect(0, 0, emu(0.26), SLIDE_H, COLORS["teal"], "Brand Rail")
            + text_box(emu(0.85), emu(1.35), emu(8.5), emu(0.7), "SentryNet", 44, "FFFFFF", True, "Deck Title")
            + text_box(
                emu(0.88),
                emu(2.12),
                emu(9.8),
                emu(0.8),
                "Mobile Privacy Guardian Application\nCurrent Progress, Architecture, Technologies, Flow, and Roadmap",
                22,
                "D9E4F2",
            )
            + card(0.9, 4.7, 3.0, 0.95, "Product focus", "Privacy-first Android security assistant", COLORS["teal"])
            + card(4.15, 4.7, 3.0, 0.95, "Current slice", "Native Android app plus FastAPI backend", COLORS["blue"])
            + card(7.4, 4.7, 3.0, 0.95, "Direction", "Local-first detection with cloud-assisted intelligence", COLORS["green"])
            + text_box(emu(0.92), emu(6.85), emu(6), emu(0.28), f"Generated {datetime.now(timezone.utc).date().isoformat()}", 11, "A9B8CA")
        )
    )
    data.append(
        slide_xml(
            header("Executive Summary", "What has been developed so far")
            + card(0.65, 1.45, 3.7, 1.25, "Android application", "SentryNet dashboard with scan modes, settings, history, realtime observer, share intake, and privacy shortcuts.", COLORS["teal"])
            + card(4.8, 1.45, 3.7, 1.25, "Backend service", "FastAPI service for permissions, messages, URLs, sensitive data, malware indicators, content safety, download guard, and agent Q&A.", COLORS["blue"])
            + card(8.95, 1.45, 3.7, 1.25, "Security foundation", "Consent-first API guardrails, scoped API keys, rate limiting, redacted audit logging, and zero raw artifact retention posture.", COLORS["green"])
            + bullet_list(
                emu(0.75),
                emu(3.25),
                emu(11.9),
                emu(2.6),
                [
                    "The application is designed as a privacy-first mobile security assistant for Android users.",
                    "Current implementation combines local Android scans with a cloud-ready analysis API.",
                    "Detection coverage includes app permissions, suspicious messages, phishing URLs, sensitive data, malware indicators, harmful content labels, and download decisions.",
                    "The architecture is intentionally modular so the first FastAPI process can later split into dedicated services.",
                ],
                18,
            )
        )
    )
    data.append(
        slide_xml(
            header("Application Purpose", "Why the product exists")
            + text_box(emu(0.75), emu(1.48), emu(11.6), emu(0.55), "SentryNet helps Android users identify privacy and security risks before those risks become account compromise, fraud, or sensitive data exposure.", 22, COLORS["ink"], True)
            + card(0.8, 2.55, 3.55, 1.2, "Privacy risks", "Risky permissions, camera access, overlays, accessibility abuse, notification access, and unknown installers.", COLORS["teal"])
            + card(4.85, 2.55, 3.55, 1.2, "Fraud and phishing", "KYC/OTP scams, suspicious messages, QR/deep links, typosquatting, unsafe transport, and malicious domains.", COLORS["amber"])
            + card(8.9, 2.55, 3.55, 1.2, "Sensitive content", "PAN, Aadhaar-like IDs, payment cards, tokens, recovery phrases, wallet addresses, and adult media labels.", COLORS["red"])
            + bullet_list(
                emu(0.95),
                emu(4.38),
                emu(11.1),
                emu(1.6),
                [
                    "Core principle: analyze locally first and send minimized cloud payloads only with explicit consent.",
                    "Outputs are explainable: scores include findings, evidence, and recommended actions.",
                    "The product competes on trust, not only detection breadth.",
                ],
                17,
            )
        )
    )
    data.append(
        slide_xml(
            header("Current Android App", "Implemented mobile-side capabilities")
            + bullet_list(
                emu(0.8),
                emu(1.48),
                emu(5.65),
                emu(4.65),
                [
                    "Native Android app scaffold installed as Privacy Guardian / SentryNet.",
                    "Dashboard UI with demo scan modes and agent-style recommendations.",
                    "Camera permission audit across installed apps.",
                    "Risk scoring for camera plus microphone, SMS, location, overlays, accessibility, and unknown APK install signals.",
                    "Settings for backend URL, sensitivity, video frame sampling, retention days, realtime monitoring, content safety, download blocking, and parental/admin mode.",
                    "Local scan history and shared text capture.",
                ],
                16,
            )
            + card(7.0, 1.55, 2.55, 1.0, "Realtime", "MediaStore observer records new image/video activity when enabled.", COLORS["blue"])
            + card(9.85, 1.55, 2.55, 1.0, "Privacy settings", "Shortcuts into Android notification and privacy controls.", COLORS["teal"])
            + card(7.0, 3.05, 2.55, 1.0, "Share intake", "Shared text is captured into history for later review.", COLORS["amber"])
            + card(9.85, 3.05, 2.55, 1.0, "Optional sync", "Best-effort backend audit push when configured.", COLORS["green"])
            + text_box(emu(7.15), emu(5.0), emu(4.9), emu(0.7), "Android limitation: normal apps cannot reliably detect every app using the camera at the exact current moment. The app therefore audits camera permission and guides users to Android Privacy Dashboard for live/recent access.", 14, COLORS["muted"])
        )
    )
    data.append(
        slide_xml(
            header("Current Backend", "Implemented cloud/API-side capabilities")
            + card(0.7, 1.42, 3.8, 1.0, "Analysis API", "FastAPI routes under /api/v1 with consent and rate-limit dependencies.", COLORS["blue"])
            + card(4.8, 1.42, 3.8, 1.0, "Detection engines", "Deterministic services for permission, fraud, phishing, PII, malware, content safety, and download guard.", COLORS["teal"])
            + card(8.9, 1.42, 3.8, 1.0, "Agent Q&A", "LangGraph-ready workflow for security questions and evidence-backed recommendations.", COLORS["green"])
            + bullet_list(
                emu(0.85),
                emu(3.05),
                emu(11.45),
                emu(2.75),
                [
                    "Endpoints: /analysis/permissions, /analysis/messages, /analysis/urls, /analysis/sensitive-data, /analysis/malware, /analysis/content-safety, /analysis/download-guard.",
                    "Privacy controls endpoint reports runtime posture: consent requirement, retention, external AI status, and active guarantees.",
                    "Audit logger writes privacy-safe, redacted, pseudonymous, tamper-evident action lines.",
                    "Docker, Kubernetes manifests, Prometheus rules, CI workflow, tests, threat model, and hardening documents are present.",
                ],
                17,
            )
        )
    )
    data.append(
        slide_xml(
            header("Technologies Used", "Current stack and platform choices")
            + card(0.7, 1.35, 2.7, 1.12, "Mobile", "Native Android\nJava\nSDK 35\nMin SDK 26", COLORS["teal"])
            + card(3.75, 1.35, 2.7, 1.12, "API", "Python 3.13\nFastAPI\nUvicorn\nPydantic v2", COLORS["blue"])
            + card(6.8, 1.35, 2.7, 1.12, "Data", "SQLAlchemy\nSQLite local/dev\nPostgreSQL\npgvector target", COLORS["green"])
            + card(9.85, 1.35, 2.7, 1.12, "Security", "API keys\nScoped auth\nConsent headers\nRate limiting", COLORS["red"])
            + card(0.7, 3.15, 2.7, 1.12, "AI/Agent", "LangChain\nLangGraph\nTool workflow\nRedaction rules", COLORS["amber"])
            + card(3.75, 3.15, 2.7, 1.12, "Infra", "Docker\nKubernetes\nRedis target\nPrometheus", COLORS["teal_dark"])
            + card(6.8, 3.15, 2.7, 1.12, "Testing", "Pytest\npytest-asyncio\nRuff\nBandit", COLORS["blue"])
            + card(9.85, 3.15, 2.7, 1.12, "Ops", "CI workflow\nSecurity docs\nHardening plan\nMonitoring rules", COLORS["green"])
        )
    )
    data.append(
        slide_xml(
            header("How It Works", "End-to-end flow")
            + flow_node(0.75, 2.0, "Android collects signal", COLORS["teal"])
            + arrow(2.65, 2.35, 3.25, 2.35)
            + flow_node(3.3, 2.0, "Local scanners score", COLORS["blue"])
            + arrow(5.2, 2.35, 5.8, 2.35)
            + flow_node(5.85, 2.0, "Consent gate", COLORS["amber"])
            + arrow(7.75, 2.35, 8.35, 2.35)
            + flow_node(8.4, 2.0, "FastAPI analysis", COLORS["teal_dark"])
            + arrow(10.3, 2.35, 10.9, 2.35)
            + flow_node(10.95, 2.0, "Findings + actions", COLORS["green"])
            + bullet_list(
                emu(1.0),
                emu(3.75),
                emu(11.2),
                emu(2.3),
                [
                    "Device gathers app permissions, user-submitted text/URLs, media labels, and local scan outcomes.",
                    "Local-first checks produce immediate findings without uploading raw private artifacts.",
                    "When cloud analysis is needed, requests must include explicit privacy consent.",
                    "Backend detectors classify risk, produce evidence, log redacted audit events, and return explainable remediation guidance.",
                ],
                17,
            )
        )
    )
    data.append(
        slide_xml(
            header("Major Key Points", "What differentiates the implementation")
            + bullet_list(
                emu(0.9),
                emu(1.42),
                emu(5.5),
                emu(4.8),
                [
                    "Local-first protection reduces unnecessary cloud exposure.",
                    "Consent is required for artifact analysis endpoints.",
                    "Raw artifacts are not retained by default.",
                    "Risk scoring is explainable with findings and recommendations.",
                    "Mobile-specific signals are handled together instead of separately.",
                    "External AI is policy-controlled and disabled by default.",
                ],
                18,
            )
            + card(7.05, 1.55, 4.8, 1.05, "Trust model", "Users remain in control of scan sources, retention, content safety, and backend sync settings.", COLORS["teal"])
            + card(7.05, 3.0, 4.8, 1.05, "Security model", "Scoped auth, rate limits, privacy consent, redaction, pseudonymous audit IDs, and security headers form the first production guardrail layer.", COLORS["blue"])
            + card(7.05, 4.45, 4.8, 1.05, "Scalability model", "Current single-process API mirrors future microservice boundaries for agent, detection, threat intelligence, notification, and dashboard services.", COLORS["green"])
        )
    )
    data.append(
        slide_xml(
            header("Detection Coverage", "Current scanning domains")
            + card(0.7, 1.35, 3.0, 0.92, "Permissions", "Dangerous Android permissions and risky combinations.", COLORS["teal"])
            + card(3.95, 1.35, 3.0, 0.92, "Fraud Messages", "OTP, KYC, banking, urgency, and social-engineering patterns.", COLORS["amber"])
            + card(7.2, 1.35, 3.0, 0.92, "Phishing URLs", "Obfuscation, suspicious TLDs, typosquatting, and unsafe transport.", COLORS["red"])
            + card(0.7, 2.85, 3.0, 0.92, "Sensitive Data", "PAN, Aadhaar-like IDs, cards, CVV, IFSC, tokens, and wallet addresses.", COLORS["blue"])
            + card(3.95, 2.85, 3.0, 0.92, "Malware Indicators", "Accessibility abuse, overlays, SMS abuse, package signals, malicious contacts.", COLORS["teal_dark"])
            + card(7.2, 2.85, 3.0, 0.92, "Content Safety", "Opt-in concrete harmful/illegal indicators and on-device adult media labels.", COLORS["green"])
            + card(3.1, 4.55, 4.2, 0.92, "Download Guard", "Block, warn, or allow adult/explicit downloads based on minimized metadata and local labels.", COLORS["amber"])
        )
    )
    data.append(
        slide_xml(
            header("Security And Privacy Posture", "Guardrails already represented in code and docs")
            + bullet_list(
                emu(0.85),
                emu(1.45),
                emu(5.65),
                emu(4.8),
                [
                    "Scoped API-key authorization foundation for service/client access.",
                    "x-privacy-consent: granted required on protected analysis routes.",
                    "Per-device or per-client rate limiting to reduce automated abuse.",
                    "Security headers and production configuration validation.",
                    "Pseudonymized audit events with redacted summaries.",
                    "Tamper-evident action log signatures.",
                ],
                17,
            )
            + bullet_list(
                emu(6.95),
                emu(1.45),
                emu(5.65),
                emu(4.8),
                [
                    "Zero raw artifact retention posture by default.",
                    "External AI calls disabled by default and subject to redaction rules.",
                    "Threat model, production hardening checklist, and production security roadmap are documented.",
                    "Kubernetes, Docker, CI, and monitoring assets are prepared for production evolution.",
                    "Private media decisions are designed around labels, not uploading explicit private content.",
                ],
                17,
            )
        )
    )
    data.append(
        slide_xml(
            header("Current Deliverables", "Repository assets available now")
            + card(0.75, 1.4, 3.6, 1.05, "APK artifacts", "Debug APKs are present for Privacy Guardian / SentryNet testing.", COLORS["teal"])
            + card(4.85, 1.4, 3.6, 1.05, "Backend code", "FastAPI app, schemas, detection services, auth, privacy, rate-limit, security middleware, and audit service.", COLORS["blue"])
            + card(8.95, 1.4, 3.6, 1.05, "Documentation", "Architecture, API specification, Android app notes, DB schema, deployment, LangGraph workflow, security docs.", COLORS["green"])
            + bullet_list(
                emu(0.9),
                emu(3.15),
                emu(11.2),
                emu(2.4),
                [
                    "Tests cover API and detection behavior.",
                    "Dockerfile and docker-compose support local service execution.",
                    "Kubernetes manifests define API deployment/service/configmap.",
                    "Prometheus rules and CI workflow prepare the project for operational hardening.",
                ],
                18,
            )
        )
    )
    data.append(
        slide_xml(
            header("Future Development", "Planned product and engineering roadmap")
            + bullet_list(
                emu(0.8),
                emu(1.38),
                emu(5.7),
                emu(4.9),
                [
                    "Add Android collectors for notification events, QR/deep links, files, local SQLite sync, and richer permission snapshots.",
                    "Replace heuristic adapters with trained fraud, phishing, OCR, PII, malware, and media classifiers.",
                    "Add pgvector retrieval over threat intelligence and user-specific security history.",
                    "Implement signed threat-feed ingestion and provenance verification.",
                    "Add notification engine, dashboard trends, and user preference controls.",
                ],
                16,
            )
            + bullet_list(
                emu(6.95),
                emu(1.38),
                emu(5.7),
                emu(4.9),
                [
                    "Move from API keys to OIDC/OAuth2, short-lived JWTs, refresh rotation, and device attestation.",
                    "Use KMS/secret manager, field-level encryption, append-only audit storage, and user-controlled export/delete/retention flows.",
                    "Add APK static analysis sandboxing and OCR isolation.",
                    "Expand CI with SAST, DAST, dependency, container, and IaC scans.",
                    "Introduce mobile biometric gate for vault and sensitive remediation actions.",
                ],
                16,
            )
        )
    )
    data.append(
        slide_xml(
            header("Recommended Next Build Phases", "A practical delivery path")
            + card(0.75, 1.32, 3.75, 1.18, "Phase 1: Stabilize MVP", "Connect Android scan events to supported backend endpoints, tighten UI flows, validate settings/history/realtime behavior, and publish repeatable APK build steps.", COLORS["teal"])
            + card(4.85, 1.32, 3.75, 1.18, "Phase 2: Production API", "Persist findings, add managed auth, retention workflows, encrypted storage, alert delivery, and operational dashboards.", COLORS["blue"])
            + card(8.95, 1.32, 3.75, 1.18, "Phase 3: Intelligence", "Integrate threat feeds, trained detectors, OCR/media pipelines, pgvector retrieval, and evidence-backed AI recommendations.", COLORS["green"])
            + card(2.75, 3.55, 3.75, 1.18, "Phase 4: Enterprise", "Device-owner policies, admin controls, compliance reporting, attestation, signed feed updates, and fleet-level dashboards.", COLORS["amber"])
            + card(6.95, 3.55, 3.75, 1.18, "Phase 5: Scale", "Split microservices, tune worker queues, expand monitoring, add incident response workflows, and formalize release gates.", COLORS["red"])
        )
    )
    data.append(
        slide_xml(
            rect(0, 0, SLIDE_W, SLIDE_H, COLORS["dark"], "Close Background")
            + rect(0, 0, SLIDE_W, emu(0.22), COLORS["teal"], "Top Bar")
            + text_box(emu(0.9), emu(1.25), emu(9.4), emu(0.65), "Summary", 38, "FFFFFF", True)
            + bullet_list(
                emu(1.0),
                emu(2.35),
                emu(10.7),
                emu(2.9),
                [
                    "SentryNet already has a working Android security dashboard and a modular privacy-first FastAPI backend.",
                    "The architecture is built around local-first scanning, consent-gated cloud analysis, explainable findings, and redacted auditability.",
                    "The next investment should focus on connecting mobile events to production API flows, persistence, trained detection, threat intelligence, and stronger identity/security controls.",
                ],
                22,
                "E5EDF6",
            )
            + text_box(emu(1.0), emu(6.1), emu(8.5), emu(0.34), "Mobile Privacy Guardian Application Presentation", 14, "A9B8CA")
        )
    )
    return data


def content_types(slide_count: int) -> str:
    overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  {overrides}
</Types>"""


def rels_root() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""


def presentation_xml(slide_count: int) -> str:
    sld_ids = "\n".join(
        f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{slide_count + 1}"/></p:sldMasterIdLst>
  <p:sldIdLst>{sld_ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle/>
</p:presentation>"""


def presentation_rels(slide_count: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, slide_count + 1)
    ]
    rels.append(
        f'<Relationship Id="rId{slide_count + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    )
    rels.append(
        f'<Relationship Id="rId{slide_count + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {' '.join(rels)}
</Relationships>"""


def slide_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""


def slide_master() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>"""


def slide_master_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""


def slide_layout() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>"""


def slide_layout_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""


def theme() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="SentryNet Theme">
  <a:themeElements>
    <a:clrScheme name="SentryNet">
      <a:dk1><a:srgbClr val="0B1726"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="334155"/></a:dk2><a:lt2><a:srgbClr val="F4F7FA"/></a:lt2>
      <a:accent1><a:srgbClr val="0D9488"/></a:accent1><a:accent2><a:srgbClr val="2563EB"/></a:accent2>
      <a:accent3><a:srgbClr val="166534"/></a:accent3><a:accent4><a:srgbClr val="B45309"/></a:accent4>
      <a:accent5><a:srgbClr val="B91C1C"/></a:accent5><a:accent6><a:srgbClr val="64748B"/></a:accent6>
      <a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="0F766E"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Aptos"><a:majorFont><a:latin typeface="Aptos"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="SentryNet"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
  <a:objectDefaults/><a:extraClrSchemeLst/>
</a:theme>"""


def core_props() -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>SentryNet Project Presentation</dc:title>
  <dc:subject>Mobile Privacy Guardian progress, architecture, technologies, flow, and roadmap</dc:subject>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""


def app_props(slide_count: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{slide_count}</Slides>
  <Notes>0</Notes>
  <HiddenSlides>0</HiddenSlides>
  <ScaleCrop>false</ScaleCrop>
</Properties>"""


def build() -> None:
    shape_id.counter = 1
    slide_parts = slides()
    with ZipFile(OUT, "w", ZIP_DEFLATED) as pptx:
        pptx.writestr("[Content_Types].xml", content_types(len(slide_parts)))
        pptx.writestr("_rels/.rels", rels_root())
        pptx.writestr("docProps/core.xml", core_props())
        pptx.writestr("docProps/app.xml", app_props(len(slide_parts)))
        pptx.writestr("ppt/presentation.xml", presentation_xml(len(slide_parts)))
        pptx.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slide_parts)))
        pptx.writestr("ppt/slideMasters/slideMaster1.xml", slide_master())
        pptx.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels())
        pptx.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout())
        pptx.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels())
        pptx.writestr("ppt/theme/theme1.xml", theme())
        for index, part in enumerate(slide_parts, start=1):
            pptx.writestr(f"ppt/slides/slide{index}.xml", part)
            pptx.writestr(f"ppt/slides/_rels/slide{index}.xml.rels", slide_rels())
    print(f"Created {OUT.resolve()} with {len(slide_parts)} slides")


if __name__ == "__main__":
    build()
