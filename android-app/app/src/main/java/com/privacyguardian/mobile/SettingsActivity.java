package com.privacyguardian.mobile;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

public class SettingsActivity extends Activity {
    private EditText backendUrl;
    private EditText sensitivity;
    private EditText videoFrames;
    private EditText retentionDays;
    private CheckBox realtime;
    private CheckBox contentSafety;
    private CheckBox downloadBlocking;
    private CheckBox parentalMode;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle("SentryNet Settings");
        setContentView(buildContent());
    }

    private ScrollView buildContent() {
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(28, 28, 28, 36);
        scroll.addView(root);

        TextView title = new TextView(this);
        title.setText("Scan policies");
        title.setTextSize(24);
        title.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        root.addView(title);

        backendUrl = input("Backend URL", AppSettings.backendUrl(this));
        sensitivity = input("Visual sensitivity 0-100", String.valueOf(AppSettings.sensitivity(this)));
        videoFrames = input("Video frames to sample", String.valueOf(AppSettings.videoFrames(this)));
        retentionDays = input("History retention days", String.valueOf(AppSettings.retentionDays(this)));
        realtime = checkbox("Realtime media monitoring", AppSettings.realtimeEnabled(this));
        contentSafety = checkbox("Content safety enabled", AppSettings.contentSafetyEnabled(this));
        downloadBlocking = checkbox("Download blocking enabled", AppSettings.downloadBlockingEnabled(this));
        parentalMode = checkbox("Parental/admin mode", AppSettings.prefs(this).getBoolean(AppSettings.PARENTAL_MODE, false));

        root.addView(backendUrl);
        root.addView(sensitivity);
        root.addView(videoFrames);
        root.addView(retentionDays);
        root.addView(realtime);
        root.addView(contentSafety);
        root.addView(downloadBlocking);
        root.addView(parentalMode);

        root.addView(button("Save settings", v -> save()));
        root.addView(button("Open notification access", v -> startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))));
        root.addView(button("Clear local history", v -> {
            ScanHistory.clear(this);
            Toast.makeText(this, "History cleared", Toast.LENGTH_SHORT).show();
        }));
        return scroll;
    }

    private EditText input(String hint, String value) {
        EditText editText = new EditText(this);
        editText.setHint(hint);
        editText.setText(value);
        editText.setSingleLine(true);
        return editText;
    }

    private CheckBox checkbox(String label, boolean checked) {
        CheckBox box = new CheckBox(this);
        box.setText(label);
        box.setChecked(checked);
        return box;
    }

    private Button button(String label, android.view.View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(label);
        button.setAllCaps(false);
        button.setOnClickListener(listener);
        return button;
    }

    private void save() {
        AppSettings.prefs(this).edit()
            .putString(AppSettings.BACKEND_URL, backendUrl.getText().toString().trim())
            .putInt(AppSettings.SENSITIVITY, parseInt(sensitivity.getText().toString(), 55, 0, 100))
            .putInt(AppSettings.VIDEO_FRAMES, parseInt(videoFrames.getText().toString(), 8, 1, 30))
            .putInt(AppSettings.RETENTION_DAYS, parseInt(retentionDays.getText().toString(), 14, 1, 365))
            .putBoolean(AppSettings.REALTIME_ENABLED, realtime.isChecked())
            .putBoolean(AppSettings.CONTENT_SAFETY, contentSafety.isChecked())
            .putBoolean(AppSettings.DOWNLOAD_BLOCKING, downloadBlocking.isChecked())
            .putBoolean(AppSettings.PARENTAL_MODE, parentalMode.isChecked())
            .apply();

        Intent service = new Intent(this, RealtimeMonitorService.class);
        if (realtime.isChecked()) {
            startService(service);
        } else {
            stopService(service);
        }
        Toast.makeText(this, "Settings saved", Toast.LENGTH_SHORT).show();
        finish();
    }

    private int parseInt(String value, int fallback, int min, int max) {
        try {
            int parsed = Integer.parseInt(value.trim());
            return Math.max(min, Math.min(max, parsed));
        } catch (Exception ignored) {
            return fallback;
        }
    }
}
