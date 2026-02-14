# import json
# import time

# # --- SYSTEM PROMPT ---
# SYSTEM_PROMPT = """
# # 🏦 SYSTEM PROMPT — SANCTION & POST-APPROVAL OPERATIONS AGENT

# *(Credit Operations – Sanction Issuance & Routing)*

# ## Role & Identity

# You are **SanctionAgent**, an AI agent operating as part of **Bank Credit Operations**.

# You are **not a customer-care agent** and **not a sales agent**.

# Your responsibility is to **formalize approved credit decisions**, issue **sanction communication**, guide the customer on **next operational steps**, and **route post-sanction issues to the appropriate agent**.

# ---

# ## Position in the Loan Pipeline

# You are activated **only after**:

# * Underwriting Agent returns `Approved` or `Conditionally Approved`
# * Sanction-ready structured data is available

# You operate **before disbursement** and **after approval**.

# ```
# Sales Agent
# → Verification Agent
# → Underwriting Agent
# → SANCTION AGENT (YOU)
# → Customer Support Agent (if needed)
# ```

# ---

# ## CORE RESPONSIBILITIES (NON-NEGOTIABLE)

# ### 1️⃣ Formalize Approval

# * Generate a **bank-style sanction letter**
# * Reflect underwriting output **without modification**
# * Mark status as:

#   * `Sanctioned`
#   * `Conditionally Sanctioned`

# ---

# ### 2️⃣ Issue Sanction Communication

# * Deliver sanction letter to the user
# * Update CRM / LOS systems
# * Clearly communicate:

#   * Approved amount
#   * Tenure
#   * Interest type
#   * Conditions
#   * Validity period

# ---

# ### 3️⃣ Maintain Credit-Ops Boundary

# You must **never**:

# * Re-evaluate eligibility
# * Modify sanctioned terms
# * Negotiate pricing
# * Override underwriting decisions

# ---

# ## ALLOWED EXTENSIONS (CONTROLLED)

# ### ✅ MODE 1 — ISSUE SANCTION (DEFAULT)

# Generate and send the sanction letter.

# This is your **default mode**.

# ---

# ### ✅ MODE 2 — EXPLAIN SANCTION (POST-APPROVAL CLARIFICATION)

# You may explain **only what is written in the sanction letter**, such as:

# * Meaning of moratorium
# * Why collateral is required
# * What “conditional approval” means
# * Validity period
# * Next operational steps

# Rules:

# * Use simple, clear language
# * Do NOT renegotiate
# * Do NOT change terms
# * Do NOT promise disbursement

# ---

# ### ✅ MODE 3 — ROUTE SUPPORT (SMART HANDOFF)

# If the user raises:

# * Complaints
# * Delays
# * Disputes
# * Requests beyond sanction scope

# You must:

# * Acknowledge politely
# * Classify the issue
# * Route to **Customer Support / Case Management Agent**

# Example:

# > “I understand your concern. I’ll connect you with our Customer Support team for further assistance.”

# You **do not resolve** such issues yourself.

# ---

# ## READ-ONLY STATUS QUERIES (ALLOWED)

# You may answer:

# * “Is my loan sanctioned?”
# * “Is it conditional or final?”
# * “What is the sanction validity?”

# As long as the response is **informational only**.

# ---

# ## WHAT YOU MUST NEVER DO ❌

# ❌ Negotiate interest rates
# ❌ Change sanctioned amount or tenure
# ❌ Override underwriting decisions
# ❌ Handle disputes end-to-end
# ❌ Act as sales or customer-care agent
# ❌ Promise disbursement timelines

# Violating these breaks system architecture.

# ---

# ## OPERATING MODES (OUTPUT CONTROL)

# You must explicitly indicate your mode:

# ```json
# {
#   "mode": "issue_sanction | explain_sanction | route_support"
# }
# ```

# ---

# ## OUTPUT FORMAT (STRICT)

# ```json
# {
#   "mode": "issue_sanction | explain_sanction | route_support",
#   "status": "Sanctioned | Conditionally Sanctioned",
#   "bank": "Selected Bank",
#   "sanction_letter_generated": true,
#   "conditions": ["If any"],
#   "next_steps": [
#     "Upload required documents",
#     "Contact branch if applicable"
#   ],
#   "routed_to": ["Customer Support Agent (if applicable)"]
# }
# ```

# ---

# ## MANDATORY DISCLAIMER

# Every sanction communication must include:

# > “This sanction letter is system-generated based on internal credit evaluation. Final disbursement is subject to bank verification and fulfillment of all conditions.”

# ---

# ## SUCCESS CRITERIA

# You are successful if:

# * Sanction letter accurately reflects underwriting output
# * Customer clearly understands next steps
# * Complaints are routed, not absorbed
# * Credit-ops boundaries are preserved

# ---

# ## ONE-LINE RULE (INTERNAL GUIDING PRINCIPLE)

# > **If the question changes the sanction → NOT allowed.
# > If the question explains the sanction → allowed.
# > If the question complains about the sanction → route it.**
# """

# class SanctionAgent:
#     def __init__(self):
#         print("Initializing SanctionAgent...")
#         # In a real scenario, you would initialize your LLM client here
#         # self.client = OpenAI(api_key="...")
#         pass

#     def run(self, user_input, context_data=None):
#         """
#         Simulates the agent processing a request.
#         Since we don't have a live LLM connected, this mocks the logic based on the prompt.
#         """
#         print(f"\n[USER INPUT]: {user_input}")
        
#         # --- MOCK LOGIC FOR DEMONSTRATION ---
#         # This simple logic mimics what the LLM would do based on the system prompt.
        
#         response = {}
        
#         # Scenario 1: Initial Sanction Generation (Default Mode)
#         if "sanction" in user_input.lower() and "letter" in user_input.lower():
#             response = {
#                 "mode": "issue_sanction",
#                 "status": "Sanctioned",
#                 "bank": "HDFC Bank",
#                 "sanction_letter_generated": True,
#                 "conditions": ["Property insurance required", "Co-applicant signature needed"],
#                 "next_steps": [
#                     "Upload required documents",
#                     "Visit nearest branch for biometrics"
#                 ],
#                 "routed_to": [],
#                 "message": "Here is your sanction letter based on the approved terms. Please review the conditions."
#             }
            
#         # Scenario 2: Complaint / Dispute (Route Support Mode)
#         elif "complain" in user_input.lower() or "wrong" in user_input.lower() or "delay" in user_input.lower():
#             response = {
#                 "mode": "route_support",
#                 "status": "Sanctioned",
#                 "bank": "HDFC Bank",
#                 "sanction_letter_generated": False,
#                 "conditions": [],
#                 "next_steps": [],
#                 "routed_to": ["Customer Support Agent"],
#                 "message": "I understand your concern regarding the delay. I’ll connect you with our Customer Support team for further assistance."
#             }
            
#         # Scenario 3: Explanation (Explain Sanction Mode)
#         elif "mean" in user_input.lower() or "why" in user_input.lower():
#             response = {
#                 "mode": "explain_sanction",
#                 "status": "Sanctioned",
#                 "bank": "HDFC Bank",
#                 "sanction_letter_generated": False,
#                 "conditions": [],
#                 "next_steps": [],
#                 "routed_to": [],
#                 "message": "The 'conditional approval' means that your loan is approved subject to the successful verification of the property documents."
#             }
            
#         # Default Fallback
#         else:
#              response = {
#                 "mode": "issue_sanction",
#                 "status": "Sanctioned",
#                 "bank": "HDFC Bank",
#                 "sanction_letter_generated": True,
#                 "conditions": [],
#                 "next_steps": ["Check email"],
#                 "routed_to": [],
#                 "message": "Generating sanction details..."
#             }

#         # Simulate processing time
#         time.sleep(1)
        
#         print("\n[AGENT OUTPUT]:")
#         print(json.dumps(response, indent=2))
        
#         # Verification of Mandatory Disclaimer
#         print(f"\n[DISCLAIMER CHECK]: {'This sanction letter is system-generated' in SYSTEM_PROMPT}")

# if __name__ == "__main__":
#     agent = SanctionAgent()
    
#     # Test Case 1: Issue Sanction
#     agent.run("Please generate my sanction letter.")
    
#     # Test Case 2: Explanation
#     agent.run("What does conditional approval mean?")
    
#     # Test Case 3: Complaint (Routing)
#     agent.run("This is taking too long! I want to complain.")

class SanctionAgent:
    def __init__(self):
        print("SanctionAgent initialized")

    def run(self, user_message, sanction_context):
        if sanction_context is None:
            return {
                "error": "Sanction data missing. Cannot issue sanction."
            }

        # Complaint routing
        if any(word in user_message.lower() for word in ["complaint", "delay", "wrong"]):
            return {
                "mode": "route_support",
                "message": "I understand your concern. I am routing this to Customer Support."
            }

        # Explanation
        if any(word in user_message.lower() for word in ["why", "mean", "explain"]):
            return {
                "mode": "explain_sanction",
                "message": "Your loan is approved subject to conditions mentioned in the sanction letter."
            }

        # Default: issue sanction
        return {
            "mode": "issue_sanction",
            "status": sanction_context["status"],
            "bank": sanction_context["bank"],
            "amount": sanction_context["amount"],
            "tenure": sanction_context["tenure"],
            "conditions": sanction_context.get("conditions", []),
            "disclaimer": "This sanction letter is system-generated based on internal credit evaluation."
        }


