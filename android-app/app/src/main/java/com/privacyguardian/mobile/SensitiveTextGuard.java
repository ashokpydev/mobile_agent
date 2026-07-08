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
    private static final Pattern IFSC = Pattern.compile("\\b[A-Z]{4}0[A-Z0-9]{6}\\b");
    private static final Pattern CRYPTO_WALLET = Pattern.compile("\\b(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\\b");
    private static final Pattern SECRET = Pattern.compile("\\b(?:cvv|api[_-]?key|token|secret|seed phrase|recovery phrase)\\b", Pattern.CASE_INSENSITIVE);

    private SensitiveTextGuard() {}

    static boolean containsOtp(String value) {
        return OTP.matcher(value).find();
    }

    static boolean containsSensitiveData(String value) {
        return OTP.matcher(value).find()
            || EMAIL.matcher(value).find()
            || PHONE.matcher(value).find()
            || AADHAAR.matcher(value).find()
            || PAN.matcher(value).find()
            || IFSC.matcher(value).find()
            || CRYPTO_WALLET.matcher(value).find()
            || containsValidCard(value)
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
        if (IFSC.matcher(value).find()) labels.add("IFSC");
        if (CRYPTO_WALLET.matcher(value).find()) labels.add("crypto wallet");
        if (containsValidCard(value)) labels.add("payment card");
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
        redacted = IFSC.matcher(redacted).replaceAll("[REDACTED_IFSC]");
        redacted = CRYPTO_WALLET.matcher(redacted).replaceAll("[REDACTED_WALLET]");
        redacted = redactValidCards(redacted);
        return redacted.replace('\n', ' ').replace('|', '/');
    }

    /** Only treat a 13-19 digit run as a card number if it also passes the Luhn checksum,
     * otherwise phone numbers and order IDs of the same length get misclassified as cards. */
    private static boolean containsValidCard(String value) {
        java.util.regex.Matcher matcher = CARD.matcher(value);
        while (matcher.find()) {
            if (passesLuhn(matcher.group())) {
                return true;
            }
        }
        return false;
    }

    private static String redactValidCards(String value) {
        java.util.regex.Matcher matcher = CARD.matcher(value);
        StringBuilder result = new StringBuilder();
        int lastEnd = 0;
        while (matcher.find()) {
            result.append(value, lastEnd, matcher.start());
            result.append(passesLuhn(matcher.group()) ? "[REDACTED_CARD]" : matcher.group());
            lastEnd = matcher.end();
        }
        result.append(value.substring(lastEnd));
        return result.toString();
    }

    private static boolean passesLuhn(String candidate) {
        int[] digits = candidate.chars().filter(Character::isDigit).map(Character::getNumericValue).toArray();
        if (digits.length < 13 || digits.length > 19) {
            return false;
        }
        int sum = 0;
        for (int i = 0; i < digits.length; i++) {
            int digit = digits[digits.length - 1 - i];
            if (i % 2 == 1) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }
            sum += digit;
        }
        return sum % 10 == 0;
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
