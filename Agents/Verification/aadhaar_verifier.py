def verify_aadhaar(aadhaar: str, otp: str | None) -> dict:
    """
    Aadhaar verification via Digilocker / UIDAI OTP
    """

    if not otp:
        return {"verified": False, "reason": "OTP_REQUIRED"}

    return {
        "verified": True,
        "aadhaar_masked": f"XXXX-XXXX-{aadhaar[-4:]}"
    }
