package com.privacyguardian.mobile;

import android.app.Activity;
import android.app.KeyguardManager;
import android.app.role.RoleManager;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.Set;

public class SettingsActivity extends Activity {
    private static final int REQUEST_CALL_SCREENING_ROLE = 50;
    private static final int REQUEST_CONFIRM_BLOCKED_NUMBERS = 51;

    private LinearLayout blockedSection;
    private EditText backendUrl;
    private EditText sensitivity;
    private EditText videoFrames;
    private EditText retentionDays;
    private CheckBox realtime;
    private CheckBox contentSafety;
    private CheckBox downloadBlocking;
    private CheckBox browserMonitor;
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
        browserMonitor = checkbox("Browser VPN/DNS monitor consent", AppSettings.browserMonitorEnabled(this));
        parentalMode = checkbox("Parental/admin mode", AppSettings.prefs(this).getBoolean(AppSettings.PARENTAL_MODE, false));

        root.addView(backendUrl);
        root.addView(sensitivity);
        root.addView(videoFrames);
        root.addView(retentionDays);
        root.addView(realtime);
        root.addView(contentSafety);
        root.addView(downloadBlocking);
        root.addView(browserMonitor);
        root.addView(parentalMode);

        root.addView(button("Save settings", v -> save()));
        root.addView(button("Open notification access", v -> startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))));
        root.addView(button("Clear local history", v -> {
            ScanHistory.clear(this);
            Toast.makeText(this, "History cleared", Toast.LENGTH_SHORT).show();
        }));

        TextView callBlockingTitle = new TextView(this);
        callBlockingTitle.setText("Call protection");
        callBlockingTitle.setTextSize(20);
        callBlockingTitle.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        callBlockingTitle.setPadding(0, 24, 0, 0);
        root.addView(callBlockingTitle);
        root.addView(button("Enable call blocking for flagged numbers", v -> requestCallScreeningRole()));

        blockedSection = new LinearLayout(this);
        blockedSection.setOrientation(LinearLayout.VERTICAL);
        root.addView(blockedSection);
        renderBlockedSummary();

        return scroll;
    }

    private void requestCallScreeningRole() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            RoleManager roleManager = getSystemService(RoleManager.class);
            if (roleManager != null && roleManager.isRoleAvailable(RoleManager.ROLE_CALL_SCREENING)) {
                if (roleManager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING)) {
                    Toast.makeText(this, "Call blocking for flagged numbers is already enabled.", Toast.LENGTH_SHORT).show();
                    return;
                }
                startActivityForResult(roleManager.createRequestRoleIntent(RoleManager.ROLE_CALL_SCREENING), REQUEST_CALL_SCREENING_ROLE);
                return;
            }
        }
        Toast.makeText(this, "This Android version does not support in-app call screening. Check your phone app's spam/caller-ID settings instead.", Toast.LENGTH_LONG).show();
    }

    private void renderBlockedSummary() {
        blockedSection.removeAllViews();
        int count = FlaggedContacts.all(this).size();
        TextView summary = new TextView(this);
        summary.setText(count + " number(s) currently blocked from calling based on message scan results.");
        summary.setPadding(0, 10, 0, 6);
        blockedSection.addView(summary);
        blockedSection.addView(button("Authenticate to manage blocked callers", v -> requestBlockedNumbersAuthentication()));
    }

    private void requestBlockedNumbersAuthentication() {
        KeyguardManager keyguardManager = (KeyguardManager) getSystemService(Context.KEYGUARD_SERVICE);
        if (keyguardManager == null || !keyguardManager.isDeviceSecure()) {
            Toast.makeText(this, "Set a device PIN, pattern, or biometric lock to manage blocked callers securely.", Toast.LENGTH_LONG).show();
            renderBlockedNumbersDetail();
            return;
        }
        Intent confirmIntent = keyguardManager.createConfirmDeviceCredentialIntent(
            "Unlock to manage blocked callers",
            "Authenticate to view or unblock numbers flagged by SentryNet's message scans."
        );
        if (confirmIntent == null) {
            renderBlockedNumbersDetail();
            return;
        }
        startActivityForResult(confirmIntent, REQUEST_CONFIRM_BLOCKED_NUMBERS);
    }

    private void renderBlockedNumbersDetail() {
        blockedSection.removeAllViews();
        Set<String> numbers = FlaggedContacts.all(this);
        if (numbers.isEmpty()) {
            TextView empty = new TextView(this);
            empty.setText("No numbers are currently blocked.");
            blockedSection.addView(empty);
            return;
        }
        for (String number : numbers) {
            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            TextView label = new TextView(this);
            label.setText(number);
            row.addView(label, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
            row.addView(button("Unblock", v -> {
                FlaggedContacts.unflag(this, number);
                renderBlockedNumbersDetail();
            }));
            blockedSection.addView(row);
        }
        blockedSection.addView(button("Clear all blocked numbers", v -> {
            FlaggedContacts.clear(this);
            renderBlockedNumbersDetail();
        }));
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CALL_SCREENING_ROLE) {
            Toast.makeText(
                this,
                resultCode == RESULT_OK ? "Call blocking for flagged numbers enabled." : "Call screening role was not granted.",
                Toast.LENGTH_LONG
            ).show();
        } else if (requestCode == REQUEST_CONFIRM_BLOCKED_NUMBERS) {
            if (resultCode == RESULT_OK) {
                renderBlockedNumbersDetail();
            } else {
                Toast.makeText(this, "Authentication cancelled.", Toast.LENGTH_SHORT).show();
            }
        }
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
            .putBoolean(AppSettings.BROWSER_MONITOR, browserMonitor.isChecked())
            .putBoolean(AppSettings.PARENTAL_MODE, parentalMode.isChecked())
            .apply();

        Intent service = new Intent(this, RealtimeMonitorService.class);
        if (realtime.isChecked()) {
            startService(service);
        } else {
            stopService(service);
        }
        Intent browserService = new Intent(this, BrowserPrivacyVpnService.class);
        browserService.setAction(browserMonitor.isChecked() ? BrowserPrivacyVpnService.ACTION_ENABLE : BrowserPrivacyVpnService.ACTION_DISABLE);
        startService(browserService);
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
