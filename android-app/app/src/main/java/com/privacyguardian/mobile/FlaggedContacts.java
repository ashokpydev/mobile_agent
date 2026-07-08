package com.privacyguardian.mobile;

import android.content.Context;
import android.content.SharedPreferences;

import java.util.HashSet;
import java.util.Set;
import java.util.regex.Pattern;

final class FlaggedContacts {
    private static final String PREFS = "sentrynet_flagged_contacts";
    private static final String NUMBERS_KEY = "flagged_numbers";
    private static final Pattern PHONE_LIKE = Pattern.compile("^\\+?[0-9][0-9\\-\\s]{6,14}$");

    private FlaggedContacts() {}

    static boolean looksLikePhoneNumber(String value) {
        return value != null && PHONE_LIKE.matcher(value.trim()).matches();
    }

    static void flag(Context context, String number, int score, String reason) {
        if (!looksLikePhoneNumber(number)) {
            return;
        }
        String normalized = normalize(number);
        SharedPreferences prefs = prefs(context);
        Set<String> numbers = new HashSet<>(prefs.getStringSet(NUMBERS_KEY, new HashSet<>()));
        if (numbers.add(normalized)) {
            prefs.edit().putStringSet(NUMBERS_KEY, numbers).apply();
            ScanHistory.append(context, "call-forward-flag", "Flagged", score,
                "Flagged " + normalized + " for incoming-call screening. Reason: " + reason);
        }
    }

    static boolean isFlagged(Context context, String number) {
        if (number == null) {
            return false;
        }
        return prefs(context).getStringSet(NUMBERS_KEY, new HashSet<>()).contains(normalize(number));
    }

    static Set<String> all(Context context) {
        return new HashSet<>(prefs(context).getStringSet(NUMBERS_KEY, new HashSet<>()));
    }

    static void unflag(Context context, String number) {
        SharedPreferences prefs = prefs(context);
        Set<String> numbers = new HashSet<>(prefs.getStringSet(NUMBERS_KEY, new HashSet<>()));
        numbers.remove(normalize(number));
        prefs.edit().putStringSet(NUMBERS_KEY, numbers).apply();
    }

    static void clear(Context context) {
        prefs(context).edit().remove(NUMBERS_KEY).apply();
    }

    private static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    private static String normalize(String number) {
        return number.replaceAll("[^0-9+]", "");
    }
}
