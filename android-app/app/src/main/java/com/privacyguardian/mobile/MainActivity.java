package com.privacyguardian.mobile;

import android.Manifest;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.ContentResolver;
import android.content.Context;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.media.MediaMetadataRetriever;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.VpnService;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.MediaStore;
import android.provider.Settings;
import android.provider.OpenableColumns;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Arrays;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MainActivity extends Activity {
    private static final int REQUEST_READ_SMS = 10;
    private static final int REQUEST_READ_MEDIA = 11;
    private static final int REQUEST_PICK_MEDIA = 20;
    private static final int REQUEST_PICK_BROWSER_HISTORY = 21;
    private static final int REQUEST_BROWSER_VPN = 22;
    private static final String BG = "#f3f6fa";
    private static final String PANEL = "#ffffff";
    private static final String INK = "#071426";
    private static final String MUTED = "#4c5f7a";
    private static final String LINE = "#d5deea";
    private static final String ACCENT = "#0d9488";
    private static final String ACCENT_DARK = "#0f766e";
    private static final String WARNING = "#b45309";
    private static final String DANGER = "#b91c1c";
    private static final String SAFE = "#166534";

    private LinearLayout scoreStrip;
    private LinearLayout scanMenu;
    private LinearLayout inputArea;
    private LinearLayout findings;
    private LinearLayout recommendations;
    private TextView resultTitle;
    private TextView resultSummary;
    private TextView resultBadge;
    private EditText currentInput;
    private String activeMode = "permissions";
    private boolean contentSafetyEnabled = false;
    private boolean downloadGuardEnabled = true;
    private boolean browserMonitorEnabled = false;
    private String selectedMediaInfo = "";
    private Uri selectedMediaUri;
    private volatile boolean cancelMediaScan = false;
    private boolean pendingFullDeviceScan = false;
    private List<AppCameraRisk> cameraApps = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle(R.string.app_name);
        setContentView(buildContent());
        loadPolicySettings();
        refreshCameraAudit();
        renderMode("permissions");
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadPolicySettings();
        if (scoreStrip != null) {
            renderScanMenu();
        }
    }

    private void loadPolicySettings() {
        contentSafetyEnabled = AppSettings.contentSafetyEnabled(this);
        downloadGuardEnabled = AppSettings.downloadBlockingEnabled(this);
        browserMonitorEnabled = AppSettings.browserMonitorEnabled(this);
    }

    private View buildContent() {
        ScrollView scrollView = new ScrollView(this);
        scrollView.setFillViewport(true);
        scrollView.setBackgroundColor(Color.parseColor(BG));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(16), dp(18), dp(16), dp(28));
        scrollView.addView(root);

        LinearLayout header = horizontalRow();
        header.setGravity(Gravity.CENTER_VERTICAL);
        root.addView(header, matchWrap());

        ImageView mark = new ImageView(this);
        mark.setImageResource(getResources().getIdentifier("ic_launcher_foreground", "drawable", getPackageName()));
        mark.setScaleType(ImageView.ScaleType.CENTER_CROP);
        mark.setBackground(round("#e8f7ff", "#b9ddf0", 10));
        mark.setPadding(dp(2), dp(2), dp(2), dp(2));
        LinearLayout.LayoutParams markParams = new LinearLayout.LayoutParams(dp(52), dp(52));
        markParams.setMargins(0, 0, dp(12), 0);
        header.addView(mark, markParams);

        LinearLayout titleBlock = new LinearLayout(this);
        titleBlock.setOrientation(LinearLayout.VERTICAL);
        header.addView(titleBlock, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        titleBlock.addView(text("SentryNet", 24, INK, true));
        titleBlock.addView(text("Mobile privacy and threat dashboard", 13, MUTED, false));

        header.addView(outlineButton("Settings", view -> startActivity(new Intent(this, SettingsActivity.class))), new LinearLayout.LayoutParams(dp(92), dp(44)));

        scoreStrip = new LinearLayout(this);
        scoreStrip.setOrientation(LinearLayout.HORIZONTAL);
        HorizontalScrollView scoreScroll = new HorizontalScrollView(this);
        scoreScroll.setHorizontalScrollBarEnabled(false);
        scoreScroll.addView(scoreStrip);
        root.addView(scoreScroll, marginTop(matchWrap(), 18));

        LinearLayout trustGrid = new LinearLayout(this);
        trustGrid.setOrientation(LinearLayout.VERTICAL);
        root.addView(trustGrid, marginTop(matchWrap(), 10));
        LinearLayout trustRowOne = horizontalRow();
        LinearLayout trustRowTwo = horizontalRow();
        trustGrid.addView(trustRowOne, matchWrap());
        trustGrid.addView(trustRowTwo, marginTop(matchWrap(), 10));
        trustRowOne.addView(trustCard("Consent first", "Cloud analysis requires explicit user consent."), weightCell());
        trustRowOne.addView(trustCard("Zero raw retention", "Raw artifacts are not stored by default."), weightCellWithLeft());
        trustRowTwo.addView(trustCard("Local-first", "Core scans run locally in this APK."), weightCell());
        trustRowTwo.addView(trustCard("AI controlled", "External AI is not called by these local scans."), weightCellWithLeft());

        LinearLayout controlPanel = panel();
        root.addView(controlPanel, marginTop(matchWrap(), 16));
        controlPanel.addView(text("Demo scans", 18, INK, true));
        scanMenu = new LinearLayout(this);
        scanMenu.setOrientation(LinearLayout.VERTICAL);
        controlPanel.addView(scanMenu, marginTop(matchWrap(), 10));

        inputArea = new LinearLayout(this);
        inputArea.setOrientation(LinearLayout.VERTICAL);
        controlPanel.addView(inputArea, marginTop(matchWrap(), 12));

        LinearLayout actions = horizontalRow();
        controlPanel.addView(actions, marginTop(matchWrap(), 12));
        actions.addView(primaryButton("Analyze", view -> runCurrentMode()), new LinearLayout.LayoutParams(0, dp(48), 1));
        LinearLayout.LayoutParams resetParams = new LinearLayout.LayoutParams(0, dp(48), 1);
        resetParams.setMargins(dp(10), 0, 0, 0);
        actions.addView(outlineButton("Reset", view -> renderMode(activeMode)), resetParams);

        LinearLayout secondaryActions = horizontalRow();
        controlPanel.addView(secondaryActions, marginTop(matchWrap(), 10));
        secondaryActions.addView(outlineButton("History", view -> startActivity(new Intent(this, HistoryActivity.class))), new LinearLayout.LayoutParams(0, dp(44), 1));
        LinearLayout.LayoutParams realtimeParams = new LinearLayout.LayoutParams(0, dp(44), 1);
        realtimeParams.setMargins(dp(10), 0, 0, 0);
        secondaryActions.addView(outlineButton("Realtime", view -> {
            AppSettings.prefs(this).edit().putBoolean(AppSettings.REALTIME_ENABLED, !AppSettings.realtimeEnabled(this)).apply();
            if (AppSettings.realtimeEnabled(this)) {
                startService(new Intent(this, RealtimeMonitorService.class));
                Toast.makeText(this, "Realtime media observer enabled", Toast.LENGTH_SHORT).show();
            } else {
                stopService(new Intent(this, RealtimeMonitorService.class));
                Toast.makeText(this, "Realtime media observer disabled", Toast.LENGTH_SHORT).show();
            }
        }), realtimeParams);

        LinearLayout deviceActions = horizontalRow();
        controlPanel.addView(deviceActions, marginTop(matchWrap(), 10));
        deviceActions.addView(primaryButton("Full device scan", view -> runFullDeviceScan()), new LinearLayout.LayoutParams(0, dp(44), 1));
        LinearLayout.LayoutParams grantParams = new LinearLayout.LayoutParams(0, dp(44), 1);
        grantParams.setMargins(dp(10), 0, 0, 0);
        deviceActions.addView(outlineButton("Grant permissions", view -> requestAllRuntimePermissions()), grantParams);

        LinearLayout resultPanel = panel();
        root.addView(resultPanel, marginTop(matchWrap(), 16));

        LinearLayout resultHead = horizontalRow();
        resultHead.setGravity(Gravity.CENTER_VERTICAL);
        resultPanel.addView(resultHead);

        LinearLayout resultCopy = new LinearLayout(this);
        resultCopy.setOrientation(LinearLayout.VERTICAL);
        resultHead.addView(resultCopy, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        resultTitle = text("", 19, INK, true);
        resultSummary = text("", 13, MUTED, false);
        resultSummary.setPadding(0, dp(7), dp(10), 0);
        resultCopy.addView(resultTitle);
        resultCopy.addView(resultSummary);

        resultBadge = text("", 13, DANGER, true);
        resultBadge.setGravity(Gravity.CENTER);
        resultHead.addView(resultBadge, new LinearLayout.LayoutParams(dp(96), dp(34)));

        View divider = new View(this);
        divider.setBackgroundColor(Color.parseColor(LINE));
        resultPanel.addView(divider, marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 1), 14));

        findings = new LinearLayout(this);
        findings.setOrientation(LinearLayout.VERTICAL);
        resultPanel.addView(findings, marginTop(matchWrap(), 14));

        resultPanel.addView(text("Agent recommendations", 18, INK, true), marginTop(matchWrap(), 18));
        recommendations = new LinearLayout(this);
        recommendations.setOrientation(LinearLayout.VERTICAL);
        resultPanel.addView(recommendations, marginTop(matchWrap(), 8));

        return scrollView;
    }

    private LinearLayout panel() {
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setBackground(round(PANEL, LINE, 8));
        panel.setPadding(dp(14), dp(14), dp(14), dp(14));
        return panel;
    }

    private void renderMode(String mode) {
        activeMode = mode;
        currentInput = null;
        renderScores(metricsFor(defaultResult(mode)));
        renderScanMenu();
        renderInput(mode);
        renderResult(defaultResult(mode));
    }

    private void runCurrentMode() {
        ScanData result;
        if ("permissions".equals(activeMode)) {
            refreshCameraAudit();
            result = analyzePermissions();
            Toast.makeText(this, "Scanned installed apps for camera permission", Toast.LENGTH_SHORT).show();
        } else if ("message".equals(activeMode)) {
            if (!hasSmsPermission()) {
                requestPermissions(new String[] {Manifest.permission.READ_SMS}, REQUEST_READ_SMS);
                Toast.makeText(this, "Allow SMS permission to scan inbox messages", Toast.LENGTH_LONG).show();
                return;
            }
            String value = readRecentSmsMessages();
            result = analyzeMessage(value);
            Toast.makeText(this, "Scanned recent SMS inbox messages", Toast.LENGTH_SHORT).show();
        } else if ("malware".equals(activeMode)) {
            result = analyzeInstalledAppsForMalware();
            Toast.makeText(this, "Scanned installed apps for risky behavior", Toast.LENGTH_SHORT).show();
        } else {
            String value = currentInput == null ? sampleFor(activeMode) : currentInput.getText().toString();
            result = analyzeTextMode(activeMode, value);
            Toast.makeText(this, "Analysis complete", Toast.LENGTH_SHORT).show();
        }
        showCompletedResult(result);
        if (currentInput != null && !"permissions".equals(activeMode)) {
            currentInput.setText(result.input);
        }
    }

    private void showCompletedResult(ScanData result) {
        renderScores(metricsFor(result));
        renderScanMenu();
        renderResult(result);
        renderInput(activeMode);
        int score = Math.max(result.threatScore, result.exposureScore);
        ScanHistory.append(this, result.title, result.badge, score, result.summary);
        BackendClient.sendAuditAsync(this, result.title, result.badge, score, result.summary);
    }

    private void runFullDeviceScan() {
        pendingFullDeviceScan = true;
        if (!hasSmsPermission() || !hasMediaPermission()) {
            requestAllRuntimePermissions();
            Toast.makeText(this, "Grant permissions, then Full device scan will continue", Toast.LENGTH_LONG).show();
            return;
        }
        pendingFullDeviceScan = false;

        refreshCameraAudit();
        List<Finding> allFindings = new ArrayList<>();
        int maxScore = 0;

        ScanData permissions = analyzePermissions();
        allFindings.add(new Finding("Permission scan", permissions.summary + " Badge: " + permissions.badge + ".", null));
        maxScore = Math.max(maxScore, permissions.threatScore);

        ScanData malware = analyzeInstalledAppsForMalware();
        allFindings.add(new Finding("Installed app scan", malware.summary + " Badge: " + malware.badge + ".", null));
        maxScore = Math.max(maxScore, malware.threatScore);

        if (hasSmsPermission()) {
            ScanData sms = analyzeMessage(readRecentSmsMessages());
            allFindings.add(new Finding("SMS inbox scan", sms.summary + " Badge: " + sms.badge + ".", null));
            maxScore = Math.max(maxScore, sms.threatScore);
        } else {
            allFindings.add(new Finding("SMS inbox blocked", "READ_SMS permission is not granted, so inbox fraud scanning cannot run.", null));
        }

        if (hasMediaPermission()) {
            MediaBatchResult media = scanRecentMediaBatch(6);
            allFindings.addAll(media.findings);
            maxScore = Math.max(maxScore, media.maxScore);
        } else {
            allFindings.add(new Finding("Media scan blocked", "Image/video read permission is not granted, so gallery scanning cannot run.", null));
        }

        String badge = maxScore >= 80 ? "Critical" : maxScore >= 45 ? "High Risk" : maxScore > 0 ? "Review" : "Healthy";
        String color = maxScore >= 45 ? DANGER : SAFE;
        String bg = maxScore >= 80 ? "#fecaca" : maxScore >= 45 ? "#fee2e2" : maxScore > 0 ? "#fef3c7" : "#dcfce7";
        ScanData result = new ScanData(
            "Full device scan",
            "Completed installed-app, SMS, permission, and recent media checks on this device.",
            badge,
            color,
            bg,
            "",
            allFindings,
            Arrays.asList(
                "Open flagged app settings and revoke risky permissions.",
                "Review SMS alerts before clicking links or sharing OTPs.",
                "Review flagged media privately; use Delete or Skip for selected files.",
                "Enable notification access for WhatsApp/Telegram style message monitoring."
            ),
            clamp(80 - maxScore / 4),
            clamp(78 - maxScore / 3),
            clamp(maxScore),
            clamp(74 - maxScore / 4),
            clamp(maxScore / 2)
        );
        showCompletedResult(result);
        Toast.makeText(this, "Full device scan complete", Toast.LENGTH_LONG).show();
    }

    private void requestAllRuntimePermissions() {
        List<String> permissions = new ArrayList<>();
        if (!hasSmsPermission()) {
            permissions.add(Manifest.permission.READ_SMS);
        }
        if (!hasMediaPermission()) {
            if (Build.VERSION.SDK_INT >= 33) {
                permissions.add(Manifest.permission.READ_MEDIA_IMAGES);
                permissions.add(Manifest.permission.READ_MEDIA_VIDEO);
            } else {
                permissions.add(Manifest.permission.READ_EXTERNAL_STORAGE);
            }
        }
        if (permissions.isEmpty()) {
            Toast.makeText(this, "Required runtime permissions are already granted", Toast.LENGTH_SHORT).show();
            return;
        }
        requestPermissions(permissions.toArray(new String[0]), REQUEST_READ_MEDIA);
    }

    private void renderScores(int[] metrics) {
        scoreStrip.removeAllViews();
        scoreStrip.addView(scoreCard("Privacy score", metrics[0], ACCENT));
        scoreStrip.addView(scoreCard("Security score", metrics[1], ACCENT));
        scoreStrip.addView(scoreCard("Threat score", metrics[2], WARNING));
        scoreStrip.addView(scoreCard("Permission score", metrics[3], ACCENT));
        scoreStrip.addView(scoreCard("Data exposure", metrics[4], WARNING));
    }

    private View scoreCard(String label, int value, String color) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(14), dp(14), dp(14), dp(14));
        card.setBackground(round(PANEL, LINE, 8));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(dp(170), dp(112));
        params.setMargins(0, 0, dp(10), 0);
        card.setLayoutParams(params);

        card.addView(text(label, 13, MUTED, true));
        TextView number = text(String.valueOf(value), 31, INK, true);
        number.setPadding(0, dp(8), 0, dp(8));
        card.addView(number);

        LinearLayout track = new LinearLayout(this);
        track.setBackground(round("#e3eaf2", "#e3eaf2", 12));
        card.addView(track, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(7)));
        View fill = new View(this);
        fill.setBackground(round(color, color, 12));
        track.addView(fill, new LinearLayout.LayoutParams(dp(Math.max(16, Math.round(value * 1.25f))), dp(7)));
        return card;
    }

    private View trustCard(String title, String body) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(12), dp(12), dp(12), dp(12));
        card.setBackground(round(PANEL, LINE, 8));
        card.addView(text(title, 14, INK, true));
        TextView copy = text(body, 12, MUTED, false);
        copy.setPadding(0, dp(6), 0, 0);
        card.addView(copy);
        return card;
    }

    private void renderScanMenu() {
        scanMenu.removeAllViews();
        addScanButton("Permission intelligence", "Scan", "permissions");
        addScanButton("Message threats", "Analyze", "message");
        addScanButton("Phishing URL", "Check", "url");
        addScanButton("Sensitive data", "Detect", "data");
        addScanButton("Browser data alert", "Clean", "browser");
        addScanButton("Malware app alert", "Review", "malware");
        addScanButton("Illegal content safety", contentSafetyEnabled ? "On" : "Off", "content");
        addScanButton("Download guard", downloadGuardEnabled ? "Block" : "Allow", "download");
    }

    private void addScanButton(String title, String action, String mode) {
        Button button = new Button(this);
        button.setText(title + "     " + action);
        button.setGravity(Gravity.CENTER_VERTICAL | Gravity.LEFT);
        button.setAllCaps(false);
        button.setTextSize(15);
        button.setTypeface(Typeface.DEFAULT, activeMode.equals(mode) ? Typeface.BOLD : Typeface.NORMAL);
        button.setTextColor(Color.parseColor(activeMode.equals(mode) ? ACCENT_DARK : INK));
        button.setBackground(round(activeMode.equals(mode) ? "#ecfdf5" : PANEL, activeMode.equals(mode) ? ACCENT : LINE, 8));
        button.setPadding(dp(12), 0, dp(12), 0);
        button.setOnClickListener(view -> {
            if ("content".equals(mode) && activeMode.equals("content")) {
                contentSafetyEnabled = !contentSafetyEnabled;
                AppSettings.prefs(this).edit().putBoolean(AppSettings.CONTENT_SAFETY, contentSafetyEnabled).apply();
            } else if ("download".equals(mode) && activeMode.equals("download")) {
                downloadGuardEnabled = !downloadGuardEnabled;
                AppSettings.prefs(this).edit().putBoolean(AppSettings.DOWNLOAD_BLOCKING, downloadGuardEnabled).apply();
            }
            renderMode(mode);
        });
        scanMenu.addView(button, marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(48)), 8));
    }

    private void renderInput(String mode) {
        inputArea.removeAllViews();
        if ("permissions".equals(mode)) {
            LinearLayout row = horizontalRow();
            inputArea.addView(row, matchWrap());
            row.addView(inputChip("Camera apps: " + cameraApps.size()), new LinearLayout.LayoutParams(0, dp(44), 1));
            LinearLayout.LayoutParams riskyParams = new LinearLayout.LayoutParams(0, dp(44), 1);
            riskyParams.setMargins(dp(10), 0, 0, 0);
            row.addView(inputChip("Review: " + highRiskCameraCount()), riskyParams);

            LinearLayout settingsRow = horizontalRow();
            inputArea.addView(settingsRow, marginTop(matchWrap(), 10));
            settingsRow.addView(outlineButton("Privacy", view -> openPrivacySettings()), new LinearLayout.LayoutParams(0, dp(44), 1));
            LinearLayout.LayoutParams cameraParams = new LinearLayout.LayoutParams(0, dp(44), 1);
            cameraParams.setMargins(dp(8), 0, 0, 0);
            settingsRow.addView(outlineButton("Camera", view -> openCameraPermissionManager()), cameraParams);
            LinearLayout.LayoutParams appsParams = new LinearLayout.LayoutParams(0, dp(44), 1);
            appsParams.setMargins(dp(8), 0, 0, 0);
            settingsRow.addView(outlineButton("Apps", view -> openInstalledAppsSettings()), appsParams);
            return;
        }

        currentInput = new EditText(this);
        currentInput.setText(sampleFor(mode));
        currentInput.setTextSize(14);
        currentInput.setTextColor(Color.parseColor(INK));
        currentInput.setHintTextColor(Color.parseColor(MUTED));
        currentInput.setGravity(Gravity.TOP | Gravity.LEFT);
        currentInput.setSingleLine(false);
        currentInput.setMinLines(3);
        currentInput.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        currentInput.setBackground(round(PANEL, LINE, 8));
        currentInput.setPadding(dp(12), dp(10), dp(12), dp(10));
        inputArea.addView(currentInput, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(116)));

        if ("message".equals(mode)) {
            inputArea.addView(primaryButton("Scan recent SMS inbox", view -> runCurrentMode()), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
        }
        if ("data".equals(mode)) {
            inputArea.addView(outlineButton("Paste from clipboard and scan", view -> {
                String clipboard = readClipboardText();
                if (clipboard.length() == 0) {
                    Toast.makeText(this, "Clipboard has no text to scan", Toast.LENGTH_SHORT).show();
                    return;
                }
                currentInput.setText(clipboard);
                ScanData result = analyzeSensitiveData(clipboard);
                renderScores(metricsFor(result));
                renderResult(result);
            }), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
        }
        if ("browser".equals(mode)) {
            inputArea.addView(primaryButton("Import browser history file", view -> pickBrowserHistoryFile()), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
            inputArea.addView(outlineButton("Paste browser data and scan", view -> {
                String clipboard = readClipboardText();
                if (clipboard.length() == 0) {
                    Toast.makeText(this, "Clipboard has no browser data to scan", Toast.LENGTH_SHORT).show();
                    return;
                }
                currentInput.setText(clipboard);
                ScanData result = analyzeBrowserData(clipboard);
                renderScores(metricsFor(result));
                renderResult(result);
            }), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
            inputArea.addView(outlineButton(browserMonitorEnabled ? "Disable VPN/DNS monitor" : "Enable VPN/DNS monitor", view -> toggleBrowserMonitor()), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
            inputArea.addView(outlineButton("Open Chrome data settings", view -> openAppDetails("com.android.chrome")), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
            inputArea.addView(outlineButton("Open Firefox data settings", view -> openAppDetails("org.mozilla.firefox")), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
            inputArea.addView(outlineButton("Open Edge data settings", view -> openAppDetails("com.microsoft.emmx")), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
        }
        if ("malware".equals(mode)) {
            inputArea.addView(primaryButton("Scan installed apps", view -> runCurrentMode()), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
        }
        if ("content".equals(mode)) {
            inputArea.addView(primaryButton(contentSafetyEnabled ? "Turn content safety off" : "Turn content safety on", view -> {
                contentSafetyEnabled = !contentSafetyEnabled;
                AppSettings.prefs(this).edit().putBoolean(AppSettings.CONTENT_SAFETY, contentSafetyEnabled).apply();
                runCurrentMode();
            }), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
            inputArea.addView(outlineButton("Pick image or video", view -> pickMedia()), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
            inputArea.addView(outlineButton("Cancel media scan", view -> {
                cancelMediaScan = true;
                Toast.makeText(this, "Cancel requested", Toast.LENGTH_SHORT).show();
            }), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
        }
        if ("download".equals(mode)) {
            inputArea.addView(primaryButton(downloadGuardEnabled ? "Disable blocking" : "Enable blocking", view -> {
                downloadGuardEnabled = !downloadGuardEnabled;
                AppSettings.prefs(this).edit().putBoolean(AppSettings.DOWNLOAD_BLOCKING, downloadGuardEnabled).apply();
                runCurrentMode();
            }), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
            inputArea.addView(outlineButton("Pick downloaded media", view -> pickMedia()), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
            inputArea.addView(outlineButton("Cancel media scan", view -> {
                cancelMediaScan = true;
                Toast.makeText(this, "Cancel requested", Toast.LENGTH_SHORT).show();
            }), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(44)), 10));
        }
    }

    private Button inputChip(String value) {
        Button chip = new Button(this);
        chip.setText(value);
        chip.setAllCaps(false);
        chip.setGravity(Gravity.CENTER_VERTICAL | Gravity.LEFT);
        chip.setTextSize(13);
        chip.setTextColor(Color.parseColor(INK));
        chip.setBackground(round(PANEL, LINE, 8));
        chip.setPadding(dp(12), 0, dp(12), 0);
        return chip;
    }

    private void renderResult(ScanData data) {
        resultTitle.setText(data.title);
        resultSummary.setText(data.summary);
        resultBadge.setText(data.badge);
        resultBadge.setTextColor(Color.parseColor(data.badgeColor));
        resultBadge.setBackground(round(data.badgeBg, data.badgeBg, 18));

        findings.removeAllViews();
        for (Finding finding : data.findings) {
            findings.addView(findingCard(finding), marginTop(matchWrap(), 10));
        }

        if (selectedMediaUri != null && ("content".equals(activeMode) || "download".equals(activeMode))) {
            LinearLayout mediaActions = horizontalRow();
            findings.addView(mediaActions, marginTop(matchWrap(), 12));
            mediaActions.addView(primaryButton("Delete selected media", view -> deleteSelectedMedia()), new LinearLayout.LayoutParams(0, dp(46), 1));
            LinearLayout.LayoutParams skipParams = new LinearLayout.LayoutParams(0, dp(46), 1);
            skipParams.setMargins(dp(10), 0, 0, 0);
            mediaActions.addView(outlineButton("Skip", view -> {
                selectedMediaUri = null;
                selectedMediaInfo = "";
                Toast.makeText(this, "Skipped. No deletion performed.", Toast.LENGTH_SHORT).show();
                renderMode(activeMode);
            }), skipParams);
        }

        recommendations.removeAllViews();
        for (String action : data.actions) {
            TextView line = text("- " + action, 14, INK, false);
            line.setPadding(0, dp(5), 0, dp(5));
            recommendations.addView(line);
        }
    }

    private View findingCard(Finding finding) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(14), dp(13), dp(14), dp(13));
        card.setBackground(round(PANEL, LINE, 8));
        card.addView(text(finding.title, 15, INK, true));
        TextView copy = text(finding.body, 14, MUTED, false);
        copy.setPadding(0, dp(7), 0, 0);
        card.addView(copy);
        if (finding.packageName != null) {
            card.addView(outlineButton("Open app settings", view -> openAppDetails(finding.packageName)), marginTop(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, dp(42)), 10));
        }
        return card;
    }

    private ScanData defaultResult(String mode) {
        if ("permissions".equals(mode)) {
            return analyzePermissions();
        }
        return analyzeTextMode(mode, sampleFor(mode));
    }

    private ScanData analyzeTextMode(String mode, String input) {
        if ("message".equals(mode)) return analyzeMessage(input);
        if ("url".equals(mode)) return analyzeUrl(input);
        if ("data".equals(mode)) return analyzeSensitiveData(input);
        if ("browser".equals(mode)) return analyzeBrowserData(input);
        if ("malware".equals(mode)) return analyzeMalware(input);
        if ("content".equals(mode)) return analyzeContentSafety(input);
        return analyzeDownloadGuard(input);
    }

    private ScanData analyzePermissions() {
        List<Finding> appFindings = new ArrayList<>();
        if (cameraApps.isEmpty()) {
            appFindings.add(new Finding("No camera apps found", "No installed apps requesting camera permission were found.", null));
        } else {
            int count = Math.min(8, cameraApps.size());
            for (int i = 0; i < count; i++) {
                AppCameraRisk app = cameraApps.get(i);
                appFindings.add(new Finding(app.appName, "Risk score " + app.riskScore + "/100. Signals: " + joinReasons(app.reasons) + ".", app.packageName));
            }
        }
        int risky = highRiskCameraCount();
        return new ScanData(
            "Permission intelligence",
            "Scanned installed apps that request camera permission.",
            risky > 0 ? "High Risk" : "Healthy",
            risky > 0 ? DANGER : SAFE,
            risky > 0 ? "#fee2e2" : "#dcfce7",
            "",
            appFindings,
            Arrays.asList(
                "Open risky app settings and revoke permissions you do not need.",
                "Use the Camera shortcut above to review Android camera permissions.",
                "Use Privacy Dashboard for recent camera access history."
            ),
            Math.max(36, 78 - risky * 4),
            Math.max(34, 74 - risky * 3),
            Math.min(95, 18 + risky * 9),
            Math.max(28, 82 - risky * 7),
            18
        );
    }

    private ScanData analyzeInstalledAppsForMalware() {
        List<AppCameraRisk> riskyApps = findRiskyInstalledApps();
        List<Finding> appFindings = new ArrayList<>();
        int topScore = 0;
        if (riskyApps.isEmpty()) {
            appFindings.add(new Finding("No high-risk app combinations found", "Installed apps did not expose the suspicious permission combinations checked by this local scan.", null));
        } else {
            int count = Math.min(10, riskyApps.size());
            for (int i = 0; i < count; i++) {
                AppCameraRisk app = riskyApps.get(i);
                topScore = Math.max(topScore, app.riskScore);
                appFindings.add(new Finding(app.appName, "Risk score " + app.riskScore + "/100. Signals: " + joinReasons(app.reasons) + ".", app.packageName));
            }
        }
        return result("Malware app alert", "Scanned installed apps for risky permission and special-access combinations.", "Installed app scan", topScore, appFindings,
            Arrays.asList("Open unknown high-risk apps and revoke sensitive permissions.", "Uninstall apps with SMS, overlay, accessibility, or sideload combinations you do not trust.", "Change important passwords if a suspicious app had accessibility or SMS access."),
            76 - topScore / 3, 74 - topScore / 2, topScore, 72 - topScore / 3, 30);
    }

    private boolean hasSmsPermission() {
        return checkSelfPermission(Manifest.permission.READ_SMS) == PackageManager.PERMISSION_GRANTED;
    }

    private boolean hasMediaPermission() {
        if (Build.VERSION.SDK_INT >= 33) {
            return checkSelfPermission(Manifest.permission.READ_MEDIA_IMAGES) == PackageManager.PERMISSION_GRANTED
                && checkSelfPermission(Manifest.permission.READ_MEDIA_VIDEO) == PackageManager.PERMISSION_GRANTED;
        }
        return checkSelfPermission(Manifest.permission.READ_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED;
    }

    private String readRecentSmsMessages() {
        StringBuilder builder = new StringBuilder();
        ContentResolver resolver = getContentResolver();
        Uri uri = Uri.parse("content://sms/inbox");
        Cursor cursor = null;
        try {
            cursor = resolver.query(uri, new String[] {"address", "body", "date"}, null, null, "date DESC");
            int count = 0;
            if (cursor != null) {
                int addressIndex = cursor.getColumnIndex("address");
                int bodyIndex = cursor.getColumnIndex("body");
                while (cursor.moveToNext() && count < 40) {
                    String address = addressIndex >= 0 ? cursor.getString(addressIndex) : "unknown";
                    String body = bodyIndex >= 0 ? cursor.getString(bodyIndex) : "";
                    builder.append("From: ").append(address).append("\n").append(body).append("\n\n");
                    count++;
                }
            }
        } catch (SecurityException ignored) {
            Toast.makeText(this, "SMS permission was not granted", Toast.LENGTH_SHORT).show();
        } finally {
            if (cursor != null) {
                cursor.close();
            }
        }
        if (builder.length() == 0) {
            return "No readable SMS messages found. Paste a message here and tap Analyze.";
        }
        return builder.toString();
    }

    private String readClipboardText() {
        ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (clipboard == null || !clipboard.hasPrimaryClip()) {
            return "";
        }
        ClipData clip = clipboard.getPrimaryClip();
        if (clip == null || clip.getItemCount() == 0) {
            return "";
        }
        CharSequence text = clip.getItemAt(0).coerceToText(this);
        return text == null ? "" : text.toString();
    }

    private void pickMedia() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        intent.putExtra(Intent.EXTRA_MIME_TYPES, new String[] {"image/*", "video/*"});
        try {
            startActivityForResult(intent, REQUEST_PICK_MEDIA);
        } catch (ActivityNotFoundException ignored) {
            Toast.makeText(this, "No file picker is available on this device", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_READ_SMS) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                runCurrentMode();
            } else {
                Toast.makeText(this, "SMS scan needs READ_SMS permission", Toast.LENGTH_LONG).show();
            }
        } else if (requestCode == REQUEST_READ_MEDIA) {
            if (pendingFullDeviceScan && hasSmsPermission() && hasMediaPermission()) {
                runFullDeviceScan();
            } else if (pendingFullDeviceScan) {
                pendingFullDeviceScan = false;
                List<Finding> blocked = new ArrayList<>();
                if (!hasSmsPermission()) {
                    blocked.add(new Finding("SMS permission missing", "READ_SMS was denied, so SMS inbox scanning cannot run.", null));
                }
                if (!hasMediaPermission()) {
                    blocked.add(new Finding("Media permission missing", "Image/video permission was denied, so gallery scanning cannot run.", null));
                }
                ScanData result = new ScanData(
                    "Permission setup incomplete",
                    "Android permissions are blocking full device scanning.",
                    "Blocked",
                    DANGER,
                    "#fee2e2",
                    "",
                    blocked,
                    Arrays.asList("Open Grant permissions and allow SMS plus media access.", "Enable notification access from Settings for app notifications."),
                    50,
                    50,
                    45,
                    45,
                    0
                );
                showCompletedResult(result);
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_PICK_MEDIA && resultCode == RESULT_OK && data != null && data.getData() != null) {
            Uri uri = data.getData();
            selectedMediaUri = uri;
            selectedMediaInfo = describeMedia(uri);
            if (currentInput != null) {
                currentInput.setText(selectedMediaInfo);
            }
            cancelMediaScan = false;
            Toast.makeText(this, "Scanning selected media on device", Toast.LENGTH_SHORT).show();
            new Thread(() -> {
                ScanData result = analyzeSelectedMedia(uri, selectedMediaInfo);
                runOnUiThread(() -> {
                    showCompletedResult(result);
                    Toast.makeText(this, cancelMediaScan ? "Media scan cancelled" : "Selected media scanned on device", Toast.LENGTH_SHORT).show();
                });
            }).start();
        } else if (requestCode == REQUEST_PICK_BROWSER_HISTORY && resultCode == RESULT_OK && data != null && data.getData() != null) {
            Uri uri = data.getData();
            String browserData = readTextFromUri(uri);
            if (browserData.length() == 0) {
                Toast.makeText(this, "Could not read browser history file", Toast.LENGTH_LONG).show();
                return;
            }
            if (currentInput != null) {
                currentInput.setText(browserData);
            }
            ScanData result = analyzeBrowserData(browserData);
            showCompletedResult(result);
            Toast.makeText(this, "Imported browser data scanned locally", Toast.LENGTH_SHORT).show();
        } else if (requestCode == REQUEST_BROWSER_VPN) {
            if (resultCode == RESULT_OK) {
                startBrowserMonitorService(BrowserPrivacyVpnService.ACTION_ENABLE);
                Toast.makeText(this, "Browser VPN/DNS monitor consent enabled", Toast.LENGTH_LONG).show();
            } else {
                Toast.makeText(this, "VPN/DNS monitor permission was not granted", Toast.LENGTH_LONG).show();
            }
        }
    }

    private void pickBrowserHistoryFile() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        intent.putExtra(Intent.EXTRA_MIME_TYPES, new String[] {"text/*", "text/csv", "application/json", "text/html", "application/xhtml+xml"});
        try {
            startActivityForResult(intent, REQUEST_PICK_BROWSER_HISTORY);
        } catch (ActivityNotFoundException ignored) {
            Toast.makeText(this, "No file picker is available on this device", Toast.LENGTH_SHORT).show();
        }
    }

    private String readTextFromUri(Uri uri) {
        try (InputStream input = getContentResolver().openInputStream(uri);
             ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            if (input == null) {
                return "";
            }
            byte[] buffer = new byte[4096];
            int total = 0;
            int read;
            while ((read = input.read(buffer)) != -1 && total < 512 * 1024) {
                output.write(buffer, 0, read);
                total += read;
            }
            return output.toString("UTF-8");
        } catch (Exception ignored) {
            return "";
        }
    }

    private void toggleBrowserMonitor() {
        if (browserMonitorEnabled) {
            startBrowserMonitorService(BrowserPrivacyVpnService.ACTION_DISABLE);
            browserMonitorEnabled = false;
            Toast.makeText(this, "Browser VPN/DNS monitor disabled", Toast.LENGTH_SHORT).show();
            renderMode(activeMode);
            return;
        }

        Intent prepare = VpnService.prepare(this);
        if (prepare != null) {
            startActivityForResult(prepare, REQUEST_BROWSER_VPN);
            return;
        }
        startBrowserMonitorService(BrowserPrivacyVpnService.ACTION_ENABLE);
        browserMonitorEnabled = true;
        Toast.makeText(this, "Browser VPN/DNS monitor consent enabled", Toast.LENGTH_LONG).show();
        renderMode(activeMode);
    }

    private void startBrowserMonitorService(String action) {
        Intent service = new Intent(this, BrowserPrivacyVpnService.class);
        service.setAction(action);
        startService(service);
        browserMonitorEnabled = BrowserPrivacyVpnService.ACTION_ENABLE.equals(action);
    }

    private String describeMedia(Uri uri) {
        String name = "selected-media";
        String type = getContentResolver().getType(uri);
        Cursor cursor = null;
        try {
            cursor = getContentResolver().query(uri, null, null, null, null);
            if (cursor != null && cursor.moveToFirst()) {
                int nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (nameIndex >= 0) {
                    name = cursor.getString(nameIndex);
                }
            }
        } finally {
            if (cursor != null) {
                cursor.close();
            }
        }
        return "Selected media\nName: " + name + "\nMIME: " + (type == null ? "unknown" : type) + "\nURI: " + uri;
    }

    private void deleteSelectedMedia() {
        if (selectedMediaUri == null) {
            Toast.makeText(this, "No selected media to delete", Toast.LENGTH_SHORT).show();
            return;
        }
        try {
            int deleted = getContentResolver().delete(selectedMediaUri, null, null);
            if (deleted > 0) {
                ScanHistory.append(this, "media-delete", "Deleted", 100, selectedMediaInfo);
                Toast.makeText(this, "Selected media deleted", Toast.LENGTH_LONG).show();
                selectedMediaUri = null;
                selectedMediaInfo = "";
                renderMode(activeMode);
            } else {
                Toast.makeText(this, "Delete was not allowed by the media provider", Toast.LENGTH_LONG).show();
            }
        } catch (SecurityException securityException) {
            Toast.makeText(this, "Delete needs file owner permission. Pick the file through Documents and try again.", Toast.LENGTH_LONG).show();
        } catch (Exception exception) {
            Toast.makeText(this, "Could not delete selected media", Toast.LENGTH_LONG).show();
        }
    }

    private ScanData analyzeSelectedMedia(Uri uri, String mediaInfo) {
        String type = getContentResolver().getType(uri);
        boolean isVideo = type != null && type.startsWith("video/");
        boolean isImage = type != null && type.startsWith("image/");
        MediaScanResult visual = isVideo ? scanVideoFrames(uri) : scanImagePixels(uri);
        if (!isVideo && !isImage && visual.framesScanned == 0) {
            visual = scanImagePixels(uri);
        }

        String lower = mediaInfo.toLowerCase(Locale.US);
        int score = visual.riskScore;
        List<Finding> items = new ArrayList<>();
        items.add(new Finding(
            isVideo ? "Video frame scan" : "Image pixel scan",
            "Scanned " + visual.framesScanned + " frame(s). Skin-tone coverage " + visual.skinPercent + "%. Highest frame risk " + visual.riskScore + "/100.",
            null
        ));

        int sensitivity = AppSettings.sensitivity(this);
        int highThreshold = Math.max(35, Math.min(90, sensitivity));
        int reviewThreshold = Math.max(20, highThreshold - 30);

        if (visual.riskScore >= highThreshold) {
            items.add(new Finding("Nudity visual risk", "The selected media has a high exposed-skin visual signal. No preview was shown.", null));
        } else if (visual.riskScore >= reviewThreshold) {
            items.add(new Finding("Adult visual review", "The selected media has a moderate exposed-skin signal and should be reviewed privately.", null));
        } else {
            items.add(new Finding("No strong nudity signal", "The local visual scan did not find a strong exposed-skin pattern.", null));
        }

        if (containsAny(lower, "adult", "explicit", "nudity", "porn")) {
            score += 25;
            items.add(new Finding("Filename or metadata marker", "The file metadata contains adult-content wording.", null));
        }
        if (containsAny(lower, "fake id", "stolen card", "cvv", "attack", "bomb", "weapon")) {
            score += 25;
            items.add(new Finding("Illegal activity text marker", "The file name or metadata contains suspicious illegal-activity wording.", null));
        }

        score = clamp(score);
        String title = "download".equals(activeMode) ? "Adult download restriction" : "Opt-in content safety scan";
        String summary = isVideo
            ? "Sampled video frames locally for adult/nudity visual risk."
            : "Decoded image locally for adult/nudity visual risk.";
        List<String> actions = new ArrayList<>();
        if (score >= highThreshold) {
            actions.add("Show a private alert with Delete and Skip choices.");
            actions.add("Do not display an explicit preview in the alert.");
            actions.add("Keep the media local; only labels should be sent to any backend.");
        } else if (score >= reviewThreshold) {
            actions.add("Ask the user to review this media privately.");
            actions.add("Avoid uploading raw media for cloud analysis.");
        } else {
            actions.add("No block needed from the local visual scan.");
            actions.add("Continue to use filename and metadata checks for policy decisions.");
        }

        return result(title, summary, mediaInfo, score, items, actions, 70 - score / 4, 72 - score / 3, score, 60, score);
    }

    private MediaScanResult scanImagePixels(Uri uri) {
        Bitmap bitmap = null;
        try {
            BitmapFactory.Options bounds = new BitmapFactory.Options();
            bounds.inJustDecodeBounds = true;
            BitmapFactory.decodeStream(getContentResolver().openInputStream(uri), null, bounds);

            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inSampleSize = sampleSize(bounds.outWidth, bounds.outHeight, 360);
            bitmap = BitmapFactory.decodeStream(getContentResolver().openInputStream(uri), null, options);
            if (bitmap == null) {
                return new MediaScanResult(0, 0, 0);
            }
            return scanBitmapForSkin(bitmap, 1);
        } catch (Exception ignored) {
            return new MediaScanResult(0, 0, 0);
        } finally {
            if (bitmap != null) {
                bitmap.recycle();
            }
        }
    }

    private MediaScanResult scanVideoFrames(Uri uri) {
        MediaMetadataRetriever retriever = new MediaMetadataRetriever();
        int bestScore = 0;
        int bestSkin = 0;
        int frames = 0;
        try {
            retriever.setDataSource(this, uri);
            String durationText = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION);
            long durationMs = durationText == null ? 0 : Long.parseLong(durationText);
            int desiredFrames = Math.max(1, AppSettings.videoFrames(this));
            for (int index = 0; index < desiredFrames; index++) {
                if (cancelMediaScan) {
                    break;
                }
                long positionMs = durationMs > 0 ? ((durationMs * (index + 1)) / (desiredFrames + 1)) : 0;
                Bitmap frame = retriever.getFrameAtTime(positionMs * 1000, MediaMetadataRetriever.OPTION_CLOSEST_SYNC);
                if (frame == null) {
                    continue;
                }
                MediaScanResult result = scanBitmapForSkin(frame, 1);
                frame.recycle();
                frames++;
                if (result.riskScore > bestScore) {
                    bestScore = result.riskScore;
                    bestSkin = result.skinPercent;
                }
            }
        } catch (Exception ignored) {
            return new MediaScanResult(0, 0, 0);
        } finally {
            try {
                retriever.release();
            } catch (Exception ignored) {
                // Nothing to clean up.
            }
        }
        return new MediaScanResult(bestScore, bestSkin, frames);
    }

    private MediaBatchResult scanRecentMediaBatch(int limit) {
        List<Finding> batchFindings = new ArrayList<>();
        int maxScore = 0;
        int scanned = 0;

        scanned += scanRecentMediaUri(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, "image", Math.max(1, limit / 2), batchFindings);
        scanned += scanRecentMediaUri(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, "video", Math.max(1, limit / 2), batchFindings);
        for (Finding finding : batchFindings) {
            int score = extractScore(finding.body);
            maxScore = Math.max(maxScore, score);
        }
        if (scanned == 0) {
            batchFindings.add(new Finding("Recent media scan", "No readable recent images or videos were found through MediaStore.", null));
        }
        return new MediaBatchResult(batchFindings, maxScore);
    }

    private int scanRecentMediaUri(Uri collection, String kind, int limit, List<Finding> findingsOut) {
        Cursor cursor = null;
        int scanned = 0;
        try {
            String[] projection = new String[] {MediaStore.MediaColumns._ID, MediaStore.MediaColumns.DISPLAY_NAME};
            cursor = getContentResolver().query(collection, projection, null, null, MediaStore.MediaColumns.DATE_ADDED + " DESC");
            if (cursor == null) {
                return 0;
            }
            int idIndex = cursor.getColumnIndex(MediaStore.MediaColumns._ID);
            int nameIndex = cursor.getColumnIndex(MediaStore.MediaColumns.DISPLAY_NAME);
            while (cursor.moveToNext() && scanned < limit) {
                long id = cursor.getLong(idIndex);
                String name = nameIndex >= 0 ? cursor.getString(nameIndex) : kind + "-" + id;
                Uri itemUri = Uri.withAppendedPath(collection, String.valueOf(id));
                MediaScanResult visual = "video".equals(kind) ? scanVideoFrames(itemUri) : scanImagePixels(itemUri);
                int score = visual.riskScore;
                findingsOut.add(new Finding(
                    "Recent " + kind + ": " + name,
                    "Visual score " + score + "/100. Skin-tone coverage " + visual.skinPercent + "%. Frames scanned " + visual.framesScanned + ".",
                    null
                ));
                scanned++;
            }
        } catch (SecurityException securityException) {
            findingsOut.add(new Finding("Recent " + kind + " scan blocked", "Android denied access to " + kind + " media.", null));
        } catch (Exception exception) {
            findingsOut.add(new Finding("Recent " + kind + " scan failed", "Could not scan recent " + kind + " media on this device.", null));
        } finally {
            if (cursor != null) {
                cursor.close();
            }
        }
        return scanned;
    }

    private int extractScore(String body) {
        java.util.regex.Matcher matcher = Pattern.compile("score ([0-9]{1,3})/100", Pattern.CASE_INSENSITIVE).matcher(body);
        if (matcher.find()) {
            try {
                return clamp(Integer.parseInt(matcher.group(1)));
            } catch (Exception ignored) {
                return 0;
            }
        }
        return 0;
    }

    private MediaScanResult scanBitmapForSkin(Bitmap bitmap, int frameCount) {
        int width = bitmap.getWidth();
        int height = bitmap.getHeight();
        if (width == 0 || height == 0) {
            return new MediaScanResult(0, 0, frameCount);
        }

        int step = Math.max(1, Math.min(width, height) / 120);
        int total = 0;
        int skin = 0;
        int centerSkin = 0;
        int lowerSkin = 0;
        int centerTotal = 0;
        int lowerTotal = 0;

        for (int y = 0; y < height; y += step) {
            boolean centerY = y > height * 0.18f && y < height * 0.82f;
            boolean lowerY = y > height * 0.45f;
            for (int x = 0; x < width; x += step) {
                int color = bitmap.getPixel(x, y);
                int red = Color.red(color);
                int green = Color.green(color);
                int blue = Color.blue(color);
                boolean isSkin = isSkinTone(red, green, blue);
                total++;
                if (isSkin) {
                    skin++;
                }
                boolean centerX = x > width * 0.18f && x < width * 0.82f;
                if (centerX && centerY) {
                    centerTotal++;
                    if (isSkin) centerSkin++;
                }
                if (centerX && lowerY) {
                    lowerTotal++;
                    if (isSkin) lowerSkin++;
                }
            }
        }

        int skinPercent = total == 0 ? 0 : Math.round((skin * 100f) / total);
        int centerPercent = centerTotal == 0 ? 0 : Math.round((centerSkin * 100f) / centerTotal);
        int lowerPercent = lowerTotal == 0 ? 0 : Math.round((lowerSkin * 100f) / lowerTotal);
        int risk = Math.max(skinPercent, Math.max(centerPercent, lowerPercent));
        if (skinPercent > 32 && centerPercent > 35) risk += 15;
        if (lowerPercent > 38) risk += 10;
        if (skinPercent < 12) risk -= 15;
        return new MediaScanResult(clamp(risk), skinPercent, frameCount);
    }

    private boolean isSkinTone(int red, int green, int blue) {
        int max = Math.max(red, Math.max(green, blue));
        int min = Math.min(red, Math.min(green, blue));
        boolean rgbRule = red > 70 && green > 35 && blue > 20 && (max - min) > 15 && red > green && red > blue && Math.abs(red - green) > 10;
        float[] hsv = new float[3];
        Color.RGBToHSV(red, green, blue, hsv);
        boolean hsvRule = hsv[0] >= 0 && hsv[0] <= 50 && hsv[1] >= 0.18f && hsv[1] <= 0.75f && hsv[2] >= 0.28f;
        return rgbRule && hsvRule;
    }

    private int sampleSize(int width, int height, int target) {
        int sample = 1;
        int max = Math.max(width, height);
        while (max / sample > target) {
            sample *= 2;
        }
        return Math.max(1, sample);
    }

    private ScanData analyzeMessage(String input) {
        List<SmsThreat> smsThreats = findSuspiciousSmsMessages(input);
        int score = 0;
        List<Finding> items = new ArrayList<>();

        if (!smsThreats.isEmpty()) {
            for (SmsThreat threat : smsThreats) {
                score = Math.max(score, threat.score);
                items.add(new Finding(
                    "Suspicious message from " + threat.sender,
                    "Score " + threat.score + "/100. Signals: " + joinReasons(threat.reasons) + ". Text: " + threat.preview,
                    null
                ));
            }
        }

        String lower = input.toLowerCase(Locale.US);
        if (containsAny(lower, "otp", "password", "pin", "cvv")) {
            score += 30;
            if (smsThreats.isEmpty()) {
                items.add(new Finding("Credential request", "The message asks for OTP, password, PIN, or payment secrets.", null));
            }
        }
        if (containsAny(lower, "urgent", "final warning", "blocked", "expire", "suspend", "immediately")) {
            score += 25;
            if (smsThreats.isEmpty()) {
                items.add(new Finding("Pressure language", "Urgency and account-blocking language are common fraud tactics.", null));
            }
        }
        if (containsAny(lower, "bank", "kyc", "upi", "refund", "reward", "lottery", "parcel")) {
            score += 15;
            if (smsThreats.isEmpty()) {
                items.add(new Finding("Financial lure", "The message uses banking, payment, reward, or delivery context.", null));
            }
        }
        if (hasUrl(lower)) {
            score += 25;
            if (smsThreats.isEmpty()) {
                items.add(new Finding("Embedded link", "The message contains a link. Open official apps manually instead.", null));
            }
        }
        if (containsAny(lower, ".apk", " apk", "install app", "download app", "unknown sources", "install unknown apps", "sideload")) {
            score += 35;
            if (smsThreats.isEmpty()) {
                items.add(new Finding("Malware install lure", "The message asks you to install an APK or enable unknown-source installs.", null));
            }
        }
        if (containsAny(lower, "play protect", "disable antivirus", "turn off antivirus", "accessibility", "notification access", "draw over other apps", "overlay permission")) {
            score += 30;
            if (smsThreats.isEmpty()) {
                items.add(new Finding("Dangerous access request", "The message asks for device protection changes or powerful app access.", null));
            }
        }
        if (items.isEmpty()) {
            items.add(new Finding("No major message threat markers", "No OTP request, pressure phrase, malware install lure, dangerous access request, financial lure, or URL was detected.", null));
        }
        return result("Message threat analysis", "Local scan checked recent text messages for fraud, malware install lures, risky access requests, and suspicious links.", input, score, items,
            Arrays.asList("Do not share OTPs or passwords.", "Do not install APKs from messages or enable unknown-source installs.", "Verify requests inside the official app.", "Block and report suspicious senders."),
            70 - score / 3, 72 - score / 2, score, 66, 22);
    }

    private List<SmsThreat> findSuspiciousSmsMessages(String input) {
        List<SmsThreat> threats = new ArrayList<>();
        String[] blocks = input.split("\\n\\n+");
        for (String block : blocks) {
            String trimmed = block.trim();
            if (trimmed.length() == 0 || !trimmed.toLowerCase(Locale.US).startsWith("from:")) {
                continue;
            }
            String[] lines = trimmed.split("\\n", 2);
            String sender = lines[0].replaceFirst("(?i)^from:\\s*", "").trim();
            String body = lines.length > 1 ? lines[1].trim() : "";
            SmsThreat threat = scoreSmsThreat(sender.length() == 0 ? "unknown" : sender, body);
            if (threat.score >= 35) {
                threats.add(threat);
            }
        }
        return threats;
    }

    private SmsThreat scoreSmsThreat(String sender, String body) {
        String lower = body.toLowerCase(Locale.US);
        int score = 0;
        List<String> reasons = new ArrayList<>();
        if (containsAny(lower, ".apk", " apk", "install app", "download app", "security update", "cleaner app", "scanner app")) {
            score += 35;
            reasons.add("APK/install lure");
        }
        if (containsAny(lower, "unknown sources", "install unknown apps", "unknown app installs", "sideload")) {
            score += 35;
            reasons.add("unknown-source install request");
        }
        if (containsAny(lower, "play protect", "disable antivirus", "turn off antivirus", "security scan disabled")) {
            score += 35;
            reasons.add("disable protection request");
        }
        if (containsAny(lower, "accessibility", "notification access", "draw over other apps", "overlay permission")) {
            score += 30;
            reasons.add("dangerous access request");
        }
        if (containsAny(lower, "otp", "password", "pin", "cvv")) {
            score += 25;
            reasons.add("credential request");
        }
        if (containsAny(lower, "urgent", "final warning", "blocked", "expire", "suspend", "immediately")) {
            score += 20;
            reasons.add("pressure language");
        }
        if (containsAny(lower, "bank", "kyc", "upi", "refund", "reward", "lottery", "parcel", "courier", "bill")) {
            score += 12;
            reasons.add("trusted-service lure");
        }
        if (hasUrl(lower)) {
            score += 22;
            reasons.add("embedded link");
        }
        return new SmsThreat(sender, clamp(score), reasons, preview(body));
    }

    private ScanData analyzeUrl(String input) {
        String lower = input.toLowerCase(Locale.US).trim();
        int score = 0;
        List<Finding> items = new ArrayList<>();
        if (lower.startsWith("http://")) {
            score += 25;
            items.add(new Finding("Unsafe HTTP", "The URL does not use HTTPS.", null));
        }
        if (lower.contains("@") || lower.contains("%40")) {
            score += 25;
            items.add(new Finding("URL obfuscation", "An at-sign can hide the real destination host.", null));
        }
        if (containsAny(lower, "bit.ly", "tinyurl", "t.co", "goo.gl")) {
            score += 20;
            items.add(new Finding("Shortened link", "Short links hide the final destination.", null));
        }
        if (containsAny(lower, ".click", ".top", ".xyz", ".loan", ".work")) {
            score += 18;
            items.add(new Finding("Suspicious domain", "The URL uses a domain pattern often abused in campaigns.", null));
        }
        if (containsAny(lower, "sbi", "hdfc", "bank", "login", "verify", "kyc") && !containsAny(lower, "https://www.", "https://secure.")) {
            score += 18;
            items.add(new Finding("Brand impersonation", "The link appears to imitate a banking or login page.", null));
        }
        if (items.isEmpty()) {
            items.add(new Finding("No major URL markers", "No unsafe transport, obfuscation, shortener, or suspicious TLD was detected.", null));
        }
        return result("Phishing URL analysis", "Local scan checked transport, obfuscation, shorteners, and brand impersonation.", input, score, items,
            Arrays.asList("Type sensitive websites manually.", "Avoid short links for financial actions.", "Do not enter credentials on suspicious domains."),
            78 - score / 4, 74 - score / 3, score, 70, 18);
    }

    private ScanData analyzeSensitiveData(String input) {
        int score = 0;
        List<Finding> items = new ArrayList<>();
        if (matches(input, "\\b[A-Z]{5}[0-9]{4}[A-Z]\\b")) {
            score += 20;
            items.add(new Finding("PAN detected", "A tax identifier pattern appears in the text.", null));
        }
        if (matches(input, "\\b[0-9]{4}\\s?[0-9]{4}\\s?[0-9]{4}\\b")) {
            score += 20;
            items.add(new Finding("Aadhaar-like ID", "A 12-digit identity pattern appears in the text.", null));
        }
        if (matches(input, "\\b(?:[0-9][ -]*?){13,19}\\b")) {
            score += 20;
            items.add(new Finding("Payment card pattern", "A card-number-like sequence was found.", null));
        }
        if (matches(input.toLowerCase(Locale.US), "\\b(cvv|secret|api[_-]?key|token|recovery phrase|seed phrase)\\b")) {
            score += 35;
            items.add(new Finding("Secret material", "Credential, CVV, token, or recovery-secret wording was found.", null));
        }
        if (items.isEmpty()) {
            items.add(new Finding("No sensitive data markers", "No identity, card, CVV, token, or recovery-secret pattern was detected.", null));
        }
        return result("Sensitive data discovery", "Local scan looked for identity, banking, card, token, and recovery-secret patterns.", input, score, items,
            Arrays.asList("Move sensitive notes to an encrypted vault.", "Rotate exposed keys or tokens.", "Delete CVV and recovery phrases from plain text."),
            78 - score / 3, 76 - score / 3, Math.min(70, score), 68, score);
    }

    private ScanData analyzeBrowserData(String input) {
        String lower = input.toLowerCase(Locale.US);
        int score = 0;
        int urlCount = 0;
        int trackerCount = 0;
        int sensitiveUrlCount = 0;
        List<Finding> items = new ArrayList<>();

        Matcher matcher = Pattern.compile("https?://[^\\s\"'<>]+|www\\.[^\\s\"'<>]+", Pattern.CASE_INSENSITIVE).matcher(input);
        while (matcher.find() && urlCount < 80) {
            urlCount++;
            String url = matcher.group();
            String urlLower = url.toLowerCase(Locale.US);
            String domain = extractDomain(urlLower);
            int urlScore = 0;
            List<String> reasons = new ArrayList<>();

            if (urlLower.startsWith("http://")) {
                urlScore += 20;
                reasons.add("unsafe HTTP");
            }
            if (BrowserPrivacyFeed.isTrackerDomain(domain)) {
                urlScore += 18;
                trackerCount++;
                reasons.add("tracking or ad domain");
            }
            if (BrowserPrivacyFeed.isDataBrokerDomain(domain)) {
                urlScore += 30;
                reasons.add("data broker style domain");
            }
            if (containsAny(urlLower, "email=", "phone=", "mobile=", "otp=", "token=", "session=", "password=", "pan=", "aadhaar=") || SensitiveTextGuard.containsSensitiveData(url)) {
                urlScore += 35;
                sensitiveUrlCount++;
                reasons.add("personal data in URL");
            }
            if (containsAny(domain, ".click", ".top", ".xyz", ".loan", ".work") || containsAny(urlLower, "login", "verify", "kyc", "secure-update")) {
                urlScore += 18;
                reasons.add("phishing-like URL pattern");
            }

            if (urlScore >= 25) {
                score += Math.min(45, urlScore);
                items.add(new Finding(
                    "Risky browser entry: " + domain,
                    "Signals: " + joinReasons(reasons) + ". URL: " + SensitiveTextGuard.redact(url),
                    null
                ));
            }
        }

        if (urlCount == 0 && lower.trim().length() > 0) {
            score += 10;
            items.add(new Finding("No URLs extracted", "Paste browser history export text, copied history rows, or shared URLs to scan website privacy risk.", null));
        }
        if (trackerCount > 3) {
            score += 20;
            items.add(new Finding("Repeated tracker exposure", "Multiple tracker or advertising domains were found in the provided browser data.", null));
        }
        if (sensitiveUrlCount > 0) {
            score += 25;
            items.add(new Finding("Personal info in browser data", "One or more URLs appear to contain OTP, phone, email, token, or identity data.", null));
        }
        if (items.isEmpty()) {
            items.add(new Finding("No risky browser entries", "No tracker, data-broker, unsafe HTTP, personal-data URL, or phishing-like marker was detected.", null));
        }

        return result("Browser data alert", "Local scan checked user-provided browser data with feed " + BrowserPrivacyFeed.VERSION + " for trackers, data brokers, unsafe sites, and personal info in URLs.", input, score, items,
            Arrays.asList("Clear history and site data for flagged domains.", "Use the browser data settings shortcuts below to clean app storage.", "Remove saved passwords or sessions for suspicious websites.", "Avoid sharing browser history unless the scan is authenticated and redacted.", "Use browser privacy settings to block third-party cookies and trackers."),
            76 - score / 3, 74 - score / 3, score, 66, Math.min(90, sensitiveUrlCount * 30 + trackerCount * 6));
    }

    private ScanData analyzeMalware(String input) {
        String lower = input.toLowerCase(Locale.US);
        int score = 0;
        List<Finding> items = new ArrayList<>();
        if (containsAny(lower, "accessibility", "bind_accessibility")) {
            score += 25;
            items.add(new Finding("Accessibility access", "Accessibility can observe screens and interact with apps.", null));
        }
        if (containsAny(lower, "overlay", "system_alert_window", "draw over")) {
            score += 20;
            items.add(new Finding("Overlay capability", "Overlays can cover legitimate prompts or mimic UI.", null));
        }
        if (containsAny(lower, "read_sms", "sms", "otp")) {
            score += 20;
            items.add(new Finding("SMS or OTP access", "SMS access may expose one-time passwords.", null));
        }
        if (containsAny(lower, "unknown installer", "apk install", "request_install_packages", "sideload")) {
            score += 18;
            items.add(new Finding("Unknown installation source", "Apps installed outside trusted stores deserve extra review.", null));
        }
        if (containsAny(lower, "malicious", "evil", "command", "c2", ".ru", ".top")) {
            score += 22;
            items.add(new Finding("Network indicator", "The text includes suspicious domain or command-and-control wording.", null));
        }
        if (items.isEmpty()) {
            items.add(new Finding("No major malware markers", "No accessibility, overlay, SMS, sideload, or malicious-domain marker was detected.", null));
        }
        return result("Malware app alert", "Local scan combined special access, installer, SMS, and network indicators.", input, score, items,
            Arrays.asList("Uninstall suspicious apps you do not recognize.", "Revoke accessibility, overlay, and SMS access.", "Change sensitive passwords from a trusted device."),
            76 - score / 3, 75 - score / 2, score, 70 - score / 3, 30);
    }

    private ScanData analyzeContentSafety(String input) {
        if (!contentSafetyEnabled) {
            return new ScanData("Opt-in content safety scan", "Feature is off. No content is scanned until you enable it.", "Off", SAFE, "#dcfce7", input,
                Arrays.asList(new Finding("Scanning disabled", "Tap Turn content safety on, then Analyze to scan the text locally.", null)),
                Arrays.asList("Enable this only with explicit user consent.", "Keep raw content on device whenever possible."),
                74, 69, 0, 62, 18);
        }
        String lower = input.toLowerCase(Locale.US);
        int score = 0;
        List<Finding> items = new ArrayList<>();
        if (containsAny(lower, "attack", "kill", "bomb", "shoot", "public crowd")) {
            score += 35;
            items.add(new Finding("Threat indicator", "The content includes language about physical harm.", null));
        }
        if (containsAny(lower, "stolen card", "fake id", "cvv sale", "sell otp")) {
            score += 25;
            items.add(new Finding("Financial crime indicator", "The content references fake IDs, stolen cards, CVV, or OTP trade.", null));
        }
        if (containsAny(lower, "adult", "nudity", "explicit sexual")) {
            score += 25;
            items.add(new Finding("Private media indicator", "Adult or nudity labels should trigger a private Delete or Skip prompt.", null));
        }
        if (items.isEmpty()) {
            items.add(new Finding("No selected safety markers", "No threat, financial-crime, or adult-media marker was detected.", null));
        }
        return result("Opt-in content safety scan", "Local opt-in scan checked concrete harmful or adult media indicators.", input, score, items,
            Arrays.asList("Do not forward harmful content.", "Use a private Delete or Skip prompt for explicit media.", "Preserve evidence only through lawful safety channels."),
            70 - score / 4, 72 - score / 3, score, 60, 35);
    }

    private ScanData analyzeDownloadGuard(String input) {
        if (!downloadGuardEnabled) {
            return new ScanData("Adult download restriction", "Download Guard is off. The file would be allowed.", "Allowed", SAFE, "#dcfce7", input,
                Arrays.asList(new Finding("Blocking disabled", "Tap Enable blocking, then Analyze to enforce the local policy.", null)),
                Arrays.asList("Enable blocking to stop adult downloads before saving.", "Use metadata and on-device labels instead of uploading private media."),
                74, 71, 0, 62, 18);
        }
        String lower = input.toLowerCase(Locale.US);
        int score = 0;
        List<Finding> items = new ArrayList<>();
        if (containsAny(lower, "adult", "explicit", "porn", "nudity")) {
            score += 45;
            items.add(new Finding("Adult content marker", "The input includes adult or explicit media wording.", null));
        }
        if (containsAny(lower, ".mp4", ".mkv", ".mov", "video")) {
            score += 15;
            items.add(new Finding("Video download", "The file appears to be a video download.", null));
        }
        if (containsAny(lower, "chrome", "browser", "download")) {
            score += 10;
            items.add(new Finding("Download source", "The source appears to be a browser or download flow.", null));
        }
        if (items.isEmpty()) {
            items.add(new Finding("No block condition", "No adult marker or video download metadata was detected.", null));
        }
        return result("Adult download restriction", "Local policy checked filename, source, MIME hints, and media labels.", input, score, items,
            Arrays.asList(score >= 45 ? "Block the download before saving." : "Allow this download under the current policy.", "Show a private notice explaining the decision.", "Do not render explicit thumbnails in alerts."),
            72, 74, score, 66, 18);
    }

    private ScanData result(String title, String summary, String input, int rawScore, List<Finding> items, List<String> actions, int privacy, int security, int threat, int permission, int exposure) {
        int score = clamp(rawScore);
        String badge = score >= 80 ? "Critical" : score >= 45 ? "High Risk" : score > 0 ? "Review" : "Safe";
        String badgeColor = score >= 45 ? DANGER : SAFE;
        String badgeBg = score >= 80 ? "#fecaca" : score >= 45 ? "#fee2e2" : score > 0 ? "#fef3c7" : "#dcfce7";
        return new ScanData(title, summary, badge, badgeColor, badgeBg, input, items, actions, clamp(privacy), clamp(security), clamp(threat), clamp(permission), clamp(exposure));
    }

    private int[] metricsFor(ScanData data) {
        return new int[] {data.privacyScore, data.securityScore, data.threatScore, data.permissionScore, data.exposureScore};
    }

    private String sampleFor(String mode) {
        if ("message".equals(mode)) return "Final warning: Your bank KYC is expired. Account will be blocked in 30 minutes. Share OTP at http://bit.ly/secure-kyc";
        if ("url".equals(mode)) return "http://sbi-login-secure.example.click@evil.test/login";
        if ("data".equals(mode)) return "PAN ABCDE1234F\nAadhaar 1234 5678 9012\nsecret_key=sk_test_1234567890abcdef123456\nCVV: 123";
        if ("browser".equals(mode)) return "https://tracker.example/collect?email=ashok@example.com\nhttp://old-login.example.click/verify\nhttps://doubleclick.net/pagead/id";
        if ("malware".equals(mode)) return "Bank Security Update\nSignals: Accessibility, overlay, READ_SMS, unknown installer, malicious-example.test";
        if ("content".equals(mode)) return "Message says to attack a public crowd tomorrow\nImage labels: nudity\nOCR: fake ID and stolen card sale";
        return "URL: https://example.test/downloads/adult-video.mp4\nFile: adult-video.mp4\nSource: Chrome\nLabels: adult, explicit sexual";
    }

    private int clamp(int value) {
        return Math.max(0, Math.min(100, value));
    }

    private boolean containsAny(String value, String... needles) {
        for (String needle : needles) {
            if (value.contains(needle)) {
                return true;
            }
        }
        return false;
    }

    private boolean hasUrl(String value) {
        return value.contains("http://") || value.contains("https://") || value.contains("www.");
    }

    private String extractDomain(String url) {
        String value = url;
        if (value.startsWith("http://")) {
            value = value.substring(7);
        } else if (value.startsWith("https://")) {
            value = value.substring(8);
        }
        if (value.startsWith("www.")) {
            value = value.substring(4);
        }
        int slash = value.indexOf('/');
        if (slash >= 0) {
            value = value.substring(0, slash);
        }
        int query = value.indexOf('?');
        if (query >= 0) {
            value = value.substring(0, query);
        }
        int port = value.indexOf(':');
        if (port >= 0) {
            value = value.substring(0, port);
        }
        return value.length() == 0 ? "unknown" : value;
    }

    private boolean matches(String value, String regex) {
        return Pattern.compile(regex, Pattern.CASE_INSENSITIVE).matcher(value).find();
    }

    private String preview(String value) {
        String normalized = value.replaceAll("\\s+", " ").trim();
        if (normalized.length() <= 120) {
            return normalized;
        }
        return normalized.substring(0, 117) + "...";
    }

    private void refreshCameraAudit() {
        cameraApps = findAppsRequestingCamera();
        Collections.sort(cameraApps, (left, right) -> {
            int riskCompare = Integer.compare(right.riskScore, left.riskScore);
            if (riskCompare != 0) {
                return riskCompare;
            }
            return left.appName.compareToIgnoreCase(right.appName);
        });
    }

    private int highRiskCameraCount() {
        int count = 0;
        for (AppCameraRisk app : cameraApps) {
            if (app.riskScore >= 50) {
                count++;
            }
        }
        return count;
    }

    private List<AppCameraRisk> findAppsRequestingCamera() {
        PackageManager packageManager = getPackageManager();
        List<ApplicationInfo> installedApps = packageManager.getInstalledApplications(PackageManager.GET_META_DATA);
        List<AppCameraRisk> cameraApps = new ArrayList<>();

        for (ApplicationInfo appInfo : installedApps) {
            try {
                PackageInfo packageInfo = packageManager.getPackageInfo(appInfo.packageName, PackageManager.GET_PERMISSIONS);
                List<String> permissions = packageInfo.requestedPermissions == null
                    ? Collections.emptyList()
                    : Arrays.asList(packageInfo.requestedPermissions);

                if (!permissions.contains(Manifest.permission.CAMERA)) {
                    continue;
                }

                String appName = packageManager.getApplicationLabel(appInfo).toString();
                boolean systemApp = (appInfo.flags & ApplicationInfo.FLAG_SYSTEM) != 0;
                cameraApps.add(scoreApp(appName, appInfo.packageName, permissions, systemApp));
            } catch (PackageManager.NameNotFoundException ignored) {
                // Package was removed while scanning.
            }
        }
        return cameraApps;
    }

    private List<AppCameraRisk> findRiskyInstalledApps() {
        PackageManager packageManager = getPackageManager();
        List<ApplicationInfo> installedApps = packageManager.getInstalledApplications(PackageManager.GET_META_DATA);
        List<AppCameraRisk> riskyApps = new ArrayList<>();

        for (ApplicationInfo appInfo : installedApps) {
            try {
                PackageInfo packageInfo = packageManager.getPackageInfo(appInfo.packageName, PackageManager.GET_PERMISSIONS);
                List<String> permissions = packageInfo.requestedPermissions == null
                    ? Collections.emptyList()
                    : Arrays.asList(packageInfo.requestedPermissions);
                AppCameraRisk risk = scoreInstalledApp(
                    packageManager.getApplicationLabel(appInfo).toString(),
                    appInfo.packageName,
                    permissions,
                    (appInfo.flags & ApplicationInfo.FLAG_SYSTEM) != 0
                );
                if (risk.riskScore >= 35) {
                    riskyApps.add(risk);
                }
            } catch (PackageManager.NameNotFoundException ignored) {
                // Package was removed while scanning.
            }
        }

        Collections.sort(riskyApps, (left, right) -> {
            int riskCompare = Integer.compare(right.riskScore, left.riskScore);
            if (riskCompare != 0) {
                return riskCompare;
            }
            return left.appName.compareToIgnoreCase(right.appName);
        });
        return riskyApps;
    }

    private AppCameraRisk scoreApp(String appName, String packageName, List<String> permissions, boolean systemApp) {
        int score = systemApp ? 10 : 20;
        List<String> reasons = new ArrayList<>();
        reasons.add("camera");

        if (permissions.contains(Manifest.permission.RECORD_AUDIO)) {
            score += 20;
            reasons.add("microphone");
        }
        if (permissions.contains(Manifest.permission.READ_SMS) || permissions.contains(Manifest.permission.SEND_SMS)) {
            score += 20;
            reasons.add("SMS");
        }
        if (permissions.contains("android.permission.SYSTEM_ALERT_WINDOW")) {
            score += 18;
            reasons.add("overlay");
        }
        if (permissions.contains("android.permission.BIND_ACCESSIBILITY_SERVICE")) {
            score += 24;
            reasons.add("accessibility");
        }
        if (permissions.contains("android.permission.REQUEST_INSTALL_PACKAGES")) {
            score += 18;
            reasons.add("APK installs");
        }
        if (permissions.contains(Manifest.permission.ACCESS_FINE_LOCATION)) {
            score += 12;
            reasons.add("precise location");
        }

        return new AppCameraRisk(appName, packageName, Math.min(score, 100), reasons);
    }

    private AppCameraRisk scoreInstalledApp(String appName, String packageName, List<String> permissions, boolean systemApp) {
        int score = systemApp ? 0 : 8;
        List<String> reasons = new ArrayList<>();

        if (permissions.contains(Manifest.permission.READ_SMS) || permissions.contains(Manifest.permission.SEND_SMS) || permissions.contains(Manifest.permission.RECEIVE_SMS)) {
            score += 22;
            reasons.add("SMS");
        }
        if (permissions.contains("android.permission.SYSTEM_ALERT_WINDOW")) {
            score += 20;
            reasons.add("overlay");
        }
        if (permissions.contains("android.permission.BIND_ACCESSIBILITY_SERVICE")) {
            score += 28;
            reasons.add("accessibility");
        }
        if (permissions.contains("android.permission.REQUEST_INSTALL_PACKAGES")) {
            score += 18;
            reasons.add("APK installs");
        }
        if (permissions.contains(Manifest.permission.CAMERA) && permissions.contains(Manifest.permission.RECORD_AUDIO)) {
            score += 16;
            reasons.add("camera + microphone");
        }
        if (permissions.contains(Manifest.permission.ACCESS_FINE_LOCATION) || permissions.contains(Manifest.permission.ACCESS_BACKGROUND_LOCATION)) {
            score += 10;
            reasons.add("location");
        }
        if (permissions.contains("android.permission.READ_EXTERNAL_STORAGE") || permissions.contains("android.permission.MANAGE_EXTERNAL_STORAGE")) {
            score += 10;
            reasons.add("storage");
        }
        if (reasons.isEmpty()) {
            reasons.add("no high-risk marker");
        }
        return new AppCameraRisk(appName, packageName, Math.min(score, 100), reasons);
    }

    private String joinReasons(List<String> reasons) {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < reasons.size(); i++) {
            if (i > 0) {
                builder.append(", ");
            }
            builder.append(reasons.get(i));
        }
        return builder.toString();
    }

    private Button primaryButton(String label, View.OnClickListener listener) {
        Button button = smallButton(label, listener);
        button.setTextColor(Color.WHITE);
        button.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        button.setBackground(round(ACCENT, ACCENT, 8));
        return button;
    }

    private Button outlineButton(String label, View.OnClickListener listener) {
        Button button = smallButton(label, listener);
        button.setTextColor(Color.parseColor(INK));
        button.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        button.setBackground(round(PANEL, LINE, 8));
        return button;
    }

    private Button smallButton(String label, View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(label);
        button.setAllCaps(false);
        button.setTextSize(13);
        button.setPadding(dp(8), 0, dp(8), 0);
        button.setOnClickListener(listener);
        return button;
    }

    private TextView text(String value, int sp, String color, boolean bold) {
        TextView textView = new TextView(this);
        textView.setText(value);
        textView.setTextSize(sp);
        textView.setTextColor(Color.parseColor(color));
        if (bold) {
            textView.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        }
        textView.setLineSpacing(0, 1.08f);
        return textView;
    }

    private GradientDrawable round(String fill, String stroke, int radius) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(Color.parseColor(fill));
        drawable.setCornerRadius(dp(radius));
        drawable.setStroke(dp(1), Color.parseColor(stroke));
        return drawable;
    }

    private LinearLayout horizontalRow() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        return row;
    }

    private LinearLayout.LayoutParams matchWrap() {
        return new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
    }

    private LinearLayout.LayoutParams marginTop(LinearLayout.LayoutParams params, int top) {
        params.setMargins(params.leftMargin, dp(top), params.rightMargin, params.bottomMargin);
        return params;
    }

    private LinearLayout.LayoutParams weightCell() {
        return new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1);
    }

    private LinearLayout.LayoutParams weightCellWithLeft() {
        LinearLayout.LayoutParams params = weightCell();
        params.setMargins(dp(10), 0, 0, 0);
        return params;
    }

    private void openPrivacySettings() {
        openIntent(new Intent(Settings.ACTION_PRIVACY_SETTINGS));
    }

    private void openCameraPermissionManager() {
        Intent intent = new Intent("android.settings.MANAGE_APP_PERMISSION");
        intent.putExtra("android.intent.extra.PERMISSION_NAME", Manifest.permission.CAMERA);
        openIntent(intent);
    }

    private void openInstalledAppsSettings() {
        openIntent(new Intent(Settings.ACTION_APPLICATION_SETTINGS));
    }

    private void openAppDetails(String packageName) {
        Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
        intent.setData(Uri.parse("package:" + packageName));
        openIntent(intent);
    }

    private void openIntent(Intent intent) {
        try {
            startActivity(intent);
        } catch (ActivityNotFoundException ignored) {
            startActivity(new Intent(Settings.ACTION_SETTINGS));
        }
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private static final class Finding {
        final String title;
        final String body;
        final String packageName;

        Finding(String title, String body, String packageName) {
            this.title = title;
            this.body = body;
            this.packageName = packageName;
        }
    }

    private static final class ScanData {
        final String title;
        final String summary;
        final String badge;
        final String badgeColor;
        final String badgeBg;
        final String input;
        final List<Finding> findings;
        final List<String> actions;
        final int privacyScore;
        final int securityScore;
        final int threatScore;
        final int permissionScore;
        final int exposureScore;

        ScanData(String title, String summary, String badge, String badgeColor, String badgeBg, String input, List<Finding> findings, List<String> actions, int privacyScore, int securityScore, int threatScore, int permissionScore, int exposureScore) {
            this.title = title;
            this.summary = summary;
            this.badge = badge;
            this.badgeColor = badgeColor;
            this.badgeBg = badgeBg;
            this.input = input;
            this.findings = findings;
            this.actions = actions;
            this.privacyScore = privacyScore;
            this.securityScore = securityScore;
            this.threatScore = threatScore;
            this.permissionScore = permissionScore;
            this.exposureScore = exposureScore;
        }
    }

    private static final class MediaScanResult {
        final int riskScore;
        final int skinPercent;
        final int framesScanned;

        MediaScanResult(int riskScore, int skinPercent, int framesScanned) {
            this.riskScore = riskScore;
            this.skinPercent = skinPercent;
            this.framesScanned = framesScanned;
        }
    }

    private static final class MediaBatchResult {
        final List<Finding> findings;
        final int maxScore;

        MediaBatchResult(List<Finding> findings, int maxScore) {
            this.findings = findings;
            this.maxScore = maxScore;
        }
    }

    private static final class AppCameraRisk {
        final String appName;
        final String packageName;
        final int riskScore;
        final List<String> reasons;

        AppCameraRisk(String appName, String packageName, int riskScore, List<String> reasons) {
            this.appName = appName;
            this.packageName = packageName;
            this.riskScore = riskScore;
            this.reasons = reasons;
        }
    }

    private static final class SmsThreat {
        final String sender;
        final int score;
        final List<String> reasons;
        final String preview;

        SmsThreat(String sender, int score, List<String> reasons, String preview) {
            this.sender = sender;
            this.score = score;
            this.reasons = reasons;
            this.preview = preview;
        }
    }
}
