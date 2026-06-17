package com.privacyguardian.mobile;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

final class BrowserPrivacyFeed {
    static final String VERSION = "local-2026-06-17";

    private static final Set<String> TRACKER_DOMAINS = new HashSet<>(Arrays.asList(
        "doubleclick.net",
        "googlesyndication.com",
        "google-analytics.com",
        "facebook.com",
        "facebook.net",
        "scorecardresearch.com",
        "hotjar.com",
        "segment.io",
        "mixpanel.com",
        "appsflyer.com"
    ));

    private static final Set<String> DATA_BROKER_DOMAINS = new HashSet<>(Arrays.asList(
        "spokeo.com",
        "whitepages.com",
        "truecaller.com",
        "peoplefinder.com",
        "beenverified.com",
        "intelius.com",
        "truthfinder.com"
    ));

    private BrowserPrivacyFeed() {}

    static boolean isTrackerDomain(String domain) {
        return matches(domain, TRACKER_DOMAINS) || domain.contains("analytics") || domain.contains("tracker") || domain.contains("pixel") || domain.startsWith("ads.");
    }

    static boolean isDataBrokerDomain(String domain) {
        return matches(domain, DATA_BROKER_DOMAINS) || domain.contains("data-broker") || domain.contains("people-search") || domain.contains("background-check");
    }

    private static boolean matches(String domain, Set<String> entries) {
        for (String entry : entries) {
            if (domain.equals(entry) || domain.endsWith("." + entry)) {
                return true;
            }
        }
        return false;
    }
}
