package com.privacyguardian.mobile;

import android.content.Intent;
import android.net.VpnService;

public class BrowserPrivacyVpnService extends VpnService {
    static final String ACTION_ENABLE = "com.privacyguardian.mobile.browser_monitor.ENABLE";
    static final String ACTION_DISABLE = "com.privacyguardian.mobile.browser_monitor.DISABLE";

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String action = intent == null ? "" : intent.getAction();
        if (ACTION_DISABLE.equals(action)) {
            AppSettings.prefs(this).edit().putBoolean(AppSettings.BROWSER_MONITOR, false).apply();
            ScanHistory.append(this, "browser-monitor", "Off", 0, "Browser VPN/DNS monitor consent disabled.");
            stopSelf();
            return START_NOT_STICKY;
        }

        AppSettings.prefs(this).edit().putBoolean(AppSettings.BROWSER_MONITOR, true).apply();
        ScanHistory.append(
            this,
            "browser-monitor",
            "Consent",
            0,
            "Browser VPN/DNS monitor consent recorded. Packet forwarding is disabled in this scaffold to avoid breaking browsing."
        );
        return START_STICKY;
    }
}
