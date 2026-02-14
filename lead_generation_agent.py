import json
import time
import uuid
from datetime import datetime

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
🏦 SYSTEM PROMPT — LEAD GENERATION & CRM INTAKE AGENT

(Pre-Sales | Growth | CRM Automation)

Role & Identity

You are LeadGenerationAgent, an AI agent responsible for capturing, qualifying, scoring, and routing loan leads at the very start of the banking funnel.

You operate as a bank’s digital front desk + CRM intake system.

You are NOT a sales agent, NOT an underwriting agent, and NOT a customer-care agent.

Your job is to observe, classify, and record intent — not to explain, persuade, or decide.

Position in the Loan Pipeline
User
 ↓
LEAD GENERATION AGENT (YOU)
 ↓
Sales Agent
 ↓
Verification Agent
 ↓
Underwriting Agent
 ↓
Sanction Agent


You may also run in parallel to Sales for CRM tracking.

CORE OBJECTIVES

Your objectives are to:

Capture every potential lead

Understand user intent & readiness

Qualify and score the lead internally

Store lead data in CRM

Route the lead correctly

Enable consent-based re-engagement

No lead should be lost.

WHAT YOU MUST CAPTURE (MANDATORY)
1️⃣ Lead Identity (If Available)

Name (if user provides)

Contact permission status

Channel (chat / web / app)

2️⃣ Loan Intent

Identify and tag:

Loan type (education / home / personal / business / unsure)

Urgency (immediate / researching / future)

Purpose (if stated)

3️⃣ Conversational Signals

Infer and store:

Tone (casual / formal)

Sentiment (positive / neutral / hesitant)

Engagement level (fast / slow / dropped)

Confidence level (high / medium / low)

These are internal signals only.

ALLOWED FUNCTIONS (WHAT YOU CAN DO)
✅ A. Lead Qualification (Light)

Classify leads into:

Hot / Warm / Cold

Urgent / Exploratory

Info-seeking / Price-sensitive

This is classification, not persuasion.

✅ B. Lead Scoring (Internal Only)

You may compute a lead score using:

Clarity of intent

Response speed

Urgency keywords

Loan type complexity

⚠️ Never show this score to the user.

✅ C. CRM Storage

Persist the following:

Lead metadata

Conversation summary

Qualification tags

Drop-off reasons (if any)

Every interaction must leave a CRM trail.

✅ D. Drop-Off Reason Capture

If a user disengages or says:

“Just checking”

“Not now”

“Too expensive”

You must:

Capture the reason

Store it

Enable future re-entry

✅ E. Consent-Based Re-Engagement

You may:

Ask permission to notify later

Schedule reminders

Trigger alerts (rate drop, eligibility change)

Example:

“Would you like me to notify you if there’s a better offer later?”

No pressure. Consent only.

✅ F. Channel & Agent Routing

You may route:

Qualified leads → Sales Agent

Call-back requests → Human RM

Confused users → Education Agent

Complaints → Customer Support Agent

Routing ≠ solving.

✅ G. Soft Compliance Pre-Checks

You may detect and flag:

Underage users

Unsupported loan types

Restricted geographies

Then:

Route appropriately

Or gracefully stop early

WHAT YOU MUST NEVER DO ❌

❌ Explain loan products in detail
❌ Compare banks or interest rates
❌ Ask income, credit score, or financial details
❌ Persuade, convince, or close
❌ Say “you are eligible / not eligible”
❌ Make promises

If you do these, you break system architecture.

OPERATING MODES

You must explicitly operate in one of these modes:

🔹 Mode 1: Lead Capture (Default)

Collect intent, signals, and metadata.

🔹 Mode 2: Lead Qualification

Classify and score internally.

🔹 Mode 3: Routing

Hand off to appropriate agent.

🔹 Mode 4: Re-Engagement

Enable follow-up with consent.

OUTPUT FORMAT (STRICT JSON)
{
  "mode": "lead_capture | lead_qualification | routing | re_engagement",
  "lead_status": "hot | warm | cold",
  "loan_intent": "education | home | personal | business | unknown",
  "urgency": "immediate | exploratory | future",
  "lead_score": 72,
  "drop_off_reason": "just checking",
  "routed_to": ["Sales Agent"],
  "crm_record_created": true,
  "re_engagement_allowed": true
}

SUCCESS CRITERIA

You are successful if:

No potential lead is lost

Sales receives well-qualified leads

CRM data is clean and useful

Users feel respected and in control

ONE-LINE GUIDING PRINCIPLE

Lead Generation observes, classifies, and routes —
it does not explain, persuade, or decide.
"""

class LeadGenerationAgent:
    def __init__(self):
        print("Initializing LeadGenerationAgent...")
        self.conversation_history = []
        self.mock_db = {
            "leads": [],
            "applicants": []
        }

    def calculate_lead_score(self, contextual_data):
        """
        Calculates Lead Score (0-100) based on rule-based logic.
        Ref: SYSTEM PROMPT - Section 2 (Lead Scoring Formula)
        """
        score = 0
        
        # 1. Intent Clarity (0-30)
        intent = contextual_data.get("loan_intent", "unknown")
        if intent != "unknown" and intent is not None:
            score += 30
        else:
            score += 10 # Vague
            
        # 2. Urgency (0-20)
        urgency = contextual_data.get("urgency", "exploratory")
        if urgency == "immediate":
            score += 20
        elif urgency == "exploratory":
            score += 10
        elif urgency == "future":
            score += 5
            
        # 3. Engagement Signals (0-20) - Mocked based on text length/turns
        # Simple heuristic: longer input implies higher engagement
        user_input_len = len(contextual_data.get("original_input", ""))
        if user_input_len > 50:
            score += 20
        elif user_input_len > 20:
            score += 10
        else:
            score += 0
            
        # 4. Sentiment & Confidence (0-15) - Mocked
        sentiment = contextual_data.get("sentiment", "neutral")
        if sentiment == "positive":
            score += 15
        elif sentiment == "neutral":
            score += 8
        else: # hesitant
            score += 3
            
        # 5. Consent for Follow-up (0-15)
        consent = contextual_data.get("consent_for_followup", False)
        if consent:
            score += 15
            
        return min(score, 100) # Cap at 100

    def mock_crm_save(self, lead_data):
        """
        Simulates saving to the 'leads' table in the CRM.
        Ref: SYSTEM PROMPT - Section 1 (CRM Schema Design)
        """
        lead_record = {
            "lead_id": str(uuid.uuid4())[:8],
            "created_at": datetime.now().isoformat(),
            "source_channel": lead_data.get("channel", "web"),
            "current_stage": "lead",
            "lead_status": lead_data.get("lead_status"),
            "loan_intent": lead_data.get("loan_intent"),
            "urgency": lead_data.get("urgency"),
            "lead_score": lead_data.get("lead_score"),
            "drop_off_reason": lead_data.get("drop_off_reason"),
            "assigned_agent": None if not lead_data.get("routed_to") else "SalesAgent"
        }
        self.mock_db["leads"].append(lead_record)
        print(f"\n[CRM] Saved Lead Record: {json.dumps(lead_record, indent=2)}")
        return lead_record["lead_id"]

    def run(self, user_input, context_data=None):
        """
        Simulates the agent processing a request.
        """
        print(f"\n[USER INPUT]: {user_input}")
        
        # --- MOCK NLP/NLU LOGIC ---
        # In production, this would be the LLM API call
        
        response = {}
        context_extracted = {
            "original_input": user_input,
            "channel": "web",
            "consent_for_followup": False,
            "sentiment": "neutral"
        }

        # Analysis based on keywords
        user_input_lower = user_input.lower()
        
        # Determine Intent
        if "home loan" in user_input_lower:
            context_extracted["loan_intent"] = "home"
        elif "education" in user_input_lower:
            context_extracted["loan_intent"] = "education"
        elif "business" in user_input_lower:
            context_extracted["loan_intent"] = "business"
        else:
            context_extracted["loan_intent"] = "unknown"

        # Determine Urgency
        if "now" in user_input_lower or "urgent" in user_input_lower or "fast" in user_input_lower:
            context_extracted["urgency"] = "immediate"
        elif "checking" in user_input_lower or "rates" in user_input_lower:
             context_extracted["urgency"] = "exploratory"
        else:
             context_extracted["urgency"] = "future"
             
        # Determine Sentiment
        if "great" in user_input_lower or "want" in user_input_lower:
            context_extracted["sentiment"] = "positive"
        elif "expensive" in user_input_lower or "unsure" in user_input_lower:
            context_extracted["sentiment"] = "hesitant"

        # Logic Branching
        if "complaint" in user_input_lower or "support" in user_input_lower:
             # Mode 3: Routing (Support)
             response = {
                "mode": "routing",
                "lead_status": "cold",
                "loan_intent": "unknown",
                "urgency": "immediate",
                "lead_score": 0, # Not a sales lead
                "drop_off_reason": None,
                "routed_to": ["Customer Support Agent"],
                "crm_record_created": True,
                "re_engagement_allowed": True
            }
             context_extracted["lead_status"] = "cold"
             
        elif "checking" in user_input_lower and "just" in user_input_lower:
            # Mode 4: Re-Engagement / Drop-off
            response = {
                "mode": "re_engagement",
                "lead_status": "cold",
                "loan_intent": context_extracted["loan_intent"],
                "urgency": "exploratory",
                "lead_score": 20, # Low score
                "drop_off_reason": "just checking",
                "routed_to": [],
                "crm_record_created": True,
                "re_engagement_allowed": True
            }
            context_extracted["lead_status"] = "cold"
            context_extracted["drop_off_reason"] = "just checking"
            
        else:
            # Mode 1 & 2: Capture & Qualify
            # Calculate Score
            score = self.calculate_lead_score(context_extracted)
            context_extracted["lead_score"] = score
            
            # Helper to determine HOT/WARM/COLD
            if score > 60:
                status = "hot"
                routing = ["Sales Agent"]
            elif score > 30:
                status = "warm"
                routing = []
            else:
                status = "cold"
                routing = []

            context_extracted["lead_status"] = status
            
            response = {
                "mode": "qualification",
                "lead_status": status,
                "loan_intent": context_extracted["loan_intent"],
                "urgency": context_extracted["urgency"],
                "lead_score": score,
                "drop_off_reason": None,
                "routed_to": routing,
                "crm_record_created": True,
                "re_engagement_allowed": True
            }

        # Mock CRM Save
        context_extracted.update(response) # Merge response data
        self.mock_crm_save(context_extracted)
        
        print("\n[AGENT OUTPUT]:")
        print(json.dumps(response, indent=2))
        return response

if __name__ == "__main__":
    agent = LeadGenerationAgent()
    
    # Test Case 1: Hot Lead
    agent.run("I need a home loan right now, it's urgent.")
    
    # Test Case 2: Exploratory / Drop-off
    agent.run("I'm just checking interest rates for education loans.")
    
    # Test Case 3: Routing to Support
    agent.run("Connect me to customer support, I have a complaint.")



# ============================================================================
# MASTER AGENT ENTRY POINT (REQUIRED)
# ============================================================================

_lead_agent_instance = LeadGenerationAgent()

def handle_lead(user_message: str):
    """
    Entry point used by Master Agent
    """
    return _lead_agent_instance.run(user_message)

