def run_aml_check(name: str, pan: str) -> dict:
    """
    AML / Fraud / Sanctions screening
    """

    # Real providers: Refinitiv, ComplyAdvantage, SEBI lists
    risk_score = 20  # simulate low risk

    return {
        "blacklisted": False,
        "risk_score": risk_score
    }
