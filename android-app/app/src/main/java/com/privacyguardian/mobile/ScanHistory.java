package com.privacyguardian.mobile;

import android.content.Context;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

final class ScanHistory {
    private static final String FILE_NAME = "scan_history.log";

    private ScanHistory() {}

    static void append(Context context, String type, String badge, int score, String summary) {
        String safeSummary = summary == null ? "" : summary.replace('\n', ' ').replace('|', '/');
        String stamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(new Date());
        String line = stamp + " | " + type + " | " + badge + " | score=" + score + " | " + safeSummary + "\n";
        try (FileOutputStream out = context.openFileOutput(FILE_NAME, Context.MODE_APPEND)) {
            out.write(line.getBytes(StandardCharsets.UTF_8));
        } catch (Exception ignored) {
            // History is best-effort and must never block scanning.
        }
    }

    static List<String> read(Context context) {
        List<String> lines = new ArrayList<>();
        File file = new File(context.getFilesDir(), FILE_NAME);
        if (!file.exists()) {
            return lines;
        }
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(0, line);
                if (lines.size() >= 100) {
                    break;
                }
            }
        } catch (Exception ignored) {
            // Ignore corrupt history lines.
        }
        return lines;
    }

    static void clear(Context context) {
        File file = new File(context.getFilesDir(), FILE_NAME);
        if (file.exists()) {
            file.delete();
        }
    }
}
