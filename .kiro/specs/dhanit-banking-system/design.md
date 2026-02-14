# Dhanit Banking System - Design Document

## 1. System Architecture Overview

### 1.1 Master Agent Orchestration Pattern
The Dhanit Banking System follows a **Master Agent Orchestration** pattern where a central Master Agent automatically routes user interactions through a sequential pipeline of specialized AI agents. Each agent handles a specific stage of the loan processing workflow.

```
User Request → Master Agent → [Agent Pipeline] → Response
                    ↓
    [LEAD] → [SALES] → [VERIFICATION] → [UNDERWRITING] → [SANCTION]
```

### 1.2 Core Design Principles
- **Sequential Processing**: Each agent completes its stage before transitioning to the next
- **State Management**: Master Agent maintains session state across agent transitions
- **Automatic Routing**: No manual intervention required for standard loan processing
- **Contextual Handoffs**: Each agent passes relevant data to the next stage
- **Fallback Handling**: Master Agent provides fallback routing for edge cases

## 2. Master Agent Design

### 2.1 Master Agent Architecture

```python
class MasterAgent:
    def __init__(self):
        self.session_state = {
            "stage": "LEAD",                    # Current processing stage
            "verification_context": None,       # Data for verification
            "sanction_data": None,             # Data for sanction
            "user_context": {},                # User information
            "conversation_history": []         # Full conversation log
        }
        
        # Initialize specialized agents
        self.lead_agent = LeadGenerationAgent()
        self.sales_agent = LoanSalesAgent()
        self.verification_agent = VerificationAgent()
        self.underwriting_agent = UnderwritingAgent()
        self.sanction_agent = SanctionAgent()
```

### 2.2 Stage Transition Logic

The Master Agent uses a **finite state machine** approach:

```python
def process_user_message(self, user_message: str) -> dict:
    current_stage = self.session_state["stage"]
    
    if current_stage == "LEAD":
        response = self.lead_agent.handle_lead(user_message)
        if response.get("qualified"):
            self.session_state["stage"] = "SALES"
        return response
    
    elif current_stage == "SALES":
        response = self.sales_agent.handle_sales(user_message)
        if response.get("signals", {}).get("ready_for_verification"):
            self.session_state["stage"] = "VERIFICATION"
            self.session_state["verification_context"] = response.get("data")
        return response
    
    elif current_stage == "VERIFICATION":
        response = self.verification_agent.handle_verification(
            self.session_state["verification_context"]
        )
        if response.get("status") == "VERIFIED":
            self.session_state["stage"] = "UNDERWRITING"
        return response
    
    elif current_stage == "UNDERWRITING":
        response = self.underwriting_agent.handle_underwriting(user_message)
        decision = response.get("signals", {}).get("decision")
        if decision in ["Approved", "Conditionally Approved"]:
            self.session_state["stage"] = "SANCTION"
            self.session_state["sanction_data"] = response.get("data")
        return response
    
    elif current_stage == "SANCTION":
        return self.sanction_agent.run(
            user_message=user_message,
            sanction_context=self.session_state["sanction_data"]
        )
    
    # Fallback
    return {"reply": "Routing to human support", "agent": "FALLBACK"}
```

## 3. Agent Pipeline Design

### 3.1 Stage 1: Lead Generation Agent

**Purpose**: Capture and qualify potential loan leads
**Trigger**: Initial user contact
**Duration**: Single interaction

```python
class LeadGenerationAgent:
    def handle_lead(self, user_message: str) -> dict:
        # Extract loan intent and user signals
        intent = self.classify_loan_intent(user_message)
        urgency = self.assess_urgency(user_message)
        lead_score = self.calculate_lead_score(intent, urgency)
        
        # Store in CRM
        lead_id = self.store_lead_data({
            "intent": intent,
            "urgency": urgency,
            "score": lead_score,
            "message": user_message
        })
        
        return {
            "agent": "LEAD_GENERATION",
            "qualified": lead_score > 30,  # Threshold for sales handoff
            "lead_id": lead_id,
            "response": self.generate_welcome_response(intent)
        }
```

**Transition Criteria**: Lead score > 30 (qualified lead)

### 3.2 Stage 2: Sales Agent

**Purpose**: Product recommendation and customer engagement
**Trigger**: Qualified lead from Lead Agent
**Duration**: Multi-turn conversation

```python
class LoanSalesAgent:
    def handle_sales(self, user_message: str) -> dict:
        # Analyze user communication style
        self.analyze_user_style(user_message)
        
        # Detect loan type and provide recommendations
        loan_type = self.detect_loan_type(user_message)
        if loan_type:
            response = self.present_loan_options_with_rag(loan_type)
        else:
            response = self.ask_micro_question()
        
        # Check if ready for verification
        ready_for_verification = self.assess_verification_readiness()
        
        return {
            "agent": "SALES",
            "response": response,
            "signals": {
                "ready_for_verification": ready_for_verification
            },
            "data": {
                "loan_type": loan_type,
                "user_profile": self.user_context.__dict__,
                "conversation_stage": self.conversation_stage
            }
        }
    
    def assess_verification_readiness(self) -> bool:
        # Check if user has provided sufficient information
        return (
            self.user_context.loan_type is not None and
            self.user_context.monthly_income is not None and
            self.conversation_stage == "commitment"
        )
```

**Transition Criteria**: User provides complete information and shows commitment

### 3.3 Stage 3: Verification Agent

**Purpose**: KYC, document verification, and AML checks
**Trigger**: Sales Agent completion
**Duration**: Automated processing

```python
class VerificationAgent:
    def handle_verification(self, context: dict) -> dict:
        verification_results = {}
        
        # Step 1: PAN Verification
        pan_result = self.verify_pan(context.get("pan"), context.get("name"))
        if not pan_result["verified"]:
            return self.create_failure_response("PAN_VERIFICATION_FAILED")
        
        # Step 2: Aadhaar Verification
        aadhaar_result = self.verify_aadhaar(context.get("aadhaar"), context.get("otp"))
        if not aadhaar_result["verified"]:
            return self.create_failure_response("AADHAAR_VERIFICATION_FAILED")
        
        # Step 3: AML Check
        aml_result = self.run_aml_check(context.get("name"), context.get("pan"))
        if aml_result["blacklisted"] or aml_result["risk_score"] > 70:
            return self.create_failure_response("AML_HIGH_RISK")
        
        return {
            "agent": "VERIFICATION",
            "status": "VERIFIED",
            "signals": {
                "kyc_completed": True,
                "aml_passed": True
            },
            "verification_data": {
                "pan_verified": True,
                "aadhaar_verified": True,
                "aml_score": aml_result["risk_score"]
            }
        }
```

**Transition Criteria**: All verification checks pass

### 3.4 Stage 4: Underwriting Agent

**Purpose**: Credit assessment and loan decision
**Trigger**: Successful verification
**Duration**: Automated processing with possible user clarification

```python
class UnderwritingAgent:
    def handle_underwriting(self, user_message: str) -> dict:
        # Pull credit bureau data
        credit_data = self.fetch_credit_bureau_data()
        
        # Apply bank policies
        policy_results = self.apply_bank_policies(credit_data)
        
        # Calculate risk assessment
        risk_level = self.assess_credit_risk(credit_data, policy_results)
        
        # Make credit decision
        decision = self.make_credit_decision(risk_level, policy_results)
        
        if decision == CreditDecision.APPROVED:
            sanction_data = self.prepare_sanction_data()
            return {
                "agent": "UNDERWRITING",
                "decision": "Approved",
                "signals": {"decision": "Approved"},
                "data": sanction_data
            }
        elif decision == CreditDecision.CONDITIONALLY_APPROVED:
            conditions = self.generate_approval_conditions()
            sanction_data = self.prepare_conditional_sanction_data(conditions)
            return {
                "agent": "UNDERWRITING",
                "decision": "Conditionally Approved",
                "signals": {"decision": "Conditionally Approved"},
                "data": sanction_data,
                "conditions": conditions
            }
        else:
            return {
                "agent": "UNDERWRITING",
                "decision": "Rejected",
                "reason": self.get_rejection_reasons(policy_results)
            }
```

**Transition Criteria**: Credit decision is Approved or Conditionally Approved

### 3.5 Stage 5: Sanction Agent

**Purpose**: Generate and issue formal sanction letter
**Trigger**: Loan approval from Underwriting
**Duration**: Single interaction with possible clarifications

```python
class SanctionAgent:
    def run(self, user_message: str, sanction_context: dict) -> dict:
        if not sanction_context:
            return {"error": "Sanction data missing"}
        
        # Handle different user intents
        if self.is_complaint(user_message):
            return {
                "mode": "route_support",
                "message": "Routing to Customer Support for assistance"
            }
        
        if self.is_clarification_request(user_message):
            return {
                "mode": "explain_sanction",
                "message": self.explain_sanction_terms(sanction_context)
            }
        
        # Default: Issue sanction letter
        sanction_letter = self.generate_sanction_letter(sanction_context)
        return {
            "mode": "issue_sanction",
            "status": sanction_context["status"],
            "sanction_letter": sanction_letter,
            "disclaimer": "This sanction letter is system-generated based on internal credit evaluation."
        }
```

**Transition Criteria**: Process complete or route to customer support

## 4. Data Flow Architecture

### 4.1 Session State Management

```python
SESSION_STATE = {
    "stage": "LEAD",                    # Current processing stage
    "user_id": None,                    # Unique user identifier
    "lead_data": {},                    # Lead generation results
    "sales_data": {},                   # Sales interaction data
    "verification_context": {},         # Verification requirements
    "underwriting_results": {},         # Credit decision data
    "sanction_data": {},               # Sanction letter data
    "conversation_history": [],         # Full interaction log
    "created_at": timestamp,
    "last_updated": timestamp
}
```

### 4.2 Inter-Agent Data Transfer

Each agent receives context from the previous stage and enriches it:

```python
# Lead → Sales
lead_to_sales = {
    "lead_id": "uuid",
    "loan_intent": "education",
    "urgency": "immediate",
    "lead_score": 85
}

# Sales → Verification
sales_to_verification = {
    "loan_type": "education",
    "loan_amount": 1000000,
    "user_profile": {
        "name": "John Doe",
        "monthly_income": 50000,
        "employment_type": "salaried"
    },
    "documents_required": ["pan", "aadhaar", "salary_slips"]
}

# Verification → Underwriting
verification_to_underwriting = {
    "kyc_status": "verified",
    "aml_status": "cleared",
    "document_verification": {
        "pan": True,
        "aadhaar": True,
        "income_docs": True
    }
}

# Underwriting → Sanction
underwriting_to_sanction = {
    "decision": "Approved",
    "approved_amount": 800000,
    "tenure_months": 84,
    "interest_rate_range": "9.5% - 11.5%",
    "conditions": ["Property insurance required"],
    "bank": "SBI"
}
```

## 5. Technical Implementation

### 5.1 Flask Application Structure

```python
# app.py
from flask import Flask, request, jsonify
from master_agent import MasterAgent

app = Flask(__name__)
master_agent = MasterAgent()

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    session_id = data.get("session_id", None)
    
    response = master_agent.process_message(user_message, session_id)
    return jsonify(response)

@app.route("/api/status/<session_id>", methods=["GET"])
def get_status(session_id):
    status = master_agent.get_session_status(session_id)
    return jsonify(status)
```

### 5.2 Database Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,
    current_stage VARCHAR(20),
    user_data JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Leads table
CREATE TABLE leads (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36),
    loan_intent VARCHAR(20),
    lead_score INTEGER,
    status VARCHAR(20),
    created_at TIMESTAMP
);

-- Applications table
CREATE TABLE applications (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36),
    loan_type VARCHAR(20),
    amount DECIMAL(12,2),
    status VARCHAR(20),
    decision VARCHAR(30),
    created_at TIMESTAMP
);
```

### 5.3 RAG Integration

```python
class RAGEngine:
    def __init__(self):
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection("bank_policies")
    
    def query_policies(self, query: str, bank: str = None) -> List[str]:
        filters = {"bank": bank} if bank else None
        results = self.collection.query(
            query_texts=[query],
            n_results=5,
            where=filters
        )
        return results["documents"][0]
    
    def get_loan_information(self, loan_type: str, bank: str) -> dict:
        query = f"{loan_type} loan policy {bank}"
        documents = self.query_policies(query, bank)
        return self.extract_loan_details(documents)
```

## 6. Error Handling & Fallback Mechanisms

### 6.1 Agent Failure Handling

```python
def handle_agent_failure(self, stage: str, error: Exception) -> dict:
    fallback_responses = {
        "LEAD": "Welcome! I'll connect you with our loan specialist.",
        "SALES": "Let me get you the information you need about our loan products.",
        "VERIFICATION": "We need to verify some documents. Please contact our support team.",
        "UNDERWRITING": "Your application is under review. We'll update you shortly.",
        "SANCTION": "Your loan decision is ready. Please check your email."
    }
    
    # Log error for monitoring
    self.log_error(stage, error)
    
    # Route to human support for complex cases
    return {
        "agent": "FALLBACK",
        "message": fallback_responses.get(stage, "Please contact our support team."),
        "requires_human_intervention": True
    }
```

### 6.2 Session Recovery

```python
def recover_session(self, session_id: str) -> bool:
    try:
        session_data = self.database.get_session(session_id)
        if session_data:
            self.session_state = session_data
            return True
    except Exception as e:
        self.log_error("session_recovery", e)
    return False
```

## 7. Performance Optimizations

### 7.1 Caching Strategy

```python
class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis()
    
    def cache_user_profile(self, user_id: str, profile: dict):
        self.redis_client.setex(
            f"profile:{user_id}", 
            3600,  # 1 hour TTL
            json.dumps(profile)
        )
    
    def cache_loan_products(self, bank: str, products: list):
        self.redis_client.setex(
            f"products:{bank}",
            7200,  # 2 hours TTL
            json.dumps(products)
        )
```

### 7.2 Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncMasterAgent:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def process_verification_async(self, context: dict):
        loop = asyncio.get_event_loop()
        
        # Run verification checks in parallel
        pan_task = loop.run_in_executor(self.executor, self.verify_pan, context)
        aadhaar_task = loop.run_in_executor(self.executor, self.verify_aadhaar, context)
        aml_task = loop.run_in_executor(self.executor, self.run_aml_check, context)
        
        results = await asyncio.gather(pan_task, aadhaar_task, aml_task)
        return self.combine_verification_results(results)
```

## 8. Monitoring & Analytics

### 8.1 Agent Performance Metrics

```python
class MetricsCollector:
    def track_agent_performance(self, agent_name: str, duration: float, success: bool):
        metrics = {
            "agent": agent_name,
            "duration_ms": duration * 1000,
            "success": success,
            "timestamp": time.time()
        }
        self.send_to_monitoring(metrics)
    
    def track_stage_transitions(self, from_stage: str, to_stage: str, session_id: str):
        transition = {
            "from": from_stage,
            "to": to_stage,
            "session_id": session_id,
            "timestamp": time.time()
        }
        self.log_transition(transition)
```

### 8.2 Business Intelligence

```python
class BusinessIntelligence:
    def calculate_conversion_rates(self) -> dict:
        return {
            "lead_to_sales": self.get_stage_conversion("LEAD", "SALES"),
            "sales_to_verification": self.get_stage_conversion("SALES", "VERIFICATION"),
            "verification_to_underwriting": self.get_stage_conversion("VERIFICATION", "UNDERWRITING"),
            "underwriting_to_sanction": self.get_stage_conversion("UNDERWRITING", "SANCTION")
        }
    
    def get_average_processing_time(self) -> dict:
        return {
            "lead_stage": self.get_avg_duration("LEAD"),
            "sales_stage": self.get_avg_duration("SALES"),
            "verification_stage": self.get_avg_duration("VERIFICATION"),
            "underwriting_stage": self.get_avg_duration("UNDERWRITING"),
            "sanction_stage": self.get_avg_duration("SANCTION")
        }
```

## 9. Security Considerations

### 9.1 Data Protection

```python
class SecurityManager:
    def encrypt_sensitive_data(self, data: dict) -> dict:
        sensitive_fields = ["pan", "aadhaar", "account_number", "phone"]
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data:
                encrypted_data[field] = self.encrypt(encrypted_data[field])
        
        return encrypted_data
    
    def audit_log(self, action: str, user_id: str, data: dict):
        audit_entry = {
            "timestamp": time.time(),
            "action": action,
            "user_id": user_id,
            "data_hash": self.hash_data(data),
            "ip_address": self.get_client_ip()
        }
        self.store_audit_log(audit_entry)
```

### 9.2 Access Control

```python
class AccessControl:
    def validate_session(self, session_id: str, user_id: str) -> bool:
        session = self.get_session(session_id)
        return session and session.get("user_id") == user_id
    
    def check_rate_limits(self, user_id: str) -> bool:
        request_count = self.redis_client.get(f"rate_limit:{user_id}")
        return int(request_count or 0) < self.MAX_REQUESTS_PER_HOUR
```

## 10. Deployment Architecture

### 10.1 Microservices Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  master-agent:
    build: ./master-agent
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dhanit
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  lead-agent:
    build: ./agents/lead
    environment:
      - MASTER_AGENT_URL=http://master-agent:5000
  
  sales-agent:
    build: ./agents/sales
    environment:
      - RAG_ENGINE_URL=http://rag-engine:8000
  
  verification-agent:
    build: ./agents/verification
    environment:
      - KYC_API_URL=${KYC_API_URL}
      - AML_API_URL=${AML_API_URL}
  
  underwriting-agent:
    build: ./agents/underwriting
    environment:
      - CREDIT_BUREAU_API=${CREDIT_BUREAU_API}
  
  sanction-agent:
    build: ./agents/sanction
    
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=dhanit
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
  
  redis:
    image: redis:6-alpine
  
  rag-engine:
    build: ./rag-engine
    ports:
      - "8000:8000"
    volumes:
      - ./bank_docs:/app/documents
```

### 10.2 Load Balancing

```python
class LoadBalancer:
    def __init__(self):
        self.agent_instances = {
            "sales": ["sales-1:5001", "sales-2:5001", "sales-3:5001"],
            "verification": ["verify-1:5002", "verify-2:5002"],
            "underwriting": ["underwrite-1:5003", "underwrite-2:5003"]
        }
    
    def get_available_instance(self, agent_type: str) -> str:
        instances = self.agent_instances[agent_type]
        # Round-robin or health-based selection
        return self.select_healthy_instance(instances)
```

