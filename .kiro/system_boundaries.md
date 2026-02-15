# Dhanit Banking System - System Boundaries & Scope

## 1. In Scope (MVP)

### 1.1 Core Functionality
✅ **Retail Loan Processing**
- Education loans
- Home loans
- Personal loans
- Vehicle loans
- Business/MSME loans

✅ **AI-Powered Automation**
- Master Agent orchestration
- Specialized agents (Lead, Sales, Verification, Underwriting, Sanction)
- Selective RAG for policy queries
- Deterministic underwriting rules

✅ **Bank Coverage**
- State Bank of India (SBI)
- HDFC Bank
- ICICI Bank
- Axis Bank

✅ **KYC & Verification**
- PAN verification (API integration)
- Aadhaar verification (API integration)
- AML screening
- Document validation
- Income verification

✅ **Decision Support**
- Credit score assessment
- Risk scoring
- FOIR calculation
- Bank-specific policy enforcement
- Explainable underwriting decisions

✅ **Customer Interaction**
- Web-based chatbot interface
- Multi-stage conversation flow
- Session state management
- Status tracking
- Sanction letter generation

### 1.2 Technical Capabilities
✅ **Architecture**
- Master Agent orchestration pattern
- Modular specialized agents
- RAG for dynamic policy data
- PostgreSQL for structured data
- ChromaDB for vector storage
- Redis for caching

✅ **Integration**
- External KYC APIs (PAN, Aadhaar)
- Credit bureau APIs (CIBIL/Experian)
- AML screening APIs
- Document parsing capabilities

✅ **Security & Compliance**
- PII encryption at rest
- Secure data transmission (HTTPS)
- Audit trail logging
- Role-based access control
- RBI guideline compliance

## 2. Out of Scope (MVP)

### 2.1 Banking Operations
❌ **Real Money Disbursement**
- No actual fund transfer
- No integration with core banking systems (CBS)
- No payment gateway integration
- No account debit/credit operations

❌ **Post-Disbursement Operations**
- No EMI collection
- No loan servicing
- No repayment tracking
- No default management
- No collections process

❌ **Account Management**
- No savings account creation
- No current account operations
- No deposit management
- No transaction processing

### 2.2 Advanced Financial Products
❌ **Non-Retail Loans**
- Corporate loans
- Project financing
- Syndicated loans
- Trade finance
- Letter of credit

❌ **Other Financial Products**
- Insurance products
- Investment products
- Credit cards
- Forex services
- Wealth management

### 2.3 Institutional Coverage
❌ **NBFC Integration**
- Non-Banking Financial Companies not included in MVP
- NBFC-specific policies not implemented
- NBFC regulatory requirements not covered

❌ **International Operations**
- Cross-border lending
- Foreign currency loans
- International KYC standards
- Multi-country compliance

### 2.4 Advanced Technology
❌ **Blockchain**
- No blockchain-based audit trail
- No smart contracts
- No decentralized identity
- No cryptocurrency integration

❌ **Advanced AI Features**
- No voice interaction
- No video KYC
- No computer vision for document analysis
- No predictive analytics (churn, default)
- No multi-modal RAG

❌ **Mobile Applications**
- No native iOS app
- No native Android app
- Web interface only (responsive design)

### 2.5 Operational Features
❌ **Customer Support**
- No live chat with human agents
- No call center integration
- No ticketing system
- No complaint management system

❌ **Marketing & CRM**
- No email marketing campaigns
- No SMS campaigns
- No WhatsApp integration
- No lead nurturing automation
- No customer segmentation

❌ **Advanced Analytics**
- No real-time dashboards
- No predictive modeling
- No A/B testing framework
- No conversion funnel analytics
- No customer lifetime value calculation

## 3. Assumptions

### 3.1 Data Assumptions
📌 **Credit Score Thresholds**
- Excellent: 750+
- Good: 700-749
- Fair: 650-699
- Poor: <650
- No history: First-time borrowers eligible with conditions

📌 **FOIR Limits**
- SBI: Salaried 50%, Self-employed 45%, Business 40%
- HDFC: Salaried 55%, Self-employed 50%, Business 45%
- ICICI: Salaried 50%, Self-employed 45%, Business 40%
- Axis: Salaried 55%, Self-employed 50%, Business 45%

📌 **Interest Rate Ranges**
- Education: 8.5% - 11.5%
- Home: 8.0% - 10.5%
- Personal: 10.5% - 18.0%
- Vehicle: 8.5% - 12.0%
- Business: 9.0% - 14.0%

### 3.2 API Assumptions
📌 **External API Availability**
- PAN verification API: 99% uptime
- Aadhaar verification API: 99% uptime
- Credit bureau API: 95% uptime
- AML screening API: 99% uptime
- Response time: <5 seconds

📌 **Mocked API Data**
- Development environment uses mocked responses
- Test data for all verification scenarios
- Synthetic credit scores for testing
- Sample AML screening results

### 3.3 Regulatory Assumptions
📌 **Compliance**
- RBI guidelines as of February 2026
- PMLA compliance for KYC
- Data localization within India
- 7-year audit trail retention
- Fair lending practices

📌 **Bank Policies**
- Policies accurate as of February 2026
- Bank-specific rules from public documentation
- Interest rates are indicative ranges
- Actual rates subject to bank approval

### 3.4 User Assumptions
📌 **User Capabilities**
- Users have basic digital literacy
- Users can upload documents (PDF, JPG)
- Users have valid PAN and Aadhaar
- Users can receive OTP for verification
- Users have email access

📌 **User Behavior**
- Users provide accurate information
- Users complete application in single session (or can resume)
- Users understand loan terminology (with help)
- Users consent to data processing

## 4. System Limitations

### 4.1 Functional Limitations
⚠️ **Decision Authority**
- System provides recommendations, not final decisions
- Human oversight required for borderline cases
- Credit officer can override AI decisions
- Complex cases escalated to manual review

⚠️ **Data Accuracy**
- System relies on external API data accuracy
- Document authenticity not guaranteed
- Income verification based on provided documents
- Credit score accuracy depends on bureau data

⚠️ **Processing Capacity**
- MVP supports up to 1000 concurrent users
- Batch processing not optimized for high volume
- Real-time processing only (no scheduled jobs)

### 4.2 Technical Limitations
⚠️ **RAG Limitations**
- RAG accuracy depends on document quality
- Similarity threshold may miss relevant content
- No multi-modal support (text only)
- Manual document ingestion required

⚠️ **Integration Limitations**
- No real-time CBS integration
- No payment gateway integration
- No core banking operations
- API rate limits apply

⚠️ **Scalability Limitations**
- Single-server deployment in MVP
- In-memory session state (not distributed)
- No auto-scaling
- No multi-region support

### 4.3 Security Limitations
⚠️ **Authentication**
- Basic JWT authentication
- No multi-factor authentication (MFA)
- No biometric authentication
- No device fingerprinting

⚠️ **Fraud Detection**
- Basic AML screening only
- No behavioral fraud detection
- No velocity checks
- No IP reputation analysis

## 5. Success Boundaries

### 5.1 What Success Looks Like
✅ **Functional Success**
- Complete loan journey from inquiry to sanction
- 4 banks with 5 loan types each
- 80% straight-through processing for qualified leads
- <3 second average response time
- 95% API success rate

✅ **User Experience Success**
- 90% user retention through application process
- 85% task completion rate
- <10 minutes for complete application
- Clear error messages and guidance
- Responsive design (mobile, tablet, desktop)

✅ **Technical Success**
- 99.5% system availability
- Zero security incidents
- Comprehensive audit trail
- Explainable AI decisions
- Modular, maintainable codebase

### 5.2 What Success Does NOT Include
❌ **Not Success Criteria**
- Real money disbursement
- Integration with 50+ banks
- 10,000+ concurrent users
- Mobile native apps
- Voice interaction
- Blockchain integration
- Predictive analytics
- Marketing automation

## 6. Expansion Path (Post-MVP)

### 6.1 Phase 1 Expansion (6 months)
🔹 **Bank Coverage**: 10+ banks
🔹 **NBFC Integration**: 5+ NBFCs
🔹 **Mobile Apps**: iOS and Android
🔹 **Advanced Analytics**: Dashboards and reporting
🔹 **Multi-language**: Hindi, Tamil, Telugu

### 6.2 Phase 2 Expansion (12 months)
🔹 **Bank Coverage**: 20+ banks, 10+ NBFCs
🔹 **Disbursement**: CBS integration for fund transfer
🔹 **Loan Servicing**: EMI collection and tracking
🔹 **Advanced AI**: Predictive models, fraud detection
🔹 **Multi-region**: Pan-India deployment

### 6.3 Phase 3 Expansion (18+ months)
🔹 **Ecosystem**: Insurance, investments, credit cards
🔹 **Blockchain**: Immutable audit trail
🔹 **Voice & Video**: Multi-modal interaction
🔹 **International**: Cross-border lending

## 7. Stakeholder Communication

### 7.1 For Judges/Evaluators
💡 **Key Message**: "Dhanit is a scalable AI-powered loan origination platform, not a complete digital bank. We focus on the origination journey with production-grade architecture, leaving disbursement and servicing for future phases."

### 7.2 For Technical Reviewers
💡 **Key Message**: "Our architecture prioritizes explainability and compliance over pure AI automation. RAG is used selectively for policy data, while underwriting uses deterministic rules for auditability."

### 7.3 For Business Stakeholders
💡 **Key Message**: "MVP covers 4 banks and 5 loan types with AI-powered decision support. System provides recommendations that credit officers can review and override, ensuring human oversight for critical decisions."

---

**Document Version:** 1.0  
**Last Updated:** February 15, 2026  
**Author:** Dhanit Project Team  
**Status:** System Boundaries Definition  
**Related Documents:** design.md, requirements.md, risk_assumptions.md
