package com.privacyguardian.mobile;

import android.Manifest;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class MainActivity extends Activity {
    private LinearLayout results;
    private TextView summary;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle(R.string.app_name);
        setContentView(buildContent());
        scanCameraApps();
    }

    private View buildContent() {
        ScrollView scrollView = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(20), dp(20), dp(24));
        scrollView.addView(root);

        TextView title = text("SentryNet", 26, "#17202f", true);
        root.addView(title);

        TextView subtitle = text(
            "Camera access audit for Android apps installed on this device.",
            15,
            "#647084",
            false
        );
        subtitle.setPadding(0, dp(6), 0, dp(16));
        root.addView(subtitle);

        summary = text("", 16, "#17202f", true);
        summary.setPadding(0, 0, 0, dp(14));
        root.addView(summary);

        root.addView(button("Scan camera permissions", view -> scanCameraApps()));
        root.addView(button("Open Android Privacy Dashboard", view -> openPrivacySettings()));
        root.addView(button("Open Camera Permission Manager", view -> openCameraPermissionManager()));
        root.addView(button("Open Installed Apps Settings", view -> openInstalledAppsSettings()));

        TextView note = text(
            "Android does not let a normal app reliably identify every other app using the camera right now. "
                + "Use the system green privacy indicator and Privacy Dashboard for live/recent access. "
                + "This app lists apps that request camera permission and highlights risky combinations.",
            14,
            "#4b5563",
            false
        );
        note.setPadding(0, dp(18), 0, dp(16));
        root.addView(note);

        results = new LinearLayout(this);
        results.setOrientation(LinearLayout.VERTICAL);
        root.addView(results);
        return scrollView;
    }

    private void scanCameraApps() {
        results.removeAllViews();
        List<AppCameraRisk> apps = findAppsRequestingCamera();
        Collections.sort(apps, (left, right) -> {
            int riskCompare = Integer.compare(right.riskScore, left.riskScore);
            if (riskCompare != 0) {
                return riskCompare;
            }
            return left.appName.compareToIgnoreCase(right.appName);
        });

        int highRiskCount = 0;
        for (AppCameraRisk app : apps) {
            if (app.riskScore >= 50) {
                highRiskCount++;
            }
            results.addView(appRow(app));
        }

        summary.setText(
            apps.size() + " apps request camera access. "
                + highRiskCount + " need careful review."
        );

        if (apps.isEmpty()) {
            results.addView(text("No installed apps requesting camera permission were found.", 15, "#166534", true));
        }
    }

    private List<AppCameraRisk> findAppsRequestingCamera() {
        PackageManager packageManager = getPackageManager();
        List<ApplicationInfo> installedApps = packageManager.getInstalledApplications(PackageManager.GET_META_DATA);
        List<AppCameraRisk> cameraApps = new ArrayList<>();

        for (ApplicationInfo appInfo : installedApps) {
            try {
                PackageInfo packageInfo = packageManager.getPackageInfo(
                    appInfo.packageName,
                    PackageManager.GET_PERMISSIONS
                );
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

    private AppCameraRisk scoreApp(
        String appName,
        String packageName,
        List<String> permissions,
        boolean systemApp
    ) {
        int score = systemApp ? 10 : 20;
        List<String> reasons = new ArrayList<>();
        reasons.add("Requests camera permission");

        if (permissions.contains(Manifest.permission.RECORD_AUDIO)) {
            score += 20;
            reasons.add("also requests microphone");
        }
        if (permissions.contains(Manifest.permission.READ_SMS) || permissions.contains(Manifest.permission.SEND_SMS)) {
            score += 20;
            reasons.add("also requests SMS access");
        }
        if (permissions.contains("android.permission.SYSTEM_ALERT_WINDOW")) {
            score += 18;
            reasons.add("can request screen overlays");
        }
        if (permissions.contains("android.permission.BIND_ACCESSIBILITY_SERVICE")) {
            score += 24;
            reasons.add("declares accessibility-service capability");
        }
        if (permissions.contains("android.permission.REQUEST_INSTALL_PACKAGES")) {
            score += 18;
            reasons.add("can request APK installs");
        }
        if (permissions.contains(Manifest.permission.ACCESS_FINE_LOCATION)) {
            score += 12;
            reasons.add("also requests precise location");
        }

        return new AppCameraRisk(appName, packageName, Math.min(score, 100), reasons);
    }

    private View appRow(AppCameraRisk app) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.VERTICAL);
        row.setPadding(dp(14), dp(14), dp(14), dp(14));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        );
        params.setMargins(0, 0, 0, dp(10));
        row.setLayoutParams(params);
        row.setBackgroundColor(Color.parseColor(app.riskScore >= 50 ? "#fff7ed" : "#f8fafc"));

        row.addView(text(app.appName, 17, "#17202f", true));
        row.addView(text(app.packageName, 12, "#647084", false));
        row.addView(text("Risk score: " + app.riskScore + "/100", 14, riskColor(app.riskScore), true));
        row.addView(text("Why: " + String.join(", ", app.reasons), 14, "#374151", false));
        row.addView(button("Open app settings", view -> openAppDetails(app.packageName)));
        return row;
    }

    private Button button(String label, View.OnClickListener listener) {
        Button button = new Button(this);
        button.setText(label);
        button.setAllCaps(false);
        button.setOnClickListener(listener);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        );
        params.setMargins(0, dp(5), 0, dp(5));
        button.setLayoutParams(params);
        return button;
    }

    private TextView text(String value, int sp, String color, boolean bold) {
        TextView textView = new TextView(this);
        textView.setText(value);
        textView.setTextSize(sp);
        textView.setTextColor(Color.parseColor(color));
        if (bold) {
            textView.setTypeface(textView.getTypeface(), android.graphics.Typeface.BOLD);
        }
        textView.setLineSpacing(0, 1.08f);
        return textView;
    }

    private String riskColor(int score) {
        if (score >= 70) {
            return "#b91c1c";
        }
        if (score >= 50) {
            return "#b45309";
        }
        return "#166534";
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
}
