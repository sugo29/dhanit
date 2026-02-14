def verify_pan(pan: str, name: str) -> dict:
    """
    Real-world PAN verification uses NSDL / Karza / Signzy API.
    Here we keep it API-ready.
    """

    if not pan or len(pan) != 10:
        return {"verified": False, "reason": "INVALID_PAN_FORMAT"}

    # 🔐 API call placeholder (Karza / Signzy)
    return {
        "verified": True,
        "pan": pan,
        "name_match": True
    }
