# Dhanit Banking System - Requirements Document

## 1. Project Overview

### 1.1 System Description
The Dhanit Banking System is a production-grade AI-powered loan processing platform that automates the complete end-to-end loan lifecycle from lead capture to disbursement. The system uses a Master Agent orchestration pattern with specialized AI agents for each stage, combined with selective RAG (Retrieval-Augmented Generation) for dynamic policy data and deterministic rule engines for compliance and explainability.

**Scope:** This MVP covers the complete loan origination journey including lead generation, sales, verification, underwriting, sanction, customer acceptance, and disbursement orchestration. Disbursement is simulated (no real fund transfer) in MVP, with architecture ready for production CBS integration.

### 1.2 Business Context
- **Target Market**: Indian banking sector with focus on retail loans (Education, Home, Personal, Vehicle, Business)
- **Primary Users**: Loan applicants, bank staff, relationship managers
- **Business Model**: B2B2C platform serving banks and their customers
- **Regulatory Environment**: Compliant with RBI guidelines, PMLA, and Indian banking regulations
- **Competitive Advantage**: Selective RAG usage, explainable AI, modular architecture

### 1.3 Key Differentiators
- **Smart RAG Usage**: RAG only for frequently changing policy data, not for loan rules
- **Explainable Underwriting**: Every decision has clear reasoning for compliance
- **Modular Architecture**: Easy to add new banks or loan types
- **Production-Ready**: Error handling, monitoring, security built-in

## 2. System Architecture & Technology Stack

### 2.1 Core Technologies
- **Backend Framework**: Python 3.9+ with Flask
- **AI/ML Framework**: LangChain for agent orchestration
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB for RAG
- **Relational Database**: PostgreSQL for structured data
- **Caching**: Redis for session state and performance
- **Frontend**: HTML5, CSS3, JavaScript (responsive design)
- **Deployment**: Docker, Docker Compose (microservices ready)

### 2.2 External Integrations
- **Credit Bureau APIs**: CIBIL, Experian, Equifax
- **KYC Services**: Aadhaar verification API, PAN verification API, DigiLocker
- **AML Services**: Anti-Money Laundering screening APIs
- **Banking APIs**: Core banking system integration (future)
- **Document Services**: Bank statement parser, OCR (future)
- **Communication**: SMS, Email, WhatsApp (future)

### 2.3 Architecture Pattern
- **Master Agent Orchestration**: Central orchestrator with 5 core responsibilities
- **Specialized Agents**: Lead, Sales, Verification, Underwriting, Sanction
- **RAG Controller**: Selective RAG usage for policy queries only
- **State Machine**: Context state management across agent transitions
- **Deterministic Rules**: Fixed loan rules in internal DB for compliance


## 3. Functional Requirements

### 3.1 Master Agent (Orchestrator)

#### 3.1.1 Intent Understanding
- **FR-MA-001**: Detect loan inquiry intent (education, home, personal, vehicle, business)
- **FR-MA-002**: Identify eligibility check requests
- **FR-MA-003**: Handle document upload requests
- **FR-MA-004**: Track status inquiry requests
- **FR-MA-005**: Recognize repeat customer interactions

#### 3.1.2 Context State Machine
- **FR-MA-006**: Maintain user journey state (New user, KYC pending, Verified, Underwriting, Sanctioned, Disbursed)
- **FR-MA-007**: Persist session state across interactions
- **FR-MA-008**: Enable session recovery after disconnection
- **FR-MA-009**: Track conversation history for context

#### 3.1.3 Risk Pre-Screening
- **FR-MA-010**: Detect missing required data before routing
- **FR-MA-011**: Flag suspicious input patterns
- **FR-MA-012**: Verify KYC completion status
- **FR-MA-013**: Validate data quality before agent handoff

#### 3.1.4 Agent Switching Logic
- **FR-MA-014**: Route "Explore Loan" intent to Sales Agent
- **FR-MA-015**: Route "Submit Documents" to Verification Agent
- **FR-MA-016**: Route verified users to Underwriting Agent
- **FR-MA-017**: Route approved applications to Sanction Agent
- **FR-MA-018**: Route drop-offs to Lead Generation Agent
- **FR-MA-019**: Provide fallback routing for edge cases

#### 3.1.5 RAG Controller
- **FR-MA-020**: Detect policy-related queries (RBI circulars, govt schemes)
- **FR-MA-021**: Trigger RAG pipeline for dynamic policy data
- **FR-MA-022**: Use internal DB for fixed loan rules
- **FR-MA-023**: Cache RAG results for performance

### 3.2 Lead Generation Agent

#### 3.2.1 Lead Capture
- **FR-LG-001**: Capture loan intent (education, home, personal, vehicle, business, unknown)
- **FR-LG-002**: Detect urgency level (immediate, exploratory, future)
- **FR-LG-003**: Record source channel (web, mobile, referral)
- **FR-LG-004**: Capture initial user signals (tone, sentiment)

#### 3.2.2 Lead Qualification
- **FR-LG-005**: Calculate lead score (0-100) based on:
  - Intent clarity (0-30 points)
  - Urgency signals (0-20 points)
  - Engagement level (0-20 points)
  - Sentiment analysis (0-15 points)
  - Consent for follow-up (0-15 points)
- **FR-LG-006**: Classify leads as Hot (>60), Warm (30-60), Cold (<30)
- **FR-LG-007**: Route hot leads to Sales Agent immediately

#### 3.2.3 CRM Storage
- **FR-LG-008**: Store lead metadata in CRM database
- **FR-LG-009**: Record conversation summary
- **FR-LG-010**: Capture drop-off reasons
- **FR-LG-011**: Enable consent-based re-engagement

#### 3.2.4 Lead Routing
- **FR-LG-012**: Transition qualified leads (score > 30) to Sales Agent
- **FR-LG-013**: Store warm leads for nurturing campaigns
- **FR-LG-014**: Enable re-engagement for cold leads

**No RAG Usage**: Lead generation uses pattern matching and rule-based classification only.


### 3.3 Sales Agent (Loan Advisory)

#### 3.3.1 Loan Type Identification
- **FR-SA-001**: Identify personal loan requirements
- **FR-SA-002**: Identify SME/business loan needs
- **FR-SA-003**: Identify education loan requirements
- **FR-SA-004**: Identify gold loan inquiries
- **FR-SA-005**: Identify home loan needs

#### 3.3.2 Pre-Eligibility Assessment
- **FR-SA-006**: Collect monthly income information
- **FR-SA-007**: Verify employment type (salaried, self-employed, business, retired, student)
- **FR-SA-008**: Check age eligibility
- **FR-SA-009**: Assess location/geography
- **FR-SA-010**: Calculate basic affordability (income multiplier)

#### 3.3.3 CRM Lookup
- **FR-SA-011**: Check existing customer status
- **FR-SA-012**: Retrieve previous loan history
- **FR-SA-013**: Assess repayment history (excellent, good, fair, poor)
- **FR-SA-014**: Calculate relationship value/loyalty score

#### 3.3.4 Personalized Offer Generation
- **FR-SA-015**: Present loan options from internal product DB
- **FR-SA-016**: Use RAG ONLY for policy questions (e.g., "What is the latest RBI education loan scheme?")
- **FR-SA-017**: Provide bank-specific product features
- **FR-SA-018**: Calculate estimated EMI ranges
- **FR-SA-019**: Explain eligibility criteria

#### 3.3.5 User Engagement
- **FR-SA-020**: Analyze user communication style (casual, formal, neutral)
- **FR-SA-021**: Detect sentiment (positive, neutral, hesitant, skeptical)
- **FR-SA-022**: Assess financial literacy (low, medium, high)
- **FR-SA-023**: Ask micro-questions to gather information gradually
- **FR-SA-024**: Handle hesitation with empathy
- **FR-SA-025**: Track trust score (0-100)

#### 3.3.6 Education Mode
- **FR-SA-026**: Switch to education mode for clarification requests
- **FR-SA-027**: Explain loan concepts in simple terms
- **FR-SA-028**: Use RAG for policy-related explanations
- **FR-SA-029**: Return to sales mode after clarification

#### 3.3.7 Transition Criteria
- **FR-SA-030**: Detect readiness for verification when:
  - User provides complete information (loan type, income, purpose)
  - User shows commitment signals
  - All required data collected
- **FR-SA-031**: Pass structured data to Verification Agent

**RAG Usage**: Sales Agent uses RAG selectively for government schemes, RBI circulars, and policy updates. Static product information comes from internal DB.


### 3.4 Verification Agent (KYC Layer)

#### 3.4.1 Identity Verification
- **FR-VA-001**: Verify PAN card against government database
- **FR-VA-002**: Validate PAN-name match
- **FR-VA-003**: Perform Aadhaar verification with OTP
- **FR-VA-004**: Validate Aadhaar-name match
- **FR-VA-005**: Check for duplicate/fake identity documents

#### 3.4.2 Income Verification
- **FR-VA-006**: Validate salary slips (format, authenticity)
- **FR-VA-007**: Parse bank statements for income verification
- **FR-VA-008**: Verify ITR (Income Tax Returns) documents
- **FR-VA-009**: Cross-check income consistency across documents

#### 3.4.3 Employment Verification
- **FR-VA-010**: Verify company name and legitimacy
- **FR-VA-011**: Validate employment type
- **FR-VA-012**: Check Udyam registration for SME applicants
- **FR-VA-013**: Verify years of experience/business vintage

#### 3.4.4 External API Integration
- **FR-VA-014**: Integrate with DigiLocker API for document retrieval
- **FR-VA-015**: Call PAN verification API
- **FR-VA-016**: Call Aadhaar verification API with OTP
- **FR-VA-017**: Use bank statement parser API
- **FR-VA-018**: Handle API failures gracefully

#### 3.4.5 AML (Anti-Money Laundering) Checks
- **FR-VA-019**: Screen against blacklist databases
- **FR-VA-020**: Calculate AML risk score (0-100, lower is better)
- **FR-VA-021**: Flag high-risk applicants (score > 70)
- **FR-VA-022**: Check for politically exposed persons (PEP)
- **FR-VA-023**: Verify source of funds for large loans

#### 3.4.6 Verification Output
- **FR-VA-024**: Generate verification status (VERIFIED, FAILED, NEED_MORE_DOCS)
- **FR-VA-025**: Calculate confidence score (0-1 scale)
- **FR-VA-026**: List verified documents
- **FR-VA-027**: Provide failure reasons if verification fails
- **FR-VA-028**: Store verification results in internal DB

#### 3.4.7 Transition Criteria
- **FR-VA-029**: Route to Underwriting Agent when all checks pass
- **FR-VA-030**: Request additional documents if verification incomplete
- **FR-VA-031**: Reject application if AML flags are critical

**No RAG Usage**: Verification is purely deterministic using external APIs and rule-based validation.


### 3.5 Underwriting Agent (Risk Engine & Decision Intelligence)

#### 3.5.1 Credit Bureau Integration
- **FR-UW-001**: Pull credit score from CIBIL/Experian/Equifax
- **FR-UW-002**: Classify credit score into buckets:
  - Excellent (750+)
  - Good (700-749)
  - Fair (650-699)
  - Poor (<650)
  - No History (first-time borrowers)
- **FR-UW-003**: Retrieve credit history details (total accounts, active accounts, overdue accounts)
- **FR-UW-004**: Check payment behavior (30/60/90 days past due)
- **FR-UW-005**: Identify write-offs and settlements (deal breakers)
- **FR-UW-006**: Calculate credit utilization ratio

#### 3.5.2 Financial Assessment
- **FR-UW-007**: Calculate Debt-to-Income ratio (DTI)
- **FR-UW-008**: Calculate FOIR (Fixed Obligations to Income Ratio)
- **FR-UW-009**: Apply bank-specific FOIR limits:
  - SBI: Salaried 50%, Self-employed 45%, Business 40%
  - HDFC: Salaried 55%, Self-employed 50%, Business 45%
  - ICICI: Salaried 50%, Self-employed 45%, Business 40%
  - Axis: Salaried 55%, Self-employed 50%, Business 45%
- **FR-UW-010**: Assess existing EMI burden
- **FR-UW-011**: Evaluate credit card dues

#### 3.5.3 Bank Policy Enforcement
- **FR-UW-012**: Apply bank-specific credit score thresholds
- **FR-UW-013**: Enforce minimum income requirements
- **FR-UW-014**: Check age eligibility (min age, max age at maturity)
- **FR-UW-015**: Validate loan amount limits (min/max)
- **FR-UW-016**: Apply LTV (Loan-to-Value) ratios for secured loans
- **FR-UW-017**: Check collateral requirements
- **FR-UW-018**: Validate tenure limits

#### 3.5.4 Risk Scoring
- **FR-UW-019**: Calculate overall risk score (0-100)
- **FR-UW-020**: Classify risk level (Low, Medium, High, Critical)
- **FR-UW-021**: Consider verification confidence score
- **FR-UW-022**: Factor in CRM loyalty score for existing customers
- **FR-UW-023**: Detect fraud signals (multiple applications, suspicious patterns)

#### 3.5.5 Credit Decision Making
- **FR-UW-024**: Make credit decision:
  - **Approved**: All criteria met, low risk
  - **Conditionally Approved**: Borderline case with conditions
  - **Rejected**: Does not meet minimum criteria
- **FR-UW-025**: Generate clear decision reasoning
- **FR-UW-026**: Determine approved loan amount (may be less than requested)
- **FR-UW-027**: Set interest rate range (provisional)
- **FR-UW-028**: Define tenure
- **FR-UW-029**: List conditions for conditional approval

#### 3.5.6 OSR (On Sanction Risk) Handling
- **FR-UW-030**: Identify policy deviations
- **FR-UW-031**: Assess compensating factors
- **FR-UW-032**: Determine if deviation is approvable
- **FR-UW-033**: Define conditions to mitigate risk
- **FR-UW-034**: Escalate to appropriate approval authority

#### 3.5.7 Decision Output
- **FR-UW-035**: Generate structured sanction data for Sanction Agent
- **FR-UW-036**: Store underwriting decision in Risk Score DB
- **FR-UW-037**: Create audit trail for compliance
- **FR-UW-038**: Provide rejection reasons if declined

#### 3.5.8 Transition Criteria
- **FR-UW-039**: Route to Sanction Agent if Approved or Conditionally Approved
- **FR-UW-040**: Communicate rejection to user if Rejected
- **FR-UW-041**: Request clarification if additional information needed

**No RAG Usage**: Underwriting is pure deterministic + ML risk scoring. All rules are in internal policy DB for explainability and compliance.

**Why No RAG?**
- Compliance: Decisions must be explainable
- Audit: Clear reasoning for every decision
- Speed: Deterministic rules are faster
- Consistency: Same inputs = same outputs


### 3.6 Sanction Agent (Letter Generation & Formalization)

#### 3.6.1 Sanction Letter Generation
- **FR-SN-001**: Generate bank-compliant sanction letter (PDF format)
- **FR-SN-002**: Include approved loan amount
- **FR-SN-003**: Specify interest rate (provisional range, not exact)
- **FR-SN-004**: Define tenure and estimated EMI
- **FR-SN-005**: List moratorium period (if applicable)
- **FR-SN-006**: Detail special conditions
- **FR-SN-007**: Specify validity period (typically 90 days)
- **FR-SN-008**: Include mandatory disclaimer

#### 3.6.2 Loan Agreement Draft
- **FR-SN-009**: Generate loan agreement draft
- **FR-SN-010**: Include terms and conditions
- **FR-SN-011**: Provide repayment schedule
- **FR-SN-012**: Detail collateral requirements (if applicable)
- **FR-SN-013**: List processing fees and charges

#### 3.6.3 System Updates
- **FR-SN-014**: Update CRM status to "Sanctioned"
- **FR-SN-015**: Record sanction date and validity
- **FR-SN-016**: Update LOS (Loan Origination System) queue
- **FR-SN-017**: Trigger notifications (email, SMS)

#### 3.6.4 Operating Modes

**Mode 1: Issue Sanction (Default)**
- **FR-SN-018**: Generate and send sanction letter
- **FR-SN-019**: Communicate next steps to customer
- **FR-SN-020**: Provide document checklist

**Mode 2: Explain Sanction**
- **FR-SN-021**: Clarify moratorium meaning
- **FR-SN-022**: Explain collateral requirements
- **FR-SN-023**: Define "conditional approval"
- **FR-SN-024**: Explain validity period
- **FR-SN-025**: Describe next operational steps

**Mode 3: Route Support**
- **FR-SN-026**: Detect complaint intent
- **FR-SN-027**: Route complaints to Customer Support
- **FR-SN-028**: Handle delay inquiries
- **FR-SN-029**: Escalate disputes to Case Management
- **FR-SN-030**: Acknowledge and route gracefully

#### 3.6.5 Restrictions (What Sanction Agent Must NOT Do)
- **FR-SN-031**: Never renegotiate interest rates
- **FR-SN-032**: Never modify sanctioned amount
- **FR-SN-033**: Never override underwriting decisions
- **FR-SN-034**: Never promise disbursement timelines
- **FR-SN-035**: Never handle disputes end-to-end

#### 3.6.6 Mandatory Disclaimer
- **FR-SN-036**: Include disclaimer: "This sanction letter is system-generated based on internal credit evaluation. Final disbursement is subject to bank verification and fulfillment of all conditions."

**No RAG Usage**: Sanction uses fixed legal templates. No policy queries needed.


### 3.7 RAG (Retrieval-Augmented Generation) System

#### 3.7.1 Document Ingestion
- **FR-RAG-001**: Ingest PDF documents (bank policies, RBI circulars)
- **FR-RAG-002**: Ingest Markdown files (policy documents)
- **FR-RAG-003**: Ingest text files
- **FR-RAG-004**: Support web scraping for online policy pages
- **FR-RAG-005**: Process documents from directory (recursive)

#### 3.7.2 Text Processing
- **FR-RAG-006**: Chunk documents (500 characters per chunk, 50 overlap)
- **FR-RAG-007**: Extract metadata (bank name, loan type, document type)
- **FR-RAG-008**: Generate embeddings using Sentence Transformers
- **FR-RAG-009**: Store in ChromaDB vector database

#### 3.7.3 Retrieval
- **FR-RAG-010**: Generate query embeddings
- **FR-RAG-011**: Search vector database (top 5 results)
- **FR-RAG-012**: Filter by similarity threshold (>0.3)
- **FR-RAG-013**: Support metadata filtering (bank name, loan type)
- **FR-RAG-014**: Return results with citations

#### 3.7.4 Citation Management
- **FR-RAG-015**: Extract source information
- **FR-RAG-016**: Include bank name in citations
- **FR-RAG-017**: Include loan type in citations
- **FR-RAG-018**: Provide document source (file name, URL)
- **FR-RAG-019**: Include similarity scores

#### 3.7.5 Performance Optimization
- **FR-RAG-020**: Cache frequent queries (30 minutes TTL)
- **FR-RAG-021**: Batch embedding generation
- **FR-RAG-022**: Persist vector database to disk
- **FR-RAG-023**: Support incremental document updates

#### 3.7.6 RAG Usage Policy
- **FR-RAG-024**: Use RAG ONLY for:
  - Government policy changes
  - RBI circular updates
  - Interest cap changes
  - Subsidy schemes (PMMY, Mudra)
  - EMI regulation changes
  - Tax benefit changes
- **FR-RAG-025**: Do NOT use RAG for:
  - Loan product rules (use internal DB)
  - Eligibility thresholds (use rule engine)
  - Risk scoring logic (use deterministic engine)


### 3.8 Loan Product Support

The system must support the following loan types with bank-specific policies:

#### 3.8.1 Education Loans
- **FR-ED-001**: Support domestic education financing (up to ₹50 lakh)
- **FR-ED-002**: Support international education financing (up to ₹1.5 crore)
- **FR-ED-003**: Handle moratorium periods (course duration + 6-12 months)
- **FR-ED-004**: Process co-applicant requirements (mandatory)
- **FR-ED-005**: Calculate collateral requirements (threshold: ₹7.5 lakh for SBI)
- **FR-ED-006**: Apply interest rate concessions (girl students, existing customers)
- **FR-ED-007**: Support floating interest rates (linked to RLLR/MCLR)
- **FR-ED-008**: Process government subsidy schemes (CSIS for EWS)

#### 3.8.2 Home Loans
- **FR-HL-001**: Support property purchase loans
- **FR-HL-002**: Support construction loans
- **FR-HL-003**: Calculate LTV (Loan-to-Value) ratios:
  - Up to ₹30L: 90% LTV
  - ₹30L to ₹75L: 80% LTV
  - Above ₹75L: 75% LTV
- **FR-HL-004**: Handle balance transfer cases
- **FR-HL-005**: Process joint applicant scenarios
- **FR-HL-006**: Support long tenure (up to 30 years)
- **FR-HL-007**: Apply tax benefits (80C for principal, 24b for interest)
- **FR-HL-008**: Support floating rates (linked to repo rate)

#### 3.8.3 Personal Loans
- **FR-PL-001**: Unsecured loan processing (no collateral)
- **FR-PL-002**: Income-based eligibility (minimum ₹15,000-25,000/month)
- **FR-PL-003**: Quick approval for existing customers
- **FR-PL-004**: Flexible tenure (6-72 months)
- **FR-PL-005**: Fixed interest rates
- **FR-PL-006**: Loan amount limits (₹25,000 to ₹50 lakh)
- **FR-PL-007**: Income multiplier limits (20-24x monthly income)

#### 3.8.4 Vehicle Loans
- **FR-VL-001**: Support new vehicle financing (LTV up to 95%)
- **FR-VL-002**: Support used vehicle financing (LTV up to 85%)
- **FR-VL-003**: Handle vehicle hypothecation
- **FR-VL-004**: Process dealer tie-up scenarios
- **FR-VL-005**: Electric vehicle incentive processing (0.2% rate concession)
- **FR-VL-006**: Tenure limits (new: 7 years, used: 5 years)

#### 3.8.5 Business Loans
- **FR-BL-001**: MSME loan processing
- **FR-BL-002**: MUDRA loan scheme integration
- **FR-BL-003**: Working capital and term loan options
- **FR-BL-004**: GST registration verification
- **FR-BL-005**: Business vintage requirements (2-3 years)
- **FR-BL-006**: Udyam registration validation
- **FR-BL-007**: CGTMSE scheme support (collateral-free up to ₹5 crore)
- **FR-BL-008**: Annual turnover requirements


### 3.9 Multi-Bank Support

#### 3.9.1 Supported Banks
- **FR-MB-001**: Support SBI (State Bank of India) policies
- **FR-MB-002**: Support HDFC Bank policies
- **FR-MB-003**: Support ICICI Bank policies
- **FR-MB-004**: Support Axis Bank policies

#### 3.9.2 Bank-Specific Configuration
- **FR-MB-005**: Bank-specific credit score thresholds
- **FR-MB-006**: Bank-specific FOIR limits
- **FR-MB-007**: Bank-specific interest rate ranges
- **FR-MB-008**: Bank-specific loan amount limits
- **FR-MB-009**: Bank-specific tenure limits
- **FR-MB-010**: Bank-specific processing fees
- **FR-MB-011**: Bank-specific collateral requirements
- **FR-MB-012**: Bank-specific document requirements

#### 3.9.3 Bank Policy Storage
- **FR-MB-013**: Store policies in structured format (Python dictionaries)
- **FR-MB-014**: Enable policy updates without code deployment
- **FR-MB-015**: Maintain policy version history
- **FR-MB-016**: Support policy effective dates

### 3.10 Database Requirements

#### 3.10.1 User Database
- **FR-DB-001**: Store user profile (name, email, phone, PAN, Aadhaar)
- **FR-DB-002**: Maintain user creation and update timestamps
- **FR-DB-003**: Encrypt sensitive PII data

#### 3.10.2 CRM Database
- **FR-DB-004**: Store lead records (lead_id, loan_intent, lead_score, status)
- **FR-DB-005**: Track customer relationships (existing customer, previous loans, loyalty score)
- **FR-DB-006**: Record drop-off reasons
- **FR-DB-007**: Enable consent-based re-engagement tracking

#### 3.10.3 Verification Database
- **FR-DB-008**: Store verification records (PAN verified, Aadhaar verified, AML status)
- **FR-DB-009**: Record confidence scores
- **FR-DB-010**: Maintain verification timestamps
- **FR-DB-011**: Store verification flags

#### 3.10.4 Loan Products Database
- **FR-DB-012**: Store loan product details (bank, loan type, amounts, tenure, rates)
- **FR-DB-013**: Maintain eligibility criteria
- **FR-DB-014**: Track processing fees
- **FR-DB-015**: Record policy update timestamps

#### 3.10.5 Risk Score Database
- **FR-DB-016**: Store underwriting decisions (approved amount, risk level, decision)
- **FR-DB-017**: Record decision reasoning
- **FR-DB-018**: Maintain conditions list
- **FR-DB-019**: Track decision timestamps

#### 3.10.6 Vector Database (ChromaDB)
- **FR-DB-020**: Store document embeddings (384-dimensional vectors)
- **FR-DB-021**: Maintain document metadata (source, bank, loan type, date)
- **FR-DB-022**: Support similarity search
- **FR-DB-023**: Enable metadata filtering


## 4. Non-Functional Requirements

### 4.1 Performance Requirements
- **NFR-P-001**: Master Agent response time < 2 seconds
- **NFR-P-002**: Sales Agent response time < 3 seconds
- **NFR-P-003**: RAG query response time < 2 seconds
- **NFR-P-004**: Verification API calls < 5 seconds total
- **NFR-P-005**: Underwriting decision < 3 seconds
- **NFR-P-006**: Support 1000+ concurrent users
- **NFR-P-007**: 99.5% system uptime availability
- **NFR-P-008**: Database query response < 100ms
- **NFR-P-009**: Redis cache hit rate > 80%

### 4.2 Security Requirements
- **NFR-S-001**: Encrypt all PII data at rest (AES-256)
- **NFR-S-002**: Encrypt data in transit (TLS 1.3)
- **NFR-S-003**: Implement role-based access control (RBAC)
- **NFR-S-004**: Audit trail for all customer interactions
- **NFR-S-005**: Secure API endpoints with JWT authentication
- **NFR-S-006**: Compliance with RBI data protection guidelines
- **NFR-S-007**: PAN/Aadhaar masking in logs
- **NFR-S-008**: Session timeout after 30 minutes inactivity
- **NFR-S-009**: Rate limiting (100 requests/minute per user)
- **NFR-S-010**: SQL injection prevention
- **NFR-S-011**: XSS (Cross-Site Scripting) prevention

### 4.3 Scalability Requirements
- **NFR-SC-001**: Horizontal scaling for agent services
- **NFR-SC-002**: Database connection pooling (min 10, max 100)
- **NFR-SC-003**: Redis clustering for distributed caching
- **NFR-SC-004**: Load balancing across multiple instances
- **NFR-SC-005**: Auto-scaling based on CPU/memory thresholds
- **NFR-SC-006**: Stateless agent design for easy scaling
- **NFR-SC-007**: Microservices-ready architecture

### 4.4 Reliability Requirements
- **NFR-R-001**: Graceful degradation when RAG fails (fallback to static data)
- **NFR-R-002**: Retry logic for external API failures (3 retries with exponential backoff)
- **NFR-R-003**: Session recovery after disconnection
- **NFR-R-004**: Database backup every 6 hours
- **NFR-R-005**: Point-in-time recovery capability
- **NFR-R-006**: Health check endpoints for all services
- **NFR-R-007**: Circuit breaker pattern for external APIs

### 4.5 Maintainability Requirements
- **NFR-M-001**: Comprehensive logging (INFO, WARNING, ERROR levels)
- **NFR-M-002**: Structured logging format (JSON)
- **NFR-M-003**: Centralized log aggregation
- **NFR-M-004**: Code documentation (docstrings for all functions)
- **NFR-M-005**: API documentation (OpenAPI/Swagger)
- **NFR-M-006**: Version control (Git)
- **NFR-M-007**: Automated testing (unit, integration)
- **NFR-M-008**: Code coverage > 70%

### 4.6 Compliance Requirements
- **NFR-C-001**: RBI compliance for digital lending guidelines
- **NFR-C-002**: Data localization (all data stored in India)
- **NFR-C-003**: KYC compliance with PMLA (Prevention of Money Laundering Act)
- **NFR-C-004**: Fair lending practice adherence
- **NFR-C-005**: Audit trail retention for 7 years
- **NFR-C-006**: Customer consent management (GDPR-like)
- **NFR-C-007**: Right to data deletion (upon request)
- **NFR-C-008**: Transparent pricing disclosure
- **NFR-C-009**: Grievance redressal mechanism

### 4.7 Usability Requirements
- **NFR-U-001**: Responsive design (mobile, tablet, desktop)
- **NFR-U-002**: Browser compatibility (Chrome, Firefox, Safari, Edge)
- **NFR-U-003**: Accessibility compliance (WCAG 2.1 Level AA)
- **NFR-U-004**: Multi-language support (English, Hindi - future)
- **NFR-U-005**: Clear error messages
- **NFR-U-006**: Progress indicators for long operations
- **NFR-U-007**: Consistent UI/UX across pages


## 5. User Stories

### 5.1 Customer Journey Stories

#### 5.1.1 Initial Loan Inquiry
**As a** potential loan customer  
**I want to** inquire about loan options through a chatbot  
**So that** I can understand available products without visiting a branch

**Acceptance Criteria:**
- Lead Generation Agent captures my loan intent
- I receive relevant loan information from Sales Agent
- My inquiry is recorded in CRM with lead score
- I can proceed to application if interested
- System remembers my context across sessions

#### 5.1.2 Loan Exploration with Policy Questions
**As a** loan applicant  
**I want to** ask about government schemes and RBI policies  
**So that** I can understand my eligibility for subsidies

**Acceptance Criteria:**
- Sales Agent detects policy-related questions
- RAG system retrieves latest RBI circulars and schemes
- Responses include citations and sources
- I receive accurate, up-to-date information
- System falls back to static data if RAG fails

#### 5.1.3 Pre-Eligibility Check
**As a** loan applicant  
**I want to** check my eligibility before applying  
**So that** I don't waste time on applications I won't qualify for

**Acceptance Criteria:**
- Sales Agent collects basic information (income, employment, age)
- System performs quick eligibility assessment
- I receive clear feedback on eligibility
- System explains why I qualify or don't qualify
- I can proceed to full application if eligible

#### 5.1.4 Document Submission
**As a** qualified loan applicant  
**I want to** submit my KYC documents online  
**So that** I can complete verification conveniently

**Acceptance Criteria:**
- Verification Agent guides me through required documents
- I can upload PAN, Aadhaar, income documents
- System validates documents in real-time
- I receive immediate feedback on verification status
- System securely stores my documents

#### 5.1.5 Application Status Tracking
**As a** loan applicant  
**I want to** track my application status  
**So that** I know the progress and next steps

**Acceptance Criteria:**
- Real-time status updates (Lead, Sales, Verification, Underwriting, Sanction)
- Clear communication of current stage
- Estimated timelines provided
- Notifications sent for status changes
- I can ask questions at any stage

#### 5.1.6 Sanction Letter Receipt
**As an** approved loan applicant  
**I want to** receive my sanction letter  
**So that** I can proceed with loan disbursement

**Acceptance Criteria:**
- Sanction Agent generates formal sanction letter
- Letter includes all terms (amount, rate, tenure, conditions)
- I receive letter via email and can download
- System explains next steps clearly
- I can ask clarification questions

### 5.2 Bank Staff Stories

#### 5.2.1 Lead Management
**As a** bank relationship manager  
**I want to** view qualified leads with scores  
**So that** I can prioritize follow-ups

**Acceptance Criteria:**
- CRM dashboard shows all leads with scores
- Leads are classified as Hot/Warm/Cold
- I can see lead details and conversation history
- I can assign leads to team members
- System tracks lead conversion rates

#### 5.2.2 Application Review
**As a** bank credit officer  
**I want to** review AI-processed applications  
**So that** I can make informed decisions on borderline cases

**Acceptance Criteria:**
- Complete application summary available
- AI recommendations clearly presented
- Underwriting reasoning explained
- Override capabilities for special cases
- Audit trail maintained for all decisions

#### 5.2.3 Policy Management
**As a** bank policy administrator  
**I want to** update lending policies in the system  
**So that** current guidelines are always applied

**Acceptance Criteria:**
- Policy changes can be made via configuration
- Changes take effect immediately
- Historical policy versions maintained
- Impact analysis provided for changes
- No code deployment required

#### 5.2.4 Monitoring & Analytics
**As a** bank operations manager  
**I want to** monitor system performance and conversion rates  
**So that** I can optimize the loan process

**Acceptance Criteria:**
- Real-time dashboard with key metrics
- Conversion rates at each stage
- Average processing times
- Agent performance metrics
- Error rates and system health


## 6. System Constraints

### 6.1 Technical Constraints
- **TC-001**: Python 3.9+ runtime environment required
- **TC-002**: Minimum 16GB RAM for optimal performance
- **TC-003**: ChromaDB storage scales with document volume (estimate 1GB per 10,000 documents)
- **TC-004**: Internet connectivity required for external API calls
- **TC-005**: PostgreSQL 13+ required for relational data
- **TC-006**: Redis 6+ required for caching
- **TC-007**: Docker and Docker Compose for deployment

### 6.2 Business Constraints
- **BC-001**: Compliance with individual bank's lending policies
- **BC-002**: Integration timeline dependent on bank API availability
- **BC-003**: Regulatory approval required for production deployment
- **BC-004**: Customer consent required for data processing
- **BC-005**: Bank partnership agreements required
- **BC-006**: Credit bureau subscription costs

### 6.3 Regulatory Constraints
- **RC-001**: Data residency within Indian borders (no cross-border data transfer)
- **RC-002**: Customer data retention as per RBI guidelines (7 years)
- **RC-003**: Audit trail retention for 7 years minimum
- **RC-004**: Real-time reporting to regulatory authorities (if required)
- **RC-005**: KYC compliance with PMLA norms
- **RC-006**: Fair lending practices (no discrimination)
- **RC-007**: Transparent pricing disclosure

### 6.4 Operational Constraints
- **OC-001**: 24/7 system availability required
- **OC-002**: Customer support availability during business hours
- **OC-003**: Backup and disaster recovery procedures
- **OC-004**: Incident response time < 1 hour for critical issues
- **OC-005**: Planned maintenance windows (off-peak hours only)

## 7. Success Criteria

### 7.1 Business Success Metrics
- **BSM-001**: 80% reduction in loan processing time (from days to hours)
- **BSM-002**: 90% customer satisfaction score (CSAT)
- **BSM-003**: 95% straight-through processing for qualified applications
- **BSM-004**: 50% reduction in operational costs
- **BSM-005**: 70% lead-to-application conversion rate
- **BSM-006**: 40% application-to-sanction conversion rate

### 7.2 Technical Success Metrics
- **TSM-001**: 99.5% system availability
- **TSM-002**: <3 second average response time
- **TSM-003**: Zero security incidents
- **TSM-004**: 95% API success rate
- **TSM-005**: 80% cache hit rate
- **TSM-006**: <1% error rate

### 7.3 User Experience Metrics
- **UXM-001**: 85% task completion rate
- **UXM-002**: <5 clicks to complete loan inquiry
- **UXM-003**: 90% user retention through application process
- **UXM-004**: <2 minutes average session time for information gathering
- **UXM-005**: <10 minutes for complete application submission

### 7.4 AI/ML Performance Metrics
- **AIM-001**: 90% lead scoring accuracy
- **AIM-002**: 95% intent classification accuracy
- **AIM-003**: 85% RAG retrieval relevance
- **AIM-004**: 98% underwriting decision consistency
- **AIM-005**: <5% false positive rate in fraud detection


## 8. Risk Assessment

### 8.1 Technical Risks

#### 8.1.1 AI Model Risks
- **TR-001**: AI model accuracy degradation over time
  - **Mitigation**: Regular model retraining, performance monitoring, A/B testing
  - **Impact**: High | **Probability**: Medium

- **TR-002**: RAG retrieval returning irrelevant results
  - **Mitigation**: Similarity threshold tuning, fallback to static data, human review
  - **Impact**: Medium | **Probability**: Low

- **TR-003**: LLM hallucinations in critical decisions
  - **Mitigation**: Use deterministic rules for underwriting, RAG only for policies
  - **Impact**: Critical | **Probability**: Low (mitigated by design)

#### 8.1.2 Integration Risks
- **TR-004**: External API dependency failures (PAN, Aadhaar, Credit Bureau)
  - **Mitigation**: Retry logic, circuit breakers, fallback mechanisms, SLA monitoring
  - **Impact**: High | **Probability**: Medium

- **TR-005**: API rate limiting by external providers
  - **Mitigation**: Request throttling, caching, multiple provider support
  - **Impact**: Medium | **Probability**: Medium

#### 8.1.3 Performance Risks
- **TR-006**: Scalability bottlenecks during peak loads
  - **Mitigation**: Load testing, auto-scaling, caching, database optimization
  - **Impact**: High | **Probability**: Medium

- **TR-007**: Database performance degradation with large datasets
  - **Mitigation**: Indexing, partitioning, archival strategy, query optimization
  - **Impact**: Medium | **Probability**: Medium

#### 8.1.4 Data Risks
- **TR-008**: Data quality issues affecting decisions
  - **Mitigation**: Input validation, data cleansing, confidence scoring
  - **Impact**: High | **Probability**: Medium

- **TR-009**: Vector database corruption
  - **Mitigation**: Regular backups, replication, rebuild capability
  - **Impact**: Medium | **Probability**: Low

### 8.2 Business Risks

#### 8.2.1 Regulatory Risks
- **BR-001**: Regulatory changes affecting system design
  - **Mitigation**: Modular architecture, policy-driven design, regular compliance audits
  - **Impact**: High | **Probability**: High

- **BR-002**: Non-compliance with RBI guidelines
  - **Mitigation**: Legal review, compliance team, audit trails, explainable AI
  - **Impact**: Critical | **Probability**: Low

#### 8.2.2 Market Risks
- **BR-003**: Bank policy changes requiring system updates
  - **Mitigation**: Configuration-driven policies, no-code policy updates, version control
  - **Impact**: Medium | **Probability**: High

- **BR-004**: Competition from established banking platforms
  - **Mitigation**: Unique value proposition (selective RAG, explainable AI), continuous innovation
  - **Impact**: High | **Probability**: High

#### 8.2.3 Adoption Risks
- **BR-005**: Customer adoption challenges (trust, digital literacy)
  - **Mitigation**: User education, transparent communication, human support option
  - **Impact**: High | **Probability**: Medium

- **BR-006**: Bank partnership delays
  - **Mitigation**: Multi-bank strategy, phased rollout, pilot programs
  - **Impact**: Medium | **Probability**: Medium

### 8.3 Security & Compliance Risks

#### 8.3.1 Security Risks
- **CR-001**: Data privacy violations (PII exposure)
  - **Mitigation**: Encryption, access control, data masking, security audits
  - **Impact**: Critical | **Probability**: Low

- **CR-002**: Unauthorized access to customer data
  - **Mitigation**: Authentication, authorization, audit trails, intrusion detection
  - **Impact**: Critical | **Probability**: Low

- **CR-003**: API security vulnerabilities
  - **Mitigation**: JWT authentication, rate limiting, input validation, penetration testing
  - **Impact**: High | **Probability**: Medium

#### 8.3.2 Compliance Risks
- **CR-004**: Discriminatory lending practices (bias in AI)
  - **Mitigation**: Fairness testing, explainable decisions, human oversight, regular audits
  - **Impact**: Critical | **Probability**: Medium

- **CR-005**: Inadequate audit trails
  - **Mitigation**: Comprehensive logging, immutable audit logs, retention policies
  - **Impact**: High | **Probability**: Low

- **CR-006**: Cross-border data transfer violations
  - **Mitigation**: Data localization, geo-fencing, compliance monitoring
  - **Impact**: Critical | **Probability**: Low

### 8.4 Operational Risks

#### 8.4.1 System Risks
- **OR-001**: System downtime during critical periods
  - **Mitigation**: High availability architecture, redundancy, disaster recovery
  - **Impact**: High | **Probability**: Low

- **OR-002**: Data loss due to system failure
  - **Mitigation**: Regular backups, replication, point-in-time recovery
  - **Impact**: Critical | **Probability**: Low

#### 8.4.2 Process Risks
- **OR-003**: Incorrect underwriting decisions
  - **Mitigation**: Deterministic rules, human review for borderline cases, audit trails
  - **Impact**: High | **Probability**: Low

- **OR-004**: Customer support overload
  - **Mitigation**: Self-service options, chatbot support, escalation procedures
  - **Impact**: Medium | **Probability**: Medium


## 9. Future Enhancements

### 9.1 Phase 1 Enhancements (6 months)

#### 9.1.1 Advanced Features
- **FE-001**: Multi-language support (Hindi, Tamil, Telugu, Bengali)
- **FE-002**: Voice-based interaction capabilities
- **FE-003**: Mobile application (iOS and Android)
- **FE-004**: Biometric authentication (fingerprint, face recognition)
- **FE-005**: Document scanning with OCR
- **FE-006**: Push notifications for status updates

#### 9.1.2 Analytics & Reporting
- **FE-007**: Advanced analytics dashboard
- **FE-008**: Predictive lead scoring with ML
- **FE-009**: Churn prediction models
- **FE-010**: Loan default prediction
- **FE-011**: Customer lifetime value calculation
- **FE-012**: A/B testing framework

#### 9.1.3 Integration Enhancements
- **FE-013**: Core banking system integration
- **FE-014**: Payment gateway integration
- **FE-015**: Document management system integration
- **FE-016**: CRM system integration (Salesforce, HubSpot)
- **FE-017**: WhatsApp Business API integration
- **FE-018**: SMS gateway integration

### 9.2 Phase 2 Enhancements (12 months)

#### 9.2.1 Advanced AI/ML
- **FE-019**: Multi-modal RAG (images, tables, charts)
- **FE-020**: Real-time policy update ingestion
- **FE-021**: Automatic document classification
- **FE-022**: Fraud detection with ML
- **FE-023**: Sentiment analysis for customer interactions
- **FE-024**: Personalized loan recommendations

#### 9.2.2 Blockchain & Security
- **FE-025**: Blockchain-based audit trail
- **FE-026**: Smart contract-based loan agreements
- **FE-027**: Decentralized identity verification
- **FE-028**: Zero-knowledge proof for privacy

#### 9.2.3 Scale & Performance
- **FE-029**: Kubernetes deployment
- **FE-030**: Multi-region support
- **FE-031**: Edge computing for low latency
- **FE-032**: Real-time streaming analytics
- **FE-033**: GraphQL API support
- **FE-034**: Microservices mesh (Istio)

### 9.3 Phase 3 Enhancements (18+ months)

#### 9.3.1 Ecosystem Expansion
- **FE-035**: Insurance product integration
- **FE-036**: Investment product recommendations
- **FE-037**: Credit card offerings
- **FE-038**: Wealth management services
- **FE-039**: Cross-sell and up-sell engine

#### 9.3.2 Advanced Capabilities
- **FE-040**: Video KYC integration
- **FE-041**: Virtual relationship manager (avatar)
- **FE-042**: Augmented reality for property loans
- **FE-043**: IoT integration for asset tracking
- **FE-044**: Quantum-resistant encryption

## 10. Dependencies & Prerequisites

### 10.1 Technical Dependencies
- **DEP-001**: Python 3.9+ installed
- **DEP-002**: PostgreSQL 13+ database server
- **DEP-003**: Redis 6+ cache server
- **DEP-004**: Docker and Docker Compose
- **DEP-005**: Git for version control
- **DEP-006**: OpenAI/Anthropic API keys
- **DEP-007**: Sentence Transformers library
- **DEP-008**: ChromaDB library
- **DEP-009**: Flask web framework
- **DEP-010**: LangChain library

### 10.2 External Service Dependencies
- **DEP-011**: PAN verification API subscription
- **DEP-012**: Aadhaar verification API subscription
- **DEP-013**: AML screening API subscription
- **DEP-014**: CIBIL/Experian/Equifax API subscription
- **DEP-015**: SMS gateway subscription (future)
- **DEP-016**: Email service (SMTP or SendGrid)
- **DEP-017**: Cloud hosting (AWS/Azure/GCP)

### 10.3 Business Prerequisites
- **DEP-018**: Bank partnership agreements
- **DEP-019**: Regulatory approvals (RBI, PMLA)
- **DEP-020**: Legal entity registration
- **DEP-021**: Compliance team setup
- **DEP-022**: Customer support team
- **DEP-023**: Data protection officer (DPO)
- **DEP-024**: Insurance coverage (cyber, liability)

### 10.4 Data Prerequisites
- **DEP-025**: Bank policy documents (PDF, Markdown)
- **DEP-026**: RBI circulars and guidelines
- **DEP-027**: Government scheme documents
- **DEP-028**: Legal templates (sanction letters, agreements)
- **DEP-029**: Test data for development
- **DEP-030**: Synthetic data for testing

## 11. Glossary

### 11.1 Banking Terms
- **AML**: Anti-Money Laundering - Process to prevent money laundering
- **CIBIL**: Credit Information Bureau (India) Limited - Credit bureau
- **DTI**: Debt-to-Income ratio - Measure of debt burden
- **EMI**: Equated Monthly Installment - Fixed monthly payment
- **FOIR**: Fixed Obligations to Income Ratio - Similar to DTI
- **ITR**: Income Tax Returns - Tax filing documents
- **KYC**: Know Your Customer - Identity verification process
- **LTV**: Loan-to-Value ratio - Loan amount vs asset value
- **MCLR**: Marginal Cost of Funds based Lending Rate - Interest rate benchmark
- **MSME**: Micro, Small, and Medium Enterprises
- **MUDRA**: Micro Units Development and Refinance Agency - Loan scheme
- **OSR**: On Sanction Risk - Deviation from standard policy
- **PAN**: Permanent Account Number - Tax identification
- **PMLA**: Prevention of Money Laundering Act
- **PMMY**: Pradhan Mantri MUDRA Yojana - Government loan scheme
- **RBI**: Reserve Bank of India - Central bank
- **RLLR**: Repo Linked Lending Rate - Interest rate benchmark

### 11.2 Technical Terms
- **ChromaDB**: Vector database for embeddings
- **Embedding**: Numerical representation of text
- **LLM**: Large Language Model (GPT, Claude)
- **RAG**: Retrieval-Augmented Generation - AI technique
- **Sentence Transformers**: Library for text embeddings
- **Vector Database**: Database optimized for similarity search

### 11.3 System Terms
- **Agent**: Specialized AI component for specific task
- **Master Agent**: Central orchestrator routing requests
- **Session State**: User journey context across interactions
- **Lead Score**: Numerical measure of lead quality (0-100)
- **Risk Score**: Numerical measure of credit risk (0-100)
- **Confidence Score**: Measure of verification certainty (0-1)

---

**Document Version:** 2.0  
**Last Updated:** February 15, 2026  
**Author:** Dhanit Project Team  
**Status:** Production-Grade Requirements  
**Related Documents:** design.md, implementation.md


## 12. Asynchronous Processing Requirements

### 12.1 Task Queue Requirements
- **FR-ASYNC-001**: Implement Celery task queue for long-running operations
- **FR-ASYNC-002**: Support asynchronous document verification (PAN, Aadhaar, AML)
- **FR-ASYNC-003**: Support asynchronous credit bureau API calls
- **FR-ASYNC-004**: Support asynchronous sanction letter generation
- **FR-ASYNC-005**: Implement retry logic with exponential backoff (3 retries)
- **FR-ASYNC-006**: Implement dead letter queue for failed tasks
- **FR-ASYNC-007**: Support task status tracking (pending, processing, completed, failed)
- **FR-ASYNC-008**: Provide task result retrieval API

### 12.2 Event-Driven Requirements
- **FR-EVENT-001**: Implement event bus for stage transitions
- **FR-EVENT-002**: Emit events for verification completion
- **FR-EVENT-003**: Emit events for underwriting completion
- **FR-EVENT-004**: Emit events for sanction letter generation
- **FR-EVENT-005**: Support event subscribers for automated workflows
- **FR-EVENT-006**: Implement webhook support for external system notifications
- **FR-EVENT-007**: Support event replay for debugging

### 12.3 Timeout Handling
- **FR-TIMEOUT-001**: Credit bureau API timeout: 10 seconds
- **FR-TIMEOUT-002**: KYC API timeout: 5 seconds per API
- **FR-TIMEOUT-003**: AML screening timeout: 8 seconds
- **FR-TIMEOUT-004**: Graceful degradation on timeout (fallback to manual review)
- **FR-TIMEOUT-005**: User notification on timeout with estimated completion time


## 13. Human-in-the-Loop Requirements

### 13.1 Manual Review Queue
- **FR-HIL-001**: Implement manual review queue for borderline cases
- **FR-HIL-002**: Support priority levels (high, medium, low)
- **FR-HIL-003**: Assign applications to credit officers
- **FR-HIL-004**: Track review status (pending, in_review, completed)
- **FR-HIL-005**: Provide complete application summary for review
- **FR-HIL-006**: Display AI recommendation with confidence score
- **FR-HIL-007**: Show underwriting reasoning and decision factors

### 13.2 Credit Officer Override
- **FR-HIL-008**: Allow credit officer to approve AI-rejected applications
- **FR-HIL-009**: Allow credit officer to reject AI-approved applications
- **FR-HIL-010**: Require mandatory reason for override
- **FR-HIL-011**: Verify officer authority level before override
- **FR-HIL-012**: Store override in audit trail with officer details
- **FR-HIL-013**: Notify senior management for high-value overrides

### 13.3 Escalation Rules
- **FR-HIL-014**: Escalate policy deviations to appropriate authority:
  - Minor deviation → Credit Manager
  - Major deviation → Regional Credit Head
  - Critical deviation → Chief Credit Officer
- **FR-HIL-015**: Escalate high-value loans (>₹50 lakh) to Regional Head
- **FR-HIL-016**: Escalate AML flags to Compliance Officer
- **FR-HIL-017**: Escalate fraud signals to Chief Compliance Officer
- **FR-HIL-018**: Support manual escalation by credit officer
- **FR-HIL-019**: Track escalation history and resolution time

### 13.4 Credit Officer Dashboard
- **FR-HIL-020**: Display pending review queue with filters
- **FR-HIL-021**: Show application details with AI analysis
- **FR-HIL-022**: Provide approve/reject/request-more-info actions
- **FR-HIL-023**: Display applicant credit history and documents
- **FR-HIL-024**: Show similar past applications for reference
- **FR-HIL-025**: Track officer performance metrics (approval rate, review time)


## 14. Monitoring & Observability Requirements

### 14.1 Metrics Collection
- **FR-MON-001**: Track agent request count by agent and status
- **FR-MON-002**: Track agent processing duration (p50, p95, p99)
- **FR-MON-003**: Track active session count
- **FR-MON-004**: Track stage transition counts
- **FR-MON-005**: Track API success/failure rates
- **FR-MON-006**: Track cache hit/miss rates
- **FR-MON-007**: Track database query performance
- **FR-MON-008**: Export metrics in Prometheus format

### 14.2 Structured Logging
- **FR-MON-009**: Implement structured logging in JSON format
- **FR-MON-010**: Include session_id, user_id, stage in all logs
- **FR-MON-011**: Log all agent transitions with reasoning
- **FR-MON-012**: Log all API calls with duration and status
- **FR-MON-013**: Log all errors with stack traces
- **FR-MON-014**: Log all security events (auth failures, access denied)
- **FR-MON-015**: Support log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **FR-MON-016**: Centralized log aggregation (ELK stack compatible)

### 14.3 Conversion Funnel Analytics
- **FR-MON-017**: Track user count at each stage (Lead, Sales, Verification, Underwriting, Sanction)
- **FR-MON-018**: Calculate conversion rates between stages
- **FR-MON-019**: Identify drop-off points and reasons
- **FR-MON-020**: Track average time spent at each stage
- **FR-MON-021**: Calculate overall lead-to-sanction conversion rate
- **FR-MON-022**: Segment analytics by loan type, bank, user demographics

### 14.4 Real-Time Dashboard
- **FR-MON-023**: Display active sessions count
- **FR-MON-024**: Display conversion funnel visualization
- **FR-MON-025**: Display agent performance metrics
- **FR-MON-026**: Display API health status
- **FR-MON-027**: Display system health (CPU, memory, disk)
- **FR-MON-028**: Display error rate trends
- **FR-MON-029**: Support real-time updates (WebSocket or polling)
- **FR-MON-030**: Support date range filtering

### 14.5 Alerting
- **FR-MON-031**: Alert on API failure rate >5%
- **FR-MON-032**: Alert on average response time >5 seconds
- **FR-MON-033**: Alert on error rate >1%
- **FR-MON-034**: Alert on system downtime
- **FR-MON-035**: Alert on database connection failures
- **FR-MON-036**: Alert on cache failures
- **FR-MON-037**: Support multiple alert channels (email, SMS, Slack)


## 15. Role-Based Access Control Requirements

### 15.1 User Roles
- **FR-RBAC-001**: Support Customer role (view own application)
- **FR-RBAC-002**: Support Credit Officer role (review and approve applications)
- **FR-RBAC-003**: Support Credit Manager role (override decisions, view team performance)
- **FR-RBAC-004**: Support Regional Credit Head role (approve high-value loans, view regional analytics)
- **FR-RBAC-005**: Support Chief Credit Officer role (approve critical deviations, view all analytics)
- **FR-RBAC-006**: Support Compliance Officer role (review AML flags, audit access)
- **FR-RBAC-007**: Support Admin role (manage users, update policies, system configuration)

### 15.2 Permission Management
- **FR-RBAC-008**: Define granular permissions (view, approve, reject, override, update, manage)
- **FR-RBAC-009**: Map permissions to roles
- **FR-RBAC-010**: Support role hierarchy (higher roles inherit lower role permissions)
- **FR-RBAC-011**: Enforce permission checks on all API endpoints
- **FR-RBAC-012**: Return 403 Forbidden for insufficient permissions
- **FR-RBAC-013**: Support temporary permission grants (time-limited)

### 15.3 Authentication & Authorization
- **FR-RBAC-014**: Implement JWT-based authentication
- **FR-RBAC-015**: Support token expiration (30 minutes for customers, 8 hours for staff)
- **FR-RBAC-016**: Support token refresh mechanism
- **FR-RBAC-017**: Implement password hashing (bcrypt)
- **FR-RBAC-018**: Support password complexity requirements
- **FR-RBAC-019**: Implement account lockout after 5 failed login attempts
- **FR-RBAC-020**: Support password reset via email

### 15.4 Audit Trail for Access
- **FR-RBAC-021**: Log all user login attempts (success and failure)
- **FR-RBAC-022**: Log all permission checks (granted and denied)
- **FR-RBAC-023**: Log all data access (who accessed what, when)
- **FR-RBAC-024**: Log all override actions with officer details
- **FR-RBAC-025**: Store audit logs for 7 years
- **FR-RBAC-026**: Support audit log search and filtering
- **FR-RBAC-027**: Generate audit reports for compliance


## 16. Policy Management Requirements

### 16.1 Policy Configuration
- **FR-POLICY-001**: Store bank policies in structured format (JSON/YAML)
- **FR-POLICY-002**: Support policy versioning (v1, v2, v3)
- **FR-POLICY-003**: Support policy effective dates
- **FR-POLICY-004**: Allow policy updates without code deployment
- **FR-POLICY-005**: Validate policy changes before activation
- **FR-POLICY-006**: Support policy rollback to previous version

### 16.2 Policy Update Workflow
- **FR-POLICY-007**: Admin can create policy draft
- **FR-POLICY-008**: Admin can preview policy impact (affected applications)
- **FR-POLICY-009**: Admin can activate policy (with effective date)
- **FR-POLICY-010**: System applies new policy to new applications only
- **FR-POLICY-011**: Existing applications continue with old policy (grandfathering)
- **FR-POLICY-012**: Notify credit officers of policy changes

### 16.3 Policy Audit
- **FR-POLICY-013**: Track all policy changes with timestamp and admin details
- **FR-POLICY-014**: Store policy change history
- **FR-POLICY-015**: Support policy comparison (diff view)
- **FR-POLICY-016**: Generate policy change reports


## 17. Fraud Detection Requirements

### 17.1 Basic Fraud Checks
- **FR-FRAUD-001**: Detect duplicate applications (same PAN, Aadhaar, phone)
- **FR-FRAUD-002**: Detect velocity anomalies (multiple applications in short time)
- **FR-FRAUD-003**: Detect suspicious income claims (income vs employment type mismatch)
- **FR-FRAUD-004**: Detect address mismatches (PAN vs Aadhaar vs provided address)
- **FR-FRAUD-005**: Detect suspicious employment claims (company not found, fake HR contact)
- **FR-FRAUD-006**: Flag applications with multiple AML hits

### 17.2 IP & Device Tracking
- **FR-FRAUD-007**: Track IP address for each session
- **FR-FRAUD-008**: Detect IP reputation (VPN, proxy, known fraud IPs)
- **FR-FRAUD-009**: Track device fingerprint (browser, OS, screen resolution)
- **FR-FRAUD-010**: Detect multiple accounts from same device
- **FR-FRAUD-011**: Flag applications from high-risk geographies

### 17.3 Fraud Scoring
- **FR-FRAUD-012**: Calculate fraud risk score (0-100)
- **FR-FRAUD-013**: Classify fraud risk (low, medium, high, critical)
- **FR-FRAUD-014**: Auto-reject critical fraud risk applications
- **FR-FRAUD-015**: Escalate high fraud risk to compliance officer
- **FR-FRAUD-016**: Store fraud signals in application record

### 17.4 Fraud Reporting
- **FR-FRAUD-017**: Generate daily fraud report (flagged applications)
- **FR-FRAUD-018**: Track fraud detection accuracy (false positives, false negatives)
- **FR-FRAUD-019**: Support manual fraud investigation workflow
- **FR-FRAUD-020**: Maintain fraud blacklist (PAN, Aadhaar, phone, email)


## 18. Additional Non-Functional Requirements

### 18.1 Disaster Recovery
- **NFR-DR-001**: Database backup every 6 hours
- **NFR-DR-002**: Point-in-time recovery capability (last 7 days)
- **NFR-DR-003**: Backup retention for 90 days
- **NFR-DR-004**: Disaster recovery plan documented
- **NFR-DR-005**: Recovery Time Objective (RTO): 4 hours
- **NFR-DR-006**: Recovery Point Objective (RPO): 6 hours
- **NFR-DR-007**: Regular disaster recovery drills (quarterly)

### 18.2 High Availability
- **NFR-HA-001**: Multi-instance deployment (minimum 2 instances)
- **NFR-HA-002**: Load balancer with health checks
- **NFR-HA-003**: Database replication (master-slave)
- **NFR-HA-004**: Redis clustering for cache
- **NFR-HA-005**: Automatic failover on instance failure
- **NFR-HA-006**: Zero-downtime deployments (blue-green or rolling)

### 18.3 Data Retention
- **NFR-DR-008**: Customer data retention: 7 years (RBI requirement)
- **NFR-DR-009**: Audit logs retention: 7 years
- **NFR-DR-010**: Session data retention: 90 days
- **NFR-DR-011**: Archived data stored in cold storage
- **NFR-DR-012**: Support data deletion on customer request (GDPR-like)

### 18.4 API Rate Limiting
- **NFR-RL-001**: Customer API: 100 requests/minute per user
- **NFR-RL-002**: Staff API: 500 requests/minute per user
- **NFR-RL-003**: Admin API: 1000 requests/minute
- **NFR-RL-004**: Return 429 Too Many Requests on limit exceeded
- **NFR-RL-005**: Include rate limit headers in response

### 18.5 Documentation
- **NFR-DOC-001**: API documentation (OpenAPI/Swagger)
- **NFR-DOC-002**: Architecture documentation (design.md)
- **NFR-DOC-003**: Requirements documentation (requirements.md)
- **NFR-DOC-004**: Deployment guide
- **NFR-DOC-005**: User manual for credit officers
- **NFR-DOC-006**: Admin guide for policy management
- **NFR-DOC-007**: Troubleshooting guide


## 19. Success Metrics (Updated)

### 19.1 Business Metrics
- **BSM-007**: 70% straight-through processing (no manual intervention)
- **BSM-008**: 90% customer satisfaction (CSAT)
- **BSM-009**: 60% lead-to-application conversion
- **BSM-010**: 45% application-to-sanction conversion
- **BSM-011**: <24 hours average processing time (inquiry to sanction)
- **BSM-012**: 50% reduction in operational costs vs manual process

### 19.2 Technical Metrics
- **TSM-007**: 99.5% system uptime
- **TSM-008**: <3 seconds average response time
- **TSM-009**: 95% API success rate
- **TSM-010**: 80% cache hit rate
- **TSM-011**: <1% error rate
- **TSM-012**: Zero security incidents

### 19.3 AI/ML Metrics
- **AIM-006**: 90% intent classification accuracy
- **AIM-007**: 85% RAG retrieval relevance
- **AIM-008**: 95% underwriting decision consistency
- **AIM-009**: <5% false positive rate in fraud detection
- **AIM-010**: 80% lead scoring accuracy

### 19.4 Operational Metrics
- **OPM-001**: <2 hours average manual review time
- **OPM-002**: 95% SLA compliance for credit officer response
- **OPM-003**: <10% override rate (AI decisions overridden by officers)
- **OPM-004**: 90% first-time document acceptance rate
- **OPM-005**: <5% escalation rate to senior management


## 20. Risk Mitigation (Updated)

### 20.1 Technical Risk Mitigation
- **RM-TECH-001**: Implement retry logic for all external APIs
- **RM-TECH-002**: Implement circuit breakers to prevent cascade failures
- **RM-TECH-003**: Implement graceful degradation (fallback to manual review)
- **RM-TECH-004**: Implement comprehensive error handling
- **RM-TECH-005**: Implement health checks for all services
- **RM-TECH-006**: Implement automated testing (unit, integration, E2E)
- **RM-TECH-007**: Implement load testing before production

### 20.2 Business Risk Mitigation
- **RM-BUS-001**: Human oversight for all critical decisions
- **RM-BUS-002**: Credit officer override capability
- **RM-BUS-003**: Escalation workflow for policy deviations
- **RM-BUS-004**: Comprehensive audit trail for compliance
- **RM-BUS-005**: Regular compliance audits
- **RM-BUS-006**: Customer consent management
- **RM-BUS-007**: Transparent communication of decisions

### 20.3 Security Risk Mitigation
- **RM-SEC-001**: Encryption at rest and in transit
- **RM-SEC-002**: Regular security audits and penetration testing
- **RM-SEC-003**: Access control and authentication
- **RM-SEC-004**: Rate limiting to prevent abuse
- **RM-SEC-005**: Input validation to prevent injection attacks
- **RM-SEC-006**: Security monitoring and alerting
- **RM-SEC-007**: Incident response plan

---

**Document Version:** 3.0  
**Last Updated:** February 15, 2026  
**Author:** Dhanit Project Team  
**Status:** Production-Grade Requirements with Async, HIL, Monitoring, RBAC & Fraud Detection  
**Related Documents:** design.md, system_boundaries.md, risk_assumptions.md


## 21. Post-Sanction & Customer Acceptance Requirements

### 21.1 Customer Acceptance Flow
- **FR-ACC-001**: Present final sanction terms to customer (amount, rate, tenure, EMI, conditions)
- **FR-ACC-002**: Display sanction validity period (90 days)
- **FR-ACC-003**: Provide clear accept/reject/clarify/modify actions
- **FR-ACC-004**: Calculate and display exact EMI amount
- **FR-ACC-005**: Show complete EMI schedule with due dates
- **FR-ACC-006**: Display all conditions and requirements clearly

### 21.2 Acceptance Capture
- **FR-ACC-007**: Capture customer acceptance with timestamp
- **FR-ACC-008**: Capture customer rejection with mandatory reason
- **FR-ACC-009**: Lock all terms immediately upon acceptance (immutable)
- **FR-ACC-010**: Generate acceptance confirmation document
- **FR-ACC-011**: Send acceptance confirmation via email/SMS
- **FR-ACC-012**: Update CRM status to 'accepted' or 'rejected'

### 21.3 Terms Locking
- **FR-ACC-013**: Freeze interest rate after acceptance
- **FR-ACC-014**: Lock loan amount after acceptance
- **FR-ACC-015**: Lock tenure after acceptance
- **FR-ACC-016**: Store locked terms in immutable format (JSONB)
- **FR-ACC-017**: Prevent any modification to locked terms
- **FR-ACC-018**: Maintain audit trail of locked terms

### 21.4 Rejection Handling
- **FR-ACC-019**: Capture rejection reason (rate too high, amount insufficient, conditions unacceptable, other)
- **FR-ACC-020**: Update CRM for re-engagement workflow
- **FR-ACC-021**: Notify relationship manager of rejection
- **FR-ACC-022**: Trigger feedback collection
- **FR-ACC-023**: Allow re-application after 30 days

### 21.5 Clarification Requests
- **FR-ACC-024**: Route clarification requests to Customer Support Agent
- **FR-ACC-025**: Maintain acceptance pending status during clarification
- **FR-ACC-026**: Resume acceptance flow after clarification
- **FR-ACC-027**: Track clarification response time

### 21.6 Modification Requests
- **FR-ACC-028**: Route modification requests to Credit Officer
- **FR-ACC-029**: Require credit officer approval for modifications
- **FR-ACC-030**: Re-run underwriting if significant changes requested
- **FR-ACC-031**: Generate new sanction letter if approved
- **FR-ACC-032**: Track modification history


## 22. Disbursement Requirements

### 22.1 Pre-Disbursement Checks
- **FR-DIS-001**: Verify customer acceptance status
- **FR-DIS-002**: Check document completeness (all required docs submitted)
- **FR-DIS-003**: Verify e-signature completion on loan agreement
- **FR-DIS-004**: Check collateral registration (if applicable)
- **FR-DIS-005**: Verify insurance policy (if required)
- **FR-DIS-006**: Validate bank account details for disbursement
- **FR-DIS-007**: Perform final AML check before disbursement

### 22.2 EMI Schedule Generation
- **FR-DIS-008**: Calculate exact EMI using standard formula
- **FR-DIS-009**: Generate complete EMI schedule (month-wise breakdown)
- **FR-DIS-010**: Show principal and interest components for each EMI
- **FR-DIS-011**: Calculate outstanding balance after each EMI
- **FR-DIS-012**: Determine first EMI due date (typically 30 days from disbursement)
- **FR-DIS-013**: Store EMI schedule in database
- **FR-DIS-014**: Provide EMI schedule download (PDF)

### 22.3 Disbursement Trigger (Simulated in MVP)
- **FR-DIS-015**: Generate unique loan account number
- **FR-DIS-016**: Simulate disbursement to customer account (mock CBS integration)
- **FR-DIS-017**: Record disbursement date and time
- **FR-DIS-018**: Record disbursement mode (NEFT/RTGS/Cheque)
- **FR-DIS-019**: Generate disbursement reference number
- **FR-DIS-020**: Mark disbursement as 'simulated' in MVP

### 22.4 Disbursement Confirmation
- **FR-DIS-021**: Send disbursement confirmation email
- **FR-DIS-022**: Send disbursement confirmation SMS
- **FR-DIS-023**: Include loan account number in confirmation
- **FR-DIS-024**: Include first EMI due date in confirmation
- **FR-DIS-025**: Provide link to EMI schedule and loan dashboard

### 22.5 Post-Disbursement Updates
- **FR-DIS-026**: Update loan status to 'disbursed'
- **FR-DIS-027**: Update CRM with disbursement details
- **FR-DIS-028**: Update LOS (Loan Origination System) status
- **FR-DIS-029**: Trigger repayment tracking setup (future phase)
- **FR-DIS-030**: Archive application documents

### 22.6 Disbursement Failure Handling
- **FR-DIS-031**: Detect disbursement failures (API timeout, account invalid)
- **FR-DIS-032**: Retry disbursement (3 attempts with 1-hour gap)
- **FR-DIS-033**: Route to manual intervention after retry exhaustion
- **FR-DIS-034**: Notify operations team of failure
- **FR-DIS-035**: Maintain disbursement attempt log

### 22.7 Production CBS Integration (Out of MVP Scope)
- **FR-DIS-036**: Define CBS API integration requirements
- **FR-DIS-037**: Support real-time fund transfer
- **FR-DIS-038**: Handle CBS response codes
- **FR-DIS-039**: Implement reconciliation process
- **FR-DIS-040**: Support rollback on failure


## 23. Customer Support & Case Management Requirements

### 23.1 Intent Detection
- **FR-CS-001**: Detect complaint intent from user message
- **FR-CS-002**: Classify issue type (delay, rejection, disbursement, technical, other)
- **FR-CS-003**: Assess urgency level (critical, high, medium, low)
- **FR-CS-004**: Perform sentiment analysis (positive, neutral, negative, angry)
- **FR-CS-005**: Detect escalation keywords ("speak to manager", "file complaint")

### 23.2 Auto-Response for Simple Queries
- **FR-CS-006**: Auto-respond to application status queries
- **FR-CS-007**: Auto-respond to document requirement queries
- **FR-CS-008**: Auto-respond to EMI schedule queries
- **FR-CS-009**: Auto-respond to interest rate queries
- **FR-CS-010**: Auto-respond to prepayment queries
- **FR-CS-011**: Provide FAQ-based responses
- **FR-CS-012**: Fallback to ticket creation if auto-response insufficient

### 23.3 Ticket Creation
- **FR-CS-013**: Generate unique ticket ID (format: TKT-YYYYMMDD-XXXX)
- **FR-CS-014**: Classify issue type automatically
- **FR-CS-015**: Assign priority based on urgency and sentiment
- **FR-CS-016**: Set SLA based on priority:
  - P1 (Critical): 2 hours
  - P2 (High): 8 hours
  - P3 (Medium): 24 hours
  - P4 (Low): 72 hours
- **FR-CS-017**: Auto-assign to appropriate support team
- **FR-CS-018**: Store complete conversation context with ticket
- **FR-CS-019**: Send ticket creation confirmation to customer

### 23.4 Ticket Lifecycle Management
- **FR-CS-020**: Support ticket statuses: open, assigned, in_progress, escalated, resolved, closed
- **FR-CS-021**: Track ticket assignment to support agent
- **FR-CS-022**: Allow support agent to update ticket status
- **FR-CS-023**: Allow support agent to add internal notes
- **FR-CS-024**: Allow support agent to add customer-facing comments
- **FR-CS-025**: Track all status changes with timestamp and agent ID

### 23.5 SLA Tracking & Escalation
- **FR-CS-026**: Track time elapsed since ticket creation
- **FR-CS-027**: Calculate time remaining to SLA breach
- **FR-CS-028**: Auto-escalate ticket on SLA breach
- **FR-CS-029**: Escalate to supervisor on SLA breach
- **FR-CS-030**: Escalate to manager if supervisor doesn't respond in 4 hours
- **FR-CS-031**: Send escalation notifications (email, SMS, Slack)
- **FR-CS-032**: Track escalation history

### 23.6 Ticket Resolution
- **FR-CS-033**: Allow support agent to mark ticket as resolved
- **FR-CS-034**: Require resolution notes (mandatory)
- **FR-CS-035**: Send resolution notification to customer
- **FR-CS-036**: Request customer feedback on resolution
- **FR-CS-037**: Auto-close ticket after 48 hours if no customer response
- **FR-CS-038**: Allow customer to reopen ticket within 7 days

### 23.7 Support Agent Dashboard
- **FR-CS-039**: Display assigned tickets with priority
- **FR-CS-040**: Show SLA countdown for each ticket
- **FR-CS-041**: Highlight tickets nearing SLA breach
- **FR-CS-042**: Provide ticket search and filter capabilities
- **FR-CS-043**: Show ticket history and conversation thread
- **FR-CS-044**: Display customer profile and loan details
- **FR-CS-045**: Track agent performance metrics (resolution time, customer satisfaction)

### 23.8 Integration with Other Agents
- **FR-CS-046**: Route technical issues to IT support
- **FR-CS-047**: Route policy questions to Sales Agent
- **FR-CS-048**: Route underwriting queries to Credit Officer
- **FR-CS-049**: Route disbursement issues to Operations Team
- **FR-CS-050**: Maintain context when routing between agents


## 24. Operational Dashboard Requirements

### 24.1 Lead Funnel Metrics
- **FR-DASH-001**: Display total leads (today, week, month, custom range)
- **FR-DASH-002**: Show lead score distribution (hot/warm/cold)
- **FR-DASH-003**: Calculate lead-to-sales conversion rate
- **FR-DASH-004**: Show average lead response time
- **FR-DASH-005**: Display lead source breakdown (web, mobile, referral)
- **FR-DASH-006**: Show lead trend over time (line chart)

### 24.2 Application Metrics
- **FR-DASH-007**: Show applications in progress by stage (bar chart)
- **FR-DASH-008**: Display applications completed today/week/month
- **FR-DASH-009**: Calculate average processing time per stage
- **FR-DASH-010**: Identify bottleneck stage (longest average time)
- **FR-DASH-011**: Show stage-wise conversion rates
- **FR-DASH-012**: Display drop-off analysis by stage

### 24.3 Approval Metrics
- **FR-DASH-013**: Calculate overall approval rate
- **FR-DASH-014**: Show approval rate by loan type
- **FR-DASH-015**: Show approval rate by bank
- **FR-DASH-016**: Display rejection rate with breakdown by reason
- **FR-DASH-017**: Show conditional approval rate
- **FR-DASH-018**: Display manual review queue size
- **FR-DASH-019**: Show average time in manual review
- **FR-DASH-020**: Display override rate by credit officers

### 24.4 Disbursement Metrics
- **FR-DASH-021**: Show disbursements today/week/month (count)
- **FR-DASH-022**: Display total disbursed amount
- **FR-DASH-023**: Calculate average time from sanction to disbursement
- **FR-DASH-024**: Show pending disbursements count
- **FR-DASH-025**: Display disbursement success rate
- **FR-DASH-026**: Show disbursement by loan type breakdown

### 24.5 Support Metrics
- **FR-DASH-027**: Display open tickets by priority (P1/P2/P3/P4)
- **FR-DASH-028**: Show average resolution time by priority
- **FR-DASH-029**: Calculate SLA compliance rate
- **FR-DASH-030**: Display escalation rate
- **FR-DASH-031**: Show ticket volume trend over time
- **FR-DASH-032**: Display customer satisfaction score (CSAT)

### 24.6 System Health Metrics
- **FR-DASH-033**: Display active sessions count
- **FR-DASH-034**: Show API success rates (PAN, Aadhaar, Credit Bureau, AML)
- **FR-DASH-035**: Display average API response times
- **FR-DASH-036**: Show cache hit rate
- **FR-DASH-037**: Display error rate (last hour, last day)
- **FR-DASH-038**: Show system uptime percentage

### 24.7 Dashboard Features
- **FR-DASH-039**: Support date range selection (today, yesterday, last 7 days, last 30 days, custom)
- **FR-DASH-040**: Support real-time updates (refresh every 30 seconds)
- **FR-DASH-041**: Support data export (CSV, Excel, PDF)
- **FR-DASH-042**: Support drill-down for detailed analysis
- **FR-DASH-043**: Support role-based dashboard views
- **FR-DASH-044**: Support dashboard customization (widget arrangement)


## 25. AI Monitoring Requirements

### 25.1 RAG Performance Monitoring
- **FR-AIM-001**: Track RAG query count (hourly, daily, weekly)
- **FR-AIM-002**: Measure average RAG retrieval time
- **FR-AIM-003**: Track similarity score distribution
- **FR-AIM-004**: Calculate RAG fallback rate (when RAG fails)
- **FR-AIM-005**: Monitor citation accuracy
- **FR-AIM-006**: Track RAG cache hit rate
- **FR-AIM-007**: Alert on RAG performance degradation (>5 seconds response time)

### 25.2 Agent Performance Monitoring
- **FR-AIM-008**: Track request count per agent
- **FR-AIM-009**: Measure average response time per agent
- **FR-AIM-010**: Calculate success rate per agent
- **FR-AIM-011**: Track error rate per agent
- **FR-AIM-012**: Monitor fallback frequency per agent
- **FR-AIM-013**: Alert on agent failure rate >5%

### 25.3 Decision Drift Monitoring
- **FR-AIM-014**: Track underwriting decision consistency over time
- **FR-AIM-015**: Compare recent approval rate with historical baseline
- **FR-AIM-016**: Detect significant drift (>10% change)
- **FR-AIM-017**: Alert on decision drift anomalies
- **FR-AIM-018**: Track override rate by credit officers
- **FR-AIM-019**: Identify decision pattern changes

### 25.4 Intent Classification Monitoring
- **FR-AIM-020**: Track intent classification confidence scores
- **FR-AIM-021**: Calculate misclassification rate
- **FR-AIM-022**: Track user correction rate (when user corrects intent)
- **FR-AIM-023**: Monitor classification accuracy by intent type
- **FR-AIM-024**: Alert on classification confidence <70%

### 25.5 Model Performance Alerts
- **FR-AIM-025**: Alert on RAG retrieval time >5 seconds
- **FR-AIM-026**: Alert on agent response time >10 seconds
- **FR-AIM-027**: Alert on error rate >5%
- **FR-AIM-028**: Alert on decision drift >10%
- **FR-AIM-029**: Alert on classification accuracy <80%
- **FR-AIM-030**: Send alerts via email, SMS, Slack


## 26. Complete State Machine Requirements

### 26.1 Stage Definitions
- **FR-SM-001**: Define LEAD stage (lead capture and qualification)
- **FR-SM-002**: Define SALES stage (product recommendation and pre-eligibility)
- **FR-SM-003**: Define VERIFICATION stage (KYC and document verification)
- **FR-SM-004**: Define UNDERWRITING stage (risk assessment and decision)
- **FR-SM-005**: Define MANUAL_REVIEW stage (credit officer review)
- **FR-SM-006**: Define SANCTION stage (sanction letter generation)
- **FR-SM-007**: Define ACCEPTANCE stage (customer acceptance/rejection)
- **FR-SM-008**: Define DISBURSEMENT stage (fund transfer orchestration)
- **FR-SM-009**: Define DISBURSED stage (loan active, repayment tracking)
- **FR-SM-010**: Define SUPPORT stage (customer support and case management)
- **FR-SM-011**: Define REJECTED stage (application rejected)
- **FR-SM-012**: Define CLOSED stage (loan closed/completed - future)

### 26.2 Stage Transitions
- **FR-SM-013**: Allow LEAD → SALES transition (when qualified)
- **FR-SM-014**: Allow SALES → VERIFICATION transition (when ready)
- **FR-SM-015**: Allow VERIFICATION → UNDERWRITING transition (when verified)
- **FR-SM-016**: Allow UNDERWRITING → SANCTION transition (when approved)
- **FR-SM-017**: Allow UNDERWRITING → MANUAL_REVIEW transition (when escalated)
- **FR-SM-018**: Allow UNDERWRITING → REJECTED transition (when rejected)
- **FR-SM-019**: Allow MANUAL_REVIEW → SANCTION transition (when approved by officer)
- **FR-SM-020**: Allow MANUAL_REVIEW → REJECTED transition (when rejected by officer)
- **FR-SM-021**: Allow SANCTION → ACCEPTANCE transition (when sanction issued)
- **FR-SM-022**: Allow ACCEPTANCE → DISBURSEMENT transition (when accepted)
- **FR-SM-023**: Allow ACCEPTANCE → REJECTED transition (when rejected by customer)
- **FR-SM-024**: Allow DISBURSEMENT → DISBURSED transition (when disbursed)
- **FR-SM-025**: Allow any stage → SUPPORT transition (when customer needs help)
- **FR-SM-026**: Allow SUPPORT → original stage transition (when issue resolved)

### 26.3 Transition Validation
- **FR-SM-027**: Validate transition is allowed before executing
- **FR-SM-028**: Prevent invalid transitions (e.g., LEAD → DISBURSEMENT)
- **FR-SM-029**: Log all transition attempts (successful and failed)
- **FR-SM-030**: Store transition reason and context
- **FR-SM-031**: Track transition timestamp

### 26.4 State Persistence
- **FR-SM-032**: Persist session state in Redis (for active sessions)
- **FR-SM-033**: Persist session state in database (for recovery)
- **FR-SM-034**: Support session recovery after disconnection
- **FR-SM-035**: Maintain complete state history for audit
- **FR-SM-036**: Store stage-specific data (lead_data, sales_data, etc.)

### 26.5 Failure Paths
- **FR-SM-037**: Define failure path from VERIFICATION (route to SUPPORT)
- **FR-SM-038**: Define failure path from UNDERWRITING (route to REJECTED or MANUAL_REVIEW)
- **FR-SM-039**: Define failure path from DISBURSEMENT (route to manual intervention)
- **FR-SM-040**: Allow retry from failure points
- **FR-SM-041**: Track failure reasons and resolution

### 26.6 Audit Logging
- **FR-SM-042**: Log every stage entry with timestamp
- **FR-SM-043**: Log every stage exit with timestamp
- **FR-SM-044**: Log stage duration
- **FR-SM-045**: Log transition triggers (user action, system event, timeout)
- **FR-SM-046**: Store complete audit trail for 7 years


## 27. Database Schema Updates

### 27.1 Customer Acceptance Table
- **FR-DB-027**: Create customer_acceptance table
- **FR-DB-028**: Store acceptance_id (PK), sanction_id (FK), user_id (FK)
- **FR-DB-029**: Store status (pending, accepted, rejected, expired)
- **FR-DB-030**: Store accepted_at, rejected_at timestamps
- **FR-DB-031**: Store rejection_reason (text)
- **FR-DB-032**: Store locked_terms (JSONB, immutable)

### 27.2 Disbursement Table
- **FR-DB-033**: Create disbursements table
- **FR-DB-034**: Store disbursement_id (PK), sanction_id (FK), user_id (FK)
- **FR-DB-035**: Store loan_account_number (unique)
- **FR-DB-036**: Store disbursed_amount, disbursement_date
- **FR-DB-037**: Store disbursement_mode (NEFT, RTGS, Cheque)
- **FR-DB-038**: Store status (pending, disbursed, failed)
- **FR-DB-039**: Store is_simulated flag (for MVP)

### 27.3 EMI Schedule Table
- **FR-DB-040**: Create emi_schedule table
- **FR-DB-041**: Store schedule_id (PK), loan_account_number (FK)
- **FR-DB-042**: Store month_number, emi_amount
- **FR-DB-043**: Store principal_amount, interest_amount
- **FR-DB-044**: Store outstanding_balance, due_date
- **FR-DB-045**: Store payment_status (pending, paid, overdue)

### 27.4 Support Tickets Table
- **FR-DB-046**: Create support_tickets table
- **FR-DB-047**: Store ticket_id (PK), user_id (FK)
- **FR-DB-048**: Store issue_type, priority, status
- **FR-DB-049**: Store message, assigned_to
- **FR-DB-050**: Store sla_hours, escalation_time
- **FR-DB-051**: Store created_at, resolved_at, closed_at

### 27.5 Ticket Escalations Table
- **FR-DB-052**: Create ticket_escalations table
- **FR-DB-053**: Store escalation_id (PK), ticket_id (FK)
- **FR-DB-054**: Store escalated_at, escalated_to
- **FR-DB-055**: Store reason (sla_breach, customer_request, critical_issue)

### 27.6 Session State Table
- **FR-DB-056**: Create session_state table
- **FR-DB-057**: Store session_id (PK), user_id (FK)
- **FR-DB-058**: Store current_stage, previous_stage
- **FR-DB-059**: Store stage_data (JSONB for each stage)
- **FR-DB-060**: Store created_at, last_updated


## 28. MVP vs Production Clarifications

### 28.1 MVP Scope (Simulated)
- **FR-MVP-001**: Disbursement is simulated (no real CBS integration)
- **FR-MVP-002**: Fund transfer is mocked (no actual money movement)
- **FR-MVP-003**: E-signature is simulated (no real e-sign integration)
- **FR-MVP-004**: Repayment tracking is out of scope
- **FR-MVP-005**: EMI collection is out of scope
- **FR-MVP-006**: Loan servicing is out of scope

### 28.2 Production Requirements (Future)
- **FR-PROD-001**: Real CBS integration for disbursement
- **FR-PROD-002**: Real payment gateway for EMI collection
- **FR-PROD-003**: Real e-signature integration (DocuSign, Adobe Sign)
- **FR-PROD-004**: Real-time repayment tracking
- **FR-PROD-005**: Automated EMI deduction
- **FR-PROD-006**: Loan closure workflow

### 28.3 Clear Documentation
- **FR-DOC-001**: Clearly mark simulated components in design.md
- **FR-DOC-002**: Document production integration requirements
- **FR-DOC-003**: Provide API specifications for future integrations
- **FR-DOC-004**: Document data migration requirements
- **FR-DOC-005**: Provide deployment guide for MVP vs Production


## 29. Updated Success Metrics

### 29.1 End-to-End Metrics
- **BSM-013**: 80% lead-to-disbursement conversion rate
- **BSM-014**: <48 hours average time from inquiry to disbursement
- **BSM-015**: 95% customer acceptance rate (of sanctioned loans)
- **BSM-016**: 90% disbursement success rate (first attempt)
- **BSM-017**: <2 hours average support ticket resolution time

### 29.2 Stage-Specific Metrics
- **BSM-018**: 70% lead qualification rate
- **BSM-019**: 85% verification success rate
- **BSM-020**: 60% underwriting approval rate
- **BSM-021**: <10% manual review escalation rate
- **BSM-022**: 95% sanction acceptance rate

### 29.3 Operational Efficiency Metrics
- **OPM-006**: <5% ticket escalation rate
- **OPM-007**: 95% SLA compliance for support tickets
- **OPM-008**: <3% disbursement failure rate
- **OPM-009**: 90% straight-through processing (no manual intervention)
- **OPM-010**: <5% customer drop-off rate post-sanction

---

**Document Version:** 4.0  
**Last Updated:** February 15, 2026  
**Author:** Dhanit Project Team  
**Status:** Complete End-to-End Loan Lifecycle Requirements  
**Related Documents:** design.md, system_boundaries.md, risk_assumptions.md, ARCHITECTURE_SUMMARY.md

**Summary of Additions:**
- Section 21: Post-Sanction & Customer Acceptance (32 requirements)
- Section 22: Disbursement (40 requirements)
- Section 23: Customer Support & Case Management (50 requirements)
- Section 24: Operational Dashboard (44 requirements)
- Section 25: AI Monitoring (30 requirements)
- Section 26: Complete State Machine (46 requirements)
- Section 27: Database Schema Updates (34 requirements)
- Section 28: MVP vs Production Clarifications (11 requirements)
- Section 29: Updated Success Metrics (15 requirements)

**Total New Requirements Added:** 302 functional requirements covering complete loan lifecycle from lead to disbursement, plus customer support, monitoring, and operational dashboards.
