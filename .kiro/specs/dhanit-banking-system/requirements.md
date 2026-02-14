# Dhanit Banking System - Requirements Document

## 1. Project Overview

### 1.1 System Description
The Dhanit Banking System is an AI-powered, multi-agent loan processing platform designed for Indian banking operations. The system automates the entire loan lifecycle from lead generation to sanction letter issuance through specialized AI agents that handle different stages of the banking process.

### 1.2 Business Context
- **Target Market**: Indian banking sector with focus on retail loans (Education, Home, Personal, Vehicle, Business)
- **Primary Users**: Loan applicants, bank staff, relationship managers
- **Business Model**: B2B2C platform serving banks and their customers
- **Regulatory Environment**: Compliant with RBI guidelines and Indian banking regulations

## 2. System Architecture & Technology Stack

### 2.1 Core Technologies
- **Backend Framework**: Python Flask
- **AI/ML Framework**: OpenAI GPT models, LangChain
- **Database**: ChromaDB (Vector database for RAG), SQLite
- **Document Processing**: RAG (Retrieval-Augmented Generation) engine
- **Frontend**: HTML/CSS/JavaScript (Chatbot interface)
- **Deployment**: Python-based microservices architecture

### 2.2 External Integrations
- **Credit Bureau APIs**: CIBIL, Experian, Equifax integration
- **KYC Services**: Aadhaar verification, PAN verification
- **AML Services**: Anti-Money Laundering checks
- **Banking APIs**: Core banking system integration
- **Document Services**: OCR for document processing
- **Communication**: SMS, Email, WhatsApp integration

## 3. Functional Requirements

### 3.1 Multi-Agent System Architecture

#### 3.1.1 Lead Generation Agent
**Purpose**: Capture and qualify potential loan leads
- **FR-LG-001**: Capture user intent and loan type preferences
- **FR-LG-002**: Score leads based on engagement and urgency (0-100 scale)
- **FR-LG-003**: Route qualified leads to appropriate agents
- **FR-LG-004**: Store lead data in CRM system
- **FR-LG-005**: Enable consent-based re-engagement for future opportunities

#### 3.1.2 Sales Agent
**Purpose**: Provide loan information and guide customers through product selection
- **FR-SA-001**: Present loan products based on user requirements
- **FR-SA-002**: Provide personalized loan recommendations using RAG engine
- **FR-SA-003**: Handle customer queries about loan terms and conditions
- **FR-SA-004**: Collect preliminary customer information
- **FR-SA-005**: Transition qualified customers to verification process

#### 3.1.3 Verification Agent
**Purpose**: Perform KYC and document verification
- **FR-VA-001**: Verify PAN card details against government database
- **FR-VA-002**: Perform Aadhaar verification with OTP validation
- **FR-VA-003**: Conduct AML (Anti-Money Laundering) checks
- **FR-VA-004**: Validate document authenticity
- **FR-VA-005**: Generate verification status report

#### 3.1.4 Underwriting Agent
**Purpose**: Assess creditworthiness and make loan decisions
- **FR-UW-001**: Evaluate credit scores from multiple bureaus
- **FR-UW-002**: Calculate FOIR (Fixed Obligations to Income Ratio)
- **FR-UW-003**: Apply bank-specific lending policies
- **FR-UW-004**: Handle OSR (On Sanction Risk) deviations
- **FR-UW-005**: Generate credit decisions (Approved/Conditionally Approved/Rejected)
- **FR-UW-006**: Determine loan terms, amounts, and conditions

#### 3.1.5 Sanction Agent
**Purpose**: Issue formal loan sanction letters and handle post-approval processes
- **FR-SN-001**: Generate bank-compliant sanction letters
- **FR-SN-002**: Communicate approval terms and conditions
- **FR-SN-003**: Handle post-sanction clarifications
- **FR-SN-004**: Route complaints to customer support
- **FR-SN-005**: Maintain sanction validity tracking

### 3.2 Master Agent Orchestration
- **FR-MA-001**: Route user requests to appropriate specialized agents
- **FR-MA-002**: Maintain session state across agent transitions
- **FR-MA-003**: Handle agent-to-agent data transfer
- **FR-MA-004**: Provide fallback routing for unhandled scenarios

### 3.3 RAG (Retrieval-Augmented Generation) System
- **FR-RAG-001**: Ingest and index bank policy documents
- **FR-RAG-002**: Provide accurate, citation-backed responses
- **FR-RAG-003**: Support multiple document formats (PDF, MD, HTML)
- **FR-RAG-004**: Enable real-time policy updates without system restart

### 3.4 Loan Product Support
The system must support the following loan types with bank-specific policies:

#### 3.4.1 Education Loans
- **FR-ED-001**: Support domestic and international education financing
- **FR-ED-002**: Handle moratorium periods during study
- **FR-ED-003**: Process co-applicant requirements
- **FR-ED-004**: Calculate collateral requirements based on loan amount

#### 3.4.2 Home Loans
- **FR-HL-001**: Support property purchase and construction loans
- **FR-HL-002**: Calculate LTV (Loan-to-Value) ratios
- **FR-HL-003**: Handle balance transfer cases
- **FR-HL-004**: Process joint applicant scenarios

#### 3.4.3 Personal Loans
- **FR-PL-001**: Unsecured loan processing
- **FR-PL-002**: Income-based eligibility assessment
- **FR-PL-003**: Quick approval for existing customers
- **FR-PL-004**: Flexible tenure options

#### 3.4.4 Vehicle Loans
- **FR-VL-001**: Support new and used vehicle financing
- **FR-VL-002**: Handle vehicle hypothecation
- **FR-VL-003**: Process dealer tie-up scenarios
- **FR-VL-004**: Electric vehicle incentive processing

#### 3.4.5 Business Loans
- **FR-BL-001**: MSME loan processing
- **FR-BL-002**: MUDRA loan scheme integration
- **FR-BL-003**: Working capital and term loan options
- **FR-BL-004**: GST and business document verification

### 3.5 Multi-Bank Support
- **FR-MB-001**: Support multiple bank policies (SBI, HDFC, ICICI, Axis)
- **FR-MB-002**: Bank-specific interest rate calculations
- **FR-MB-003**: Customizable eligibility criteria per bank
- **FR-MB-004**: Bank-specific document requirements

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
- **NFR-P-001**: System response time < 3 seconds for agent responses
- **NFR-P-002**: Support concurrent users up to 1000 simultaneous sessions
- **NFR-P-003**: RAG query response time < 2 seconds
- **NFR-P-004**: 99.5% system uptime availability

### 4.2 Security Requirements
- **NFR-S-001**: Encrypt all customer PII data at rest and in transit
- **NFR-S-002**: Implement role-based access control
- **NFR-S-003**: Audit trail for all customer interactions
- **NFR-S-004**: Secure API endpoints with authentication
- **NFR-S-005**: Compliance with RBI data protection guidelines

### 4.3 Scalability Requirements
- **NFR-SC-001**: Horizontal scaling capability for agent services
- **NFR-SC-002**: Database partitioning for large customer datasets
- **NFR-SC-003**: Load balancing across multiple service instances
- **NFR-SC-004**: Auto-scaling based on traffic patterns

### 4.4 Integration Requirements
- **NFR-I-001**: RESTful API design for external integrations
- **NFR-I-002**: Webhook support for real-time notifications
- **NFR-I-003**: Standard banking message formats (ISO 20022)
- **NFR-I-004**: Backward compatibility for API versions

### 4.5 Compliance Requirements
- **NFR-C-001**: RBI compliance for digital lending guidelines
- **NFR-C-002**: Data localization as per Indian regulations
- **NFR-C-003**: KYC compliance with PMLA requirements
- **NFR-C-004**: Fair lending practice adherence

## 5. User Stories

### 5.1 Customer Journey Stories

#### 5.1.1 Loan Inquiry
**As a** potential loan customer  
**I want to** inquire about loan options through a chatbot  
**So that** I can understand available products without visiting a branch

**Acceptance Criteria:**
- System captures my loan type preference
- I receive relevant loan information
- My inquiry is recorded for follow-up
- I can proceed to application if interested

#### 5.1.2 Loan Application
**As a** qualified loan applicant  
**I want to** complete my loan application online  
**So that** I can apply conveniently from anywhere

**Acceptance Criteria:**
- System guides me through required information
- Documents can be uploaded digitally
- Application status is tracked in real-time
- I receive confirmation of submission

#### 5.1.3 Application Status Tracking
**As a** loan applicant  
**I want to** track my application status  
**So that** I know the progress and next steps

**Acceptance Criteria:**
- Real-time status updates are provided
- Clear communication of required actions
- Estimated timelines are communicated
- Notifications are sent for status changes

### 5.2 Bank Staff Stories

#### 5.2.1 Application Review
**As a** bank relationship manager  
**I want to** review AI-processed applications  
**So that** I can make informed decisions on borderline cases

**Acceptance Criteria:**
- Complete application summary is available
- AI recommendations are clearly presented
- Override capabilities exist for special cases
- Audit trail is maintained for decisions

#### 5.2.2 Policy Management
**As a** bank policy administrator  
**I want to** update lending policies in the system  
**So that** current guidelines are always applied

**Acceptance Criteria:**
- Policy changes can be made without code deployment
- Changes take effect immediately
- Historical policy versions are maintained
- Impact analysis is provided for changes

## 6. System Constraints

### 6.1 Technical Constraints
- **TC-001**: Python 3.8+ runtime environment required
- **TC-002**: Minimum 16GB RAM for optimal performance
- **TC-003**: ChromaDB storage requirements scale with document volume
- **TC-004**: Internet connectivity required for external API calls

### 6.2 Business Constraints
- **BC-001**: Compliance with individual bank's lending policies
- **BC-002**: Integration timeline dependent on bank API availability
- **BC-003**: Regulatory approval required for production deployment
- **BC-004**: Customer consent required for data processing

### 6.3 Regulatory Constraints
- **RC-001**: Data residency within Indian borders
- **RC-002**: Customer data retention as per RBI guidelines
- **RC-003**: Audit trail retention for 7 years minimum
- **RC-004**: Real-time reporting to regulatory authorities

## 7. Success Criteria

### 7.1 Business Success Metrics
- **BSM-001**: 80% reduction in loan processing time
- **BSM-002**: 90% customer satisfaction score
- **BSM-003**: 95% straight-through processing for qualified applications
- **BSM-004**: 50% reduction in operational costs

### 7.2 Technical Success Metrics
- **TSM-001**: 99.5% system availability
- **TSM-002**: <3 second average response time
- **TSM-003**: Zero security incidents
- **TSM-004**: 95% API success rate

### 7.3 User Experience Metrics
- **UXM-001**: 85% task completion rate
- **UXM-002**: <5 clicks to complete loan inquiry
- **UXM-003**: 90% user retention through application process
- **UXM-004**: <2 minutes average session time for information gathering

## 8. Risk Assessment

### 8.1 Technical Risks
- **TR-001**: AI model accuracy degradation over time
- **TR-002**: External API dependency failures
- **TR-003**: Data quality issues affecting decisions
- **TR-004**: Scalability bottlenecks during peak loads

### 8.2 Business Risks
- **BR-001**: Regulatory changes affecting system design
- **BR-002**: Bank policy changes requiring system updates
- **BR-003**: Competition from established banking platforms
- **BR-004**: Customer adoption challenges

### 8.3 Compliance Risks
- **CR-001**: Data privacy violations
- **CR-002**: Discriminatory lending practices
- **CR-003**: Inadequate audit trails
- **CR-004**: Cross-border data transfer violations

## 9. Future Enhancements

### 9.1 Planned Features
- **FE-001**: Mobile application development
- **FE-002**: Voice-based interaction capabilities
- **FE-003**: Advanced analytics and reporting dashboard
- **FE-004**: Machine learning model for fraud detection

### 9.2 Integration Roadmap
- **IR-001**: Core banking system integration
- **IR-002**: Payment gateway integration
- **IR-003**: Document management system integration
- **IR-004**: CRM system integration

