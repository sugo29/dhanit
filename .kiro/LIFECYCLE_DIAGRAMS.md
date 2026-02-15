# Dhanit - Crystal-Clear Lifecycle Diagrams

## 🎯 Happy Path vs Failure Path

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HAPPY PATH (Green)                              │
│                        FAILURE PATH (Red)                               │
└─────────────────────────────────────────────────────────────────────────┘

                            USER INQUIRY
                                 ↓
                        ┌────────────────┐
                        │ LEAD GENERATION│
                        │   (Qualify)    │
                        └────────────────┘
                         ↓              ↓
                    [Qualified]    [Not Qualified]
                         ↓              ↓
                    ┌─────────┐    ┌─────────┐
                    │  SALES  │    │ NURTURE │
                    │ (Advise)│    │  (CRM)  │
                    └─────────┘    └─────────┘
                         ↓
                  [Ready for KYC]
                         ↓
                  ┌──────────────┐
                  │ VERIFICATION │
                  │    (KYC)     │
                  └──────────────┘
                   ↓            ↓
              [Verified]   [Failed]
                   ↓            ↓
            ┌──────────────┐  ┌─────────┐
            │ UNDERWRITING │  │ SUPPORT │
            │ (Risk Score) │  │ (Help)  │
            └──────────────┘  └─────────┘
                   ↓
        ┌──────────┼──────────┐
        ↓          ↓          ↓
   [Approved] [Borderline] [Rejected]
        ↓          ↓          ↓
   ┌─────────┐ ┌────────┐ ┌──────────┐
   │SANCTION │ │MANUAL  │ │ REJECTED │
   │         │ │REVIEW  │ │  (End)   │
   └─────────┘ └────────┘ └──────────┘
        ↓          ↓
        │    [Officer Decision]
        │          ↓
        │    ┌─────┴──────┐
        │    ↓            ↓
        │ [Approved]  [Rejected]
        │    ↓            ↓
        └────┤       ┌──────────┐
             ↓       │ REJECTED │
      ┌────────────┐ │  (End)   │
      │ ACCEPTANCE │ └──────────┘
      │ (Customer) │
      └────────────┘
             ↓
      ┌──────┴──────┐
      ↓             ↓
  [Accepted]   [Rejected]
      ↓             ↓
┌──────────────┐ ┌──────────┐
│ DISBURSEMENT │ │ REJECTED │
│   (Fund)     │ │  (End)   │
└──────────────┘ └──────────┘
      ↓
┌──────────────┐
│  DISBURSED   │
│ (Active Loan)│
└──────────────┘
```

---

## 📊 Stage-by-Stage Breakdown

### Stage 1: Lead Generation

```
User: "I need an education loan"
         ↓
┌─────────────────────────────┐
│   LEAD GENERATION AGENT     │
├─────────────────────────────┤
│ • Capture intent            │
│ • Calculate lead score      │
│ • Classify: Hot/Warm/Cold   │
└─────────────────────────────┘
         ↓
    Lead Score?
    ├─ >60 (Hot) → Sales Agent
    ├─ 30-60 (Warm) → CRM Nurture
    └─ <30 (Cold) → Re-engagement
```

**Success Criteria:** Lead score > 30  
**Failure Path:** Cold leads → CRM for future engagement  
**Time:** <1 minute

---

### Stage 2: Sales & Advisory

```
User: "What loans are available?"
         ↓
┌─────────────────────────────┐
│      SALES AGENT            │
├─────────────────────────────┤
│ • Identify loan type        │
│ • Pre-eligibility check     │
│ • RAG for policy queries    │
│ • Present offers            │
└─────────────────────────────┘
         ↓
    Ready for KYC?
    ├─ Yes → Verification Agent
    ├─ Need more info → Continue conversation
    └─ Not interested → CRM
```

**Success Criteria:** User provides complete info (income, employment, amount)  
**Failure Path:** User drops off → Lead nurturing  
**Time:** 5-15 minutes

---

### Stage 3: Verification (KYC)

```
User: Submits PAN, Aadhaar, docs
         ↓
┌─────────────────────────────┐
│   VERIFICATION AGENT        │
├─────────────────────────────┤
│ • PAN verification (API)    │
│ • Aadhaar verification (OTP)│
│ • AML screening             │
│ • Document validation       │
└─────────────────────────────┘
         ↓
    All checks pass?
    ├─ Yes → Underwriting Agent
    ├─ Partial → Request more docs
    └─ Failed → Support Agent
```

**Success Criteria:** PAN ✓, Aadhaar ✓, AML ✓  
**Failure Path:** Verification fails → Support ticket  
**Time:** 2-5 minutes (API calls)

---

### Stage 4: Underwriting (Risk Assessment)

```
System: Pulls credit score, calculates risk
         ↓
┌─────────────────────────────┐
│   UNDERWRITING AGENT        │
├─────────────────────────────┤
│ • Fetch CIBIL score         │
│ • Calculate FOIR            │
│ • Apply bank policies       │
│ • Generate risk score       │
│ • Make decision             │
└─────────────────────────────┘
         ↓
    Decision?
    ├─ Approved → Sanction Agent
    ├─ Conditional → Sanction with conditions
    ├─ Policy Deviation → Manual Review
    └─ Rejected → Rejection flow
```

**Success Criteria:** Meets bank policy (score, FOIR, etc.)  
**Failure Path:** Rejected → Notify customer with reason  
**Time:** 1-2 minutes

---

### Stage 4A: Manual Review (if needed)

```
System: Escalates to credit officer
         ↓
┌─────────────────────────────┐
│   MANUAL REVIEW QUEUE       │
├─────────────────────────────┤
│ • Credit officer reviews    │
│ • Sees AI recommendation    │
│ • Can approve/reject        │
│ • Must provide reason       │
└─────────────────────────────┘
         ↓
    Officer Decision?
    ├─ Approved → Sanction Agent
    ├─ Rejected → Rejection flow
    └─ Need more info → Back to customer
```

**Success Criteria:** Officer approves with reason  
**Failure Path:** Officer rejects → Notify customer  
**Time:** 2-24 hours (SLA)

---

### Stage 5: Sanction

```
System: Generates sanction letter
         ↓
┌─────────────────────────────┐
│     SANCTION AGENT          │
├─────────────────────────────┤
│ • Generate letter (PDF)     │
│ • Include terms & conditions│
│ • Set validity (90 days)    │
│ • Send to customer          │
└─────────────────────────────┘
         ↓
    Sanction issued
         ↓
    Customer Acceptance Agent
```

**Success Criteria:** Letter generated and sent  
**Failure Path:** Generation fails → Retry or manual  
**Time:** <1 minute

---

### Stage 6: Customer Acceptance

```
User: Reviews sanction offer
         ↓
┌─────────────────────────────┐
│  CUSTOMER ACCEPTANCE AGENT  │
├─────────────────────────────┤
│ • Present final terms       │
│ • Show EMI schedule         │
│ • Offer: Accept/Reject      │
│ • Lock terms if accepted    │
└─────────────────────────────┘
         ↓
    Customer Decision?
    ├─ Accept → Disbursement Agent
    ├─ Reject → CRM re-engagement
    ├─ Clarify → Support Agent
    └─ Modify → Credit Officer
```

**Success Criteria:** Customer accepts offer  
**Failure Path:** Customer rejects → Update CRM  
**Time:** Customer-dependent (up to 90 days)

---

### Stage 7: Disbursement

```
System: Orchestrates fund transfer
         ↓
┌─────────────────────────────┐
│   DISBURSEMENT AGENT        │
├─────────────────────────────┤
│ • Pre-disbursement checks   │
│ • Generate loan account #   │
│ • Create EMI schedule       │
│ • Trigger disbursement      │
│ • Send confirmation         │
└─────────────────────────────┘
         ↓
    Disbursement Success?
    ├─ Yes → Loan Active
    ├─ Failed → Retry (3x)
    └─ Still Failed → Manual intervention
```

**Success Criteria:** Fund transfer successful  
**Failure Path:** Disbursement fails → Operations team  
**Time:** 1-2 days (CBS processing)

---

### Stage 8: Active Loan

```
┌─────────────────────────────┐
│      DISBURSED              │
├─────────────────────────────┤
│ • Loan account active       │
│ • EMI schedule available    │
│ • Customer can view details │
│ • Repayment tracking (Phase2)│
└─────────────────────────────┘
```

**Success Criteria:** Loan disbursed, customer notified  
**Future:** Repayment tracking, EMI collection

---

## 🆘 Support Agent (Available at ANY Stage)

```
User: "Why is my application delayed?"
         ↓
┌─────────────────────────────┐
│  CUSTOMER SUPPORT AGENT     │
├─────────────────────────────┤
│ • Detect complaint intent   │
│ • Classify issue type       │
│ • Create ticket (P1-P4)     │
│ • Route to team             │
│ • Track SLA                 │
└─────────────────────────────┘
         ↓
    Ticket Lifecycle
    Open → Assigned → In Progress 
    → Resolved → Closed
         ↓
    SLA Breach? → Auto-escalate
```

---

## 📈 Conversion Funnel

```
100 Leads
  ↓ 70% qualify
70 Sales Conversations
  ↓ 85% ready for KYC
60 Verifications
  ↓ 95% pass
57 Underwriting
  ↓ 60% approved (10% manual review)
34 Sanctions
  ↓ 96% accepted
33 Disbursements
  ↓ 98% successful
32 Active Loans

Overall Conversion: 32% (Lead to Disbursement)
```

---

## ⏱️ Timeline View

```
Day 0: User Inquiry
  ↓ <1 min
Day 0: Lead Qualified
  ↓ 5-15 min
Day 0: Sales Complete
  ↓ 2-5 min
Day 0: Verification Complete
  ↓ 1-2 min
Day 0: Underwriting Decision
  ↓ <1 min
Day 0: Sanction Issued
  ↓ Customer-dependent
Day 0-90: Customer Accepts
  ↓ 1-2 days
Day 1-2: Disbursement Complete

Total: <48 hours (excluding customer acceptance time)
```

---

## 🔄 State Transitions Matrix

| From Stage | To Stage | Trigger | Condition |
|-----------|----------|---------|-----------|
| LEAD | SALES | Qualified | Score > 30 |
| LEAD | NURTURE | Not qualified | Score ≤ 30 |
| SALES | VERIFICATION | Ready | Complete info |
| SALES | LEAD | Drop-off | User inactive |
| VERIFICATION | UNDERWRITING | Verified | All checks pass |
| VERIFICATION | SUPPORT | Failed | Verification fails |
| UNDERWRITING | SANCTION | Approved | Meets policy |
| UNDERWRITING | MANUAL_REVIEW | Borderline | Policy deviation |
| UNDERWRITING | REJECTED | Rejected | Doesn't meet policy |
| MANUAL_REVIEW | SANCTION | Approved | Officer approves |
| MANUAL_REVIEW | REJECTED | Rejected | Officer rejects |
| SANCTION | ACCEPTANCE | Issued | Letter sent |
| ACCEPTANCE | DISBURSEMENT | Accepted | Customer accepts |
| ACCEPTANCE | REJECTED | Rejected | Customer rejects |
| DISBURSEMENT | DISBURSED | Success | Fund transferred |
| DISBURSEMENT | MANUAL | Failed | After 3 retries |
| ANY | SUPPORT | Issue | Customer needs help |

---

**This is the complete visual guide to understand Dhanit's loan lifecycle at a glance.**

**Document Version:** 1.0  
**Last Updated:** February 15, 2026  
**Purpose:** Crystal-clear visual reference for judges and stakeholders
