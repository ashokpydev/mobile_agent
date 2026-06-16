from dataclasses import dataclass


@dataclass(frozen=True)
class ThreatIndicator:
    value: str
    category: str
    severity: str
    source: str


class ThreatIntelFeed:
    """In-memory feed adapter; production swaps this for Redis and signed feed updates."""

    def __init__(self) -> None:
        self._indicators = {
            "malicious-example.test": ThreatIndicator(
                value="malicious-example.test",
                category="known_malicious_domain",
                severity="Critical",
                source="local_seed",
            )
        }

    def lookup_domain(self, domain: str) -> ThreatIndicator | None:
        return self._indicators.get(domain.lower())

