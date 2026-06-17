package com.privacyguardian.mobile;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.regex.Pattern;

final class SensitiveTextGuard {
    private static final Pattern OTP = Pattern.compile("\\b(?:otp|one[-\\s]?time password|verification code)\\s*(?:is|:|=)?\\s*\\d{4,8}\\b", Pattern.CASE_INSENSITIVE);
    private static final Pattern EMAIL = Pattern.compile("\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b", Pattern.CASE_INSENSITIVE);
    private static final Pattern PHONE = Pattern.compile("\\b(?:\\+?\\d{1,3}[-.\\s]?)?(?:\\d{10}|\\d{5}[-.\\s]\\d{5})\\b");
    private static final Pattern AADHAAR = Pattern.compile("\\b\\d{4}\\s?\\d{4}\\s?\\d{4}\\b");
    private static final Pattern PAN = Pattern.compile("\\b[A-Z]{5}\\d{4}[A-Z]\\b", Pattern.CASE_INSENSITIVE);
    private static final Pattern CARD = Pattern.compile("\\b(?:\\d[ -]*?){13,19}\\b");
    private static final Pattern SECRET = Pattern.compile("\\b(?:cvv|api[_-]?key|token|secret|seed phrase|recovery phrase)\\b", Pattern.CASE_INSENSITIVE);

    private SensitiveTextGuard() {}

    static boolean containsSensitiveData(String value) {
        return OTP.matcher(value).find()
            || EMAIL.matcher(value).find()
            || PHONE.matcher(value).find()
            || AADHAAR.matcher(value).find()
            || PAN.matcher(value).find()
            || CARD.matcher(value).find()
            || SECRET.matcher(value).find();
    }

    static String labels(String value) {
        String lower = value.toLowerCase(Locale.US);
        List<String> labels = new ArrayList<>();
        if (OTP.matcher(value).find()) labels.add("OTP");
        if (EMAIL.matcher(value).find()) labels.add("email");
        if (PHONE.matcher(value).find()) labels.add("phone");
        if (AADHAAR.matcher(value).find()) labels.add("Aadhaar-like ID");
        if (PAN.matcher(value).find()) labels.add("PAN");
        if (CARD.matcher(value).find()) labels.add("payment card");
        if (SECRET.matcher(value).find() || lower.contains("password")) labels.add("secret");
        return labels.isEmpty() ? "none" : join(labels);
    }

    static String redact(String value) {
        String redacted = value;
        redacted = OTP.matcher(redacted).replaceAll("[REDACTED_OTP]");
        redacted = EMAIL.matcher(redacted).replaceAll("[REDACTED_EMAIL]");
        redacted = PHONE.matcher(redacted).replaceAll("[REDACTED_PHONE]");
        redacted = AADHAAR.matcher(redacted).replaceAll("[REDACTED_ID]");
        redacted = PAN.matcher(redacted).replaceAll("[REDACTED_PAN]");
        redacted = CARD.matcher(redacted).replaceAll("[REDACTED_CARD]");
        return redacted.replace('\n', ' ').replace('|', '/');
    }

    private static String join(List<String> labels) {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < labels.size(); i++) {
            if (i > 0) {
                builder.append(", ");
            }
            builder.append(labels.get(i));
        }
        return builder.toString();
    }
}
