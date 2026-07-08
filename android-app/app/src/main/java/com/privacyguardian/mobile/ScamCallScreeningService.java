package com.privacyguardian.mobile;

import android.net.Uri;
import android.telecom.Call;
import android.telecom.CallScreeningService;

public class ScamCallScreeningService extends CallScreeningService {
    @Override
    public void onScreenCall(Call.Details callDetails) {
        Uri handle = callDetails.getHandle();
        String number = handle == null ? null : handle.getSchemeSpecificPart();
        boolean flagged = number != null && FlaggedContacts.isFlagged(this, number);

        CallResponse.Builder response = new CallResponse.Builder();
        if (flagged) {
            response.setDisallowCall(true).setRejectCall(true).setSkipCallLog(false).setSkipNotification(false);
            ScanHistory.append(
                this,
                "call-blocked",
                "Blocked",
                90,
                "Refused an incoming call from " + number + ", a number previously flagged by SentryNet's "
                    + "message scan. Open Settings > Blocked callers and authenticate to review or unblock it."
            );
        }
        respondToCall(callDetails, response.build());
    }
}
