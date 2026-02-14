def classify_intent(message):
    msg = message.lower()

    if "sanction" in msg:
        return "SANCTION_LETTER"

    if "status" in msg or "approved" in msg:
        return "UNDERWRITING"

    if "loan" in msg or "interest" in msg:
        return "LOAN_ENQUIRY"

    if "apply" in msg or "contact" in msg:
        return "LEAD"

    return "UNKNOWN"
