package com.privacyguardian.mobile;

import android.app.Service;
import android.content.Intent;
import android.database.ContentObserver;
import android.net.Uri;
import android.os.Handler;
import android.os.IBinder;
import android.provider.MediaStore;

public class RealtimeMonitorService extends Service {
    private ContentObserver mediaObserver;

    @Override
    public void onCreate() {
        super.onCreate();
        mediaObserver = new ContentObserver(new Handler()) {
            @Override
            public void onChange(boolean selfChange, Uri uri) {
                if (AppSettings.realtimeEnabled(RealtimeMonitorService.this)) {
                    ScanHistory.append(RealtimeMonitorService.this, "media-observer", "New media", 0, uri == null ? "Media changed" : uri.toString());
                }
            }
        };
        getContentResolver().registerContentObserver(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, true, mediaObserver);
        getContentResolver().registerContentObserver(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, true, mediaObserver);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        if (mediaObserver != null) {
            getContentResolver().unregisterContentObserver(mediaObserver);
        }
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
