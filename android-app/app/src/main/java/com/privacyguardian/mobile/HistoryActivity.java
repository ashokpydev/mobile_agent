package com.privacyguardian.mobile;

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import java.util.List;

public class HistoryActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setTitle("SentryNet History");
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(24, 24, 24, 32);
        scroll.addView(root);
        List<String> lines = ScanHistory.read(this);
        if (lines.isEmpty()) {
            root.addView(text("No scan history yet.", 18));
        } else {
            for (String line : lines) {
                TextView entry = text(line, 14);
                entry.setPadding(0, 10, 0, 10);
                root.addView(entry);
            }
        }
        setContentView(scroll);
    }

    private TextView text(String value, int size) {
        TextView text = new TextView(this);
        text.setText(value);
        text.setTextSize(size);
        return text;
    }
}
