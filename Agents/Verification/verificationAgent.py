from .pan_verifier import verify_pan
from .aadhaar_verifier import verify_aadhaar
from .aml_checker import run_aml_check


def handle_verification(context: dict) -> dict:
    """
    Called by Master Agent after Sales Agent
    """

    name = context.get("name")
    pan = context.get("pan")
    aadhaar = context.get("aadhaar")
    otp = context.get("otp")

    # Step 1: PAN
    pan_result = verify_pan(pan, name)

    if not pan_result["verified"]:
        return {
            "agent": "VERIFICATION_AGENT",
            "status": "FAILED",
            "reason": pan_result["reason"]
        }

    # Step 2: Aadhaar
    aadhaar_result = verify_aadhaar(aadhaar, otp)

    if not aadhaar_result["verified"]:
        return {
            "agent": "VERIFICATION_AGENT",
            "status": "FAILED",
            "reason": aadhaar_result["reason"]
        }

    # Step 3: AML
    aml_result = run_aml_check(name, pan)

    if aml_result["blacklisted"] or aml_result["risk_score"] > 70:
        return {
            "agent": "VERIFICATION_AGENT",
            "status": "FAILED",
            "reason": "AML_HIGH_RISK"
        }

    return {
        "agent": "VERIFICATION_AGENT",
        "status": "VERIFIED",
        "signals": {
            "kyc_completed": True,
            "aml_passed": True
        }
    }
