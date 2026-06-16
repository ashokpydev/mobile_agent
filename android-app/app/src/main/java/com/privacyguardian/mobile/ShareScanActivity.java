package com.privacyguardian.mobile;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Toast;

public class ShareScanActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        CharSequence shared = getIntent().getCharSequenceExtra(Intent.EXTRA_TEXT);
        if (shared != null) {
            ScanHistory.append(this, "shared-text", "Received", 0, shared.toString());
            Toast.makeText(this, "Shared text captured in SentryNet history", Toast.LENGTH_LONG).show();
        }
        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
        startActivity(intent);
        finish();
    }
}
