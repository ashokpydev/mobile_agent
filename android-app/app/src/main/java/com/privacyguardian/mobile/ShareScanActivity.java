package com.privacyguardian.mobile;

import android.app.Activity;
import android.app.KeyguardManager;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Toast;

public class ShareScanActivity extends Activity {
    private static final int REQUEST_CONFIRM_DEVICE_CREDENTIAL = 40;

    private String pendingSharedText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        CharSequence shared = getIntent().getCharSequenceExtra(Intent.EXTRA_TEXT);
        if (shared != null) {
            handleSharedText(shared.toString());
            return;
        }
        openMainAndFinish();
    }

    private void handleSharedText(String sharedText) {
        if (SensitiveTextGuard.containsSensitiveData(sharedText)) {
            pendingSharedText = sharedText;
            requestDeviceAuthentication();
            return;
        }
        recordSharedText(sharedText, false);
        openMainAndFinish();
    }

    private void requestDeviceAuthentication() {
        KeyguardManager keyguardManager = (KeyguardManager) getSystemService(Context.KEYGUARD_SERVICE);
        if (keyguardManager == null || !keyguardManager.isDeviceSecure()) {
            Toast.makeText(this, "Set a screen lock before sharing OTP or personal info with SentryNet.", Toast.LENGTH_LONG).show();
            openMainAndFinish();
            return;
        }
        Intent confirmIntent = keyguardManager.createConfirmDeviceCredentialIntent(
            "Authenticate to scan sensitive text",
            "OTP and personal information can be shared only after user authentication."
        );
        if (confirmIntent == null) {
            Toast.makeText(this, "Device authentication is unavailable. Sensitive text was not captured.", Toast.LENGTH_LONG).show();
            openMainAndFinish();
            return;
        }
        startActivityForResult(confirmIntent, REQUEST_CONFIRM_DEVICE_CREDENTIAL);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CONFIRM_DEVICE_CREDENTIAL) {
            if (resultCode == RESULT_OK && pendingSharedText != null) {
                recordSharedText(pendingSharedText, true);
            } else {
                Toast.makeText(this, "Authentication cancelled. Sensitive text was not captured.", Toast.LENGTH_LONG).show();
            }
            pendingSharedText = null;
            openMainAndFinish();
        }
    }

    private void recordSharedText(String sharedText, boolean authenticated) {
        String summary = authenticated
            ? "Authenticated sensitive share. Labels: " + SensitiveTextGuard.labels(sharedText) + ". Redacted: " + SensitiveTextGuard.redact(sharedText)
            : "Shared text captured. Redacted: " + SensitiveTextGuard.redact(sharedText);
        ScanHistory.append(this, "shared-text", authenticated ? "Authenticated" : "Received", 0, summary);
        Toast.makeText(this, authenticated ? "Sensitive text authenticated and redacted" : "Shared text captured in SentryNet history", Toast.LENGTH_LONG).show();
    }

    private void openMainAndFinish() {
        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
        startActivity(intent);
        finish();
    }
}
