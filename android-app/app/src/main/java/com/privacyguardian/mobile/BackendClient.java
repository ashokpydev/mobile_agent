package com.privacyguardian.mobile;

import android.content.Context;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

final class BackendClient {
    private BackendClient() {}

    static void sendAuditAsync(Context context, String scanType, String badge, int score, String summary) {
        String backend = AppSettings.backendUrl(context);
        if (backend == null || backend.trim().length() == 0) {
            return;
        }
        new Thread(() -> send(backend.trim(), scanType, badge, score, summary)).start();
    }

    private static void send(String backend, String scanType, String badge, int score, String summary) {
        HttpURLConnection connection = null;
        try {
            URL url = new URL(backend.endsWith("/") ? backend + "api/v1/analysis/local-event" : backend + "/api/v1/analysis/local-event");
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);
            connection.setRequestProperty("content-type", "application/json");
            connection.setDoOutput(true);
            String payload = "{"
                + "\"scan_type\":\"" + escape(scanType) + "\","
                + "\"badge\":\"" + escape(badge) + "\","
                + "\"score\":" + score + ","
                + "\"summary\":\"" + escape(summary) + "\""
                + "}";
            try (OutputStream out = connection.getOutputStream()) {
                out.write(payload.getBytes(StandardCharsets.UTF_8));
            }
            connection.getResponseCode();
        } catch (Exception ignored) {
            // Backend sync is optional and best-effort.
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private static String escape(String value) {
        if (value == null) return "";
        return value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ");
    }
}
