from intent_classifier import classify_intent
from Agents.Sales.salesAgent import handle_sales
from Agents.Verification.verificationAgent import handle_verification
from Agents.Underwriting.underWritingAgent import handle_underwriting
from sanction_agent import SanctionAgent
from lead_generation_agent import handle_lead


SESSION_STATE = {
    "stage": "LEAD",
    "verification_context": None,
    "sanction_data": None
}

sanction_agent = SanctionAgent()


def master_agent(user_message):

    # LEAD
    if SESSION_STATE["stage"] == "LEAD":
        response = handle_lead(user_message)
        SESSION_STATE["stage"] = "SALES"
        return response

    # SALES
    if SESSION_STATE["stage"] == "SALES":
        response = handle_sales(user_message)

        if response.get("signals", {}).get("ready_for_verification"):
            SESSION_STATE["stage"] = "VERIFICATION"
            SESSION_STATE["verification_context"] = response.get("data")

        return response

    # VERIFICATION
    if SESSION_STATE["stage"] == "VERIFICATION":
        response = handle_verification(SESSION_STATE["verification_context"])

        if response.get("status") == "VERIFIED":
            SESSION_STATE["stage"] = "UNDERWRITING"

        return response

    # UNDERWRITING
    if SESSION_STATE["stage"] == "UNDERWRITING":
        response = handle_underwriting(user_message)

        decision = response.get("signals", {}).get("decision")
        if decision in ["Approved", "Conditionally Approved"]:
            SESSION_STATE["stage"] = "SANCTION"
            SESSION_STATE["sanction_data"] = response.get("data")

        return response

    # SANCTION
    if SESSION_STATE["stage"] == "SANCTION":
        return sanction_agent.run(
            user_message=user_message,
            sanction_context=SESSION_STATE["sanction_data"]
        )

    return {
        "reply": "Routing to human support",
        "agent": "FALLBACK"
    }
