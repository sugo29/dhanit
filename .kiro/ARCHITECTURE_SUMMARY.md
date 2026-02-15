# Dhanit Banking System - Architecture Summary for Judges

## 🎯 What We Built

A **production-grade AI-powered loan origination platform** that automates the **complete end-to-end loan lifecycle** from lead capture to disbursement, with human oversight, customer support, and real-time monitoring - designed as a scalable fintech startup solution.

## 🏗️ Core Architecture Strengths

### 1. Smart RAG Usage (Not RAG Everywhere)
✅ **RAG ONLY for dynamic policy data**:
- RBI circulars
- Government schemes (PMMY, Mudra)
- Interest rate updates
- Subsidy changes

❌ **NO RAG for critical decisions**:
- Loan eligibility rules → Internal DB
- Risk scoring → Deterministic engine
- Underwriting logic → Rule-based

**Why This Matters**: Compliance, explainability, speed, and accuracy. No hallucinations in credit decisions.

### 2. Master Agent Orchestration (Not Just a Chatbot)
The Master Agent does 5 things:
1. Intent Understanding
2. Context State Machine (tracks user journey)
3. Risk Pre-Screening
4. Agent Switching Logic
5. RAG Controller (decides when to use RAG)

**Why This Matters**: This is architect-level thinking, not just "build a chatbot."

### 3. Specialized Agents (Complete Lifecycle)
- **Lead Generation**: Capture and qualify leads (hot/warm/cold scoring)
- **Sales**: Product recommendation + RAG for policy questions
- **Verification**: KYC (PAN, Aadhaar, AML) with external APIs
- **Underwriting**: Deterministic risk scoring + bank policy enforcement
- **Sanction**: Letter generation and formalization
- **Customer Acceptance**: Handle acceptance/rejection of sanction offer
- **Disbursement**: Orchestrate fund transfer (simulated in MVP)
- **Customer Support**: Handle queries, complaints, and case management

**Why This Matters**: Complete end-to-end lifecycle coverage. Each agent has clear scope, inputs, outputs, and transition criteria. Easy to scale and maintain.

### 4. Human-in-the-Loop (Not Fully Automated)
```
Underwriting Decision
    ↓
Policy Deviation Detected?
    ↓ YES
Manual Credit Officer Review Queue
    ↓
Credit Manager/Regional Head Approval
    ↓
Final Decision
```

**Escalation Rules**:
- Minor deviation → Credit Manager
- Major deviation → Regional Credit Head
- Critical deviation → Chief Credit Officer
- AML flags → Compliance Officer

**Why This Matters**: Real banks need human oversight. This shows production-grade thinking.

### 5. Asynchronous Processing (Not Blocking)
```python
# Long-running operations run in background
- Document verification (PAN, Aadhaar, AML) → Celery task
- Credit bureau API calls → Async with retry
- Sanction letter generation → Background job
```

**Retry Logic**: 3 retries with exponential backoff
**Dead Letter Queue**: Failed tasks for manual review
**Event-Driven**: Stage transitions trigger next agent

**Why This Matters**: Handles API timeouts gracefully. Production systems can't block on slow APIs.

### 6. Monitoring & Observability
- **Metrics**: Prometheus-compatible (agent performance, API health, conversion rates)
- **Logging**: Structured JSON logs with session/user context
- **Analytics**: Conversion funnel, drop-off analysis, agent performance
- **Alerting**: API failures, high error rates, system downtime

**Why This Matters**: You can't improve what you don't measure. Shows operational maturity.

### 7. Role-Based Access Control (RBAC)
- **Customer**: View own application
- **Credit Officer**: Review and approve applications
- **Credit Manager**: Override AI decisions
- **Regional Head**: Approve high-value loans
- **Support Agent**: Handle tickets and customer queries
- **Admin**: Update policies, manage users

**Audit Trail**: Every access, every decision, every override logged for 7 years.

**Why This Matters**: Compliance requirement. Shows understanding of real-world banking operations.

### 8. Customer Support & Case Management
- **Ticket Creation**: Auto-generate tickets for complaints
- **SLA Tracking**: P1 (2h), P2 (8h), P3 (24h), P4 (72h)
- **Auto-Escalation**: Escalate on SLA breach
- **Ticket Lifecycle**: Open → Assigned → In Progress → Resolved → Closed
- **Integration**: Route issues to appropriate teams

**Why This Matters**: Real-world systems need customer support. Shows operational maturity.

### 9. Operational Dashboards
- **Lead Funnel**: Conversion rates, drop-off analysis
- **Application Metrics**: Processing time, bottleneck identification
- **Approval Metrics**: Approval/rejection rates, manual review queue
- **Disbursement Metrics**: Success rate, pending disbursements
- **Support Metrics**: Ticket volume, SLA compliance, CSAT
- **AI Monitoring**: RAG performance, agent metrics, decision drift

**Why This Matters**: You can't improve what you don't measure. Production systems need visibility.

## 📊 System Boundaries (What's In/Out of Scope)

### ✅ In Scope (MVP)
- 4 banks (SBI, HDFC, ICICI, Axis)
- 5 loan types (Education, Home, Personal, Vehicle, Business)
- Complete lifecycle (Lead → Sales → Verification → Underwriting → Sanction → Acceptance → Disbursement)
- AI-powered decision support with human oversight
- KYC verification (PAN, Aadhaar, AML)
- Explainable underwriting
- Customer acceptance flow
- Disbursement orchestration (simulated)
- Customer support and case management
- Real-time monitoring and dashboards
- Web-based interface

### ❌ Out of Scope (MVP)
- Real money disbursement
- Core banking system integration
- Post-disbursement operations (EMI collection, servicing)
- NBFC integration
- Mobile native apps
- Blockchain
- Voice/video interaction

**Why This Matters**: Clear scope prevents judges from asking "Why didn't you build X?" You can say "That's Phase 2."

## 🔢 Risk Assumptions (Transparency)

### Credit Score Thresholds
| Bank | Min Score | Preferred | Excellent |
|------|-----------|-----------|-----------|
| SBI | 650 | 700 | 750+ |
| HDFC | 675 | 725 | 750+ |

### FOIR Limits
| Bank | Salaried | Self-Employed | Business |
|------|----------|---------------|----------|
| SBI | 50% | 45% | 40% |
| HDFC | 55% | 50% | 45% |

### Interest Rate Ranges (Indicative)
- Education: 8.5% - 11.5%
- Home: 8.0% - 10.5%
- Personal: 10.5% - 18.0%

**Disclaimer**: All assumptions based on public bank documentation and RBI guidelines as of Feb 2026. Actual policies may vary.

**Why This Matters**: Shows transparency and maturity. Judges appreciate honesty about assumptions.

## 🚀 Technical Stack

**Backend**: Python 3.9+, Flask, PostgreSQL, Redis, Celery
**AI/ML**: LangChain, OpenAI/Anthropic, Sentence Transformers, ChromaDB
**External APIs**: PAN, Aadhaar, CIBIL/Experian, AML screening
**Frontend**: HTML5, CSS3, JavaScript (responsive)
**Deployment**: Docker, Docker Compose (microservices-ready)

## 🎯 Key Differentiators (What Makes This Special)

1. **Selective RAG Usage**: Not everything goes through RAG. Policy queries only.
2. **Explainable AI**: Every decision has clear reasoning. No black boxes.
3. **Human Oversight**: Credit officers can review and override AI decisions.
4. **Async Processing**: Handles API timeouts and slow operations gracefully.
5. **Production-Ready**: Monitoring, logging, RBAC, audit trails, error handling.
6. **Modular Architecture**: Easy to add new banks, loan types, or features.

## 📈 Success Metrics

**Business**:
- 70% straight-through processing (no manual intervention)
- 60% lead-to-application conversion
- 45% application-to-sanction conversion
- <24 hours average processing time

**Technical**:
- 99.5% system uptime
- <3 seconds average response time
- 95% API success rate
- <1% error rate

**AI/ML**:
- 90% intent classification accuracy
- 85% RAG retrieval relevance
- 95% underwriting decision consistency

## 🎤 Elevator Pitch for Judges

> "Dhanit is a production-grade AI-powered loan origination platform that automates the **complete end-to-end loan lifecycle** from lead capture to disbursement. Unlike typical hackathon projects that use RAG everywhere, we use it selectively only for dynamic policy data, while keeping critical underwriting decisions deterministic and explainable for compliance. Our Master Agent orchestration with 8 specialized agents, human-in-the-loop escalation, customer support, async processing, and real-time monitoring makes this a **scalable fintech platform**, not just a chatbot demo."

## 🔍 Anticipated Judge Questions & Answers

**Q: Why not use RAG for everything?**
A: Compliance and explainability. Underwriting decisions must be auditable with clear reasoning. RAG can hallucinate. We use it only for frequently changing policy data where citations are provided.

**Q: What happens if the credit bureau API times out?**
A: We have retry logic (3 attempts with exponential backoff), circuit breakers, and graceful degradation. If all retries fail, the application goes to manual review queue with notification to the credit officer.

**Q: How do you handle policy deviations?**
A: We have an escalation engine. Minor deviations go to Credit Manager, major to Regional Head, critical to Chief Credit Officer. All escalations are tracked in audit trail.

**Q: Is this production-ready?**
A: The architecture is production-grade with complete lifecycle coverage, monitoring, logging, RBAC, audit trails, and error handling. For actual production, we'd need real CBS integration, payment gateway, and regulatory approvals. The MVP simulates disbursement.

**Q: How do you scale to 50+ banks?**
A: Our policy engine is data-driven. Adding a new bank is just adding a new policy configuration file. No code changes needed. Microservices architecture allows horizontal scaling.

**Q: What about fraud detection?**
A: We have basic fraud checks (duplicate applications, velocity anomalies, AML screening). Advanced fraud detection (behavioral analysis, device fingerprinting) is planned for Phase 2.

**Q: What happens after disbursement?**
A: In MVP, we generate EMI schedule and mark loan as disbursed. Repayment tracking and EMI collection are Phase 2. The architecture supports it - we just need to add the repayment agent and payment gateway integration.

**Q: How do you handle customer complaints?**
A: We have a complete customer support agent with ticket creation, SLA tracking, auto-escalation, and resolution workflow. Tickets are prioritized (P1-P4) with defined SLAs. Support agents have a dashboard to manage tickets.

**Q: Can customers reject the sanction offer?**
A: Yes! We have a customer acceptance agent that handles accept/reject/clarify/modify actions. If rejected, we capture the reason and update CRM for re-engagement. If accepted, terms are locked and we proceed to disbursement.

## 📚 Documentation Structure

1. **design.md**: Complete architecture with code examples
2. **requirements.md**: Functional and non-functional requirements
3. **system_boundaries.md**: Clear scope definition (in/out)
4. **risk_assumptions.md**: Transparent assumptions and limitations
5. **ARCHITECTURE_SUMMARY.md**: This document (judge-friendly overview)

---

**Pro Tip for Presentation**: Start with the elevator pitch, show the architecture diagram, highlight the 3 key differentiators (selective RAG, human-in-the-loop, async processing), then demo the working system. Keep it under 10 minutes.

**Document Version:** 1.0  
**Last Updated:** February 15, 2026  
**Author:** Dhanit Project Team  
**Purpose:** Judge-friendly architecture summary
