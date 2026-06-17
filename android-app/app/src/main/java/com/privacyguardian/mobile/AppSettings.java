package com.privacyguardian.mobile;

import android.content.Context;
import android.content.SharedPreferences;

final class AppSettings {
    static final String PREFS = "sentrynet_settings";
    static final String BACKEND_URL = "backend_url";
    static final String SENSITIVITY = "sensitivity";
    static final String VIDEO_FRAMES = "video_frames";
    static final String REALTIME_ENABLED = "realtime_enabled";
    static final String CONTENT_SAFETY = "content_safety";
    static final String DOWNLOAD_BLOCKING = "download_blocking";
    static final String BROWSER_MONITOR = "browser_monitor";
    static final String RETENTION_DAYS = "retention_days";
    static final String PARENTAL_MODE = "parental_mode";

    private AppSettings() {}

    static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    static String backendUrl(Context context) {
        return prefs(context).getString(BACKEND_URL, "");
    }

    static int sensitivity(Context context) {
        return prefs(context).getInt(SENSITIVITY, 55);
    }

    static int videoFrames(Context context) {
        return prefs(context).getInt(VIDEO_FRAMES, 8);
    }

    static int retentionDays(Context context) {
        return prefs(context).getInt(RETENTION_DAYS, 14);
    }

    static boolean realtimeEnabled(Context context) {
        return prefs(context).getBoolean(REALTIME_ENABLED, false);
    }

    static boolean contentSafetyEnabled(Context context) {
        return prefs(context).getBoolean(CONTENT_SAFETY, false);
    }

    static boolean downloadBlockingEnabled(Context context) {
        return prefs(context).getBoolean(DOWNLOAD_BLOCKING, true);
    }

    static boolean browserMonitorEnabled(Context context) {
        return prefs(context).getBoolean(BROWSER_MONITOR, false);
    }
}
