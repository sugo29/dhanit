"""
🏦 UNDERWRITING & CREDIT OPERATIONS AGENT
==========================================
This module automates the entire bank credit backend — applying bank-specific
policies, evaluating credit risk, handling OSR (exceptions/deviations), 
interacting with customers when required, and producing sanction-ready decisions.

DEVELOPER LEARNING GUIDE:
-------------------------
This code is written with extensive comments to help you understand:
1. How real bank underwriting works
2. Why certain business rules exist
3. How to extend this for new banks/products

POSITION IN PIPELINE:
    Sales Agent → Verification Agent → [THIS AGENT] → Sanction Letter Agent

WHAT THIS AGENT DOES (Bank Manager View):
- Credit risk assessment (Is the applicant creditworthy?)
- Bank policy enforcement (Does applicant meet bank's rules?)
- Financial structuring (What loan terms are feasible?)
- OSR handling (Can we approve borderline cases with conditions?)
- Customer clarification (Ask user when info is missing)
- Final credit decision (Approved / Conditionally Approved / Rejected)

Author: Dhanit Project
Last Updated: January 2026
"""

# =============================================================================
# IMPORTS
# =============================================================================
# Standard library imports for type hints, enums, and data structures
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
import re
import json

# RAG Engine Integration - For retrieving bank policy information
# This allows the agent to query policy documents dynamically
try:
    from rag_engine import RAGRetriever, RAGConfig
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    RAGRetriever = None
    RAGConfig = None


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================
# Enums provide type-safe, readable constants that prevent typos and make
# code easier to understand. In banking, precision matters!

class CreditDecision(Enum):
    """
    Final credit decision outcomes.
    
    DEVELOPER NOTE:
    ---------------
    Banks have exactly 3 outcomes for any loan application:
    - APPROVED: Full green signal, ready for sanction
    - CONDITIONALLY_APPROVED: Approval with conditions (most common in real banking!)
    - REJECTED: Cannot proceed, provide clear reasons
    
    Real-world insight: Most bank approvals are actually "conditional" —
    they require additional documents, collateral, or guarantors.
    """
    APPROVED = "Approved"
    CONDITIONALLY_APPROVED = "Conditionally Approved"
    REJECTED = "Rejected"


class RiskLevel(Enum):
    """
    Credit risk classification.
    
    DEVELOPER NOTE:
    ---------------
    Risk levels determine:
    - Interest rate pricing (higher risk = higher rate)
    - Collateral requirements
    - Approval authority level needed
    
    LOW: Auto-approval eligible, best rates
    MEDIUM: Standard processing, normal rates
    HIGH: Requires senior approval, higher rates
    CRITICAL: Usually rejected or needs very strong conditions
    """
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class UnderwritingMode(Enum):
    """
    Operating modes for the underwriting agent.
    
    DEVELOPER NOTE:
    ---------------
    The agent operates in 3 distinct modes:
    
    INTERNAL: Silent backend processing (like a bank's credit desk)
              - No customer interaction
              - Pure policy evaluation
              - This is the DEFAULT mode
    
    CUSTOMER_CLARIFICATION: When we need info from the applicant
              - Policy requires missing input
              - Risk can be reduced by clarification
              - OSR decision needs user confirmation
    
    AGENT_SWITCH: When task belongs to another agent
              - Missing documents → Verification Agent
              - Loan concepts → Education Agent
              - Renegotiation → Sales Agent
    """
    INTERNAL = "internal"
    CUSTOMER_CLARIFICATION = "user_clarification"
    AGENT_SWITCH = "agent_switch"


class EmploymentType(Enum):
    """
    Employment classification for income assessment.
    
    DEVELOPER NOTE:
    ---------------
    Banks treat different employment types differently:
    - SALARIED: Most preferred, stable income, easier approval
    - SELF_EMPLOYED_PROFESSIONAL: Doctors, lawyers, CAs - good but more docs
    - SELF_EMPLOYED_BUSINESS: Higher risk, needs ITR and business proof
    - RETIRED: Pension income, age limits apply
    - STUDENT: For education loans, co-applicant income matters
    """
    SALARIED = "salaried"
    SELF_EMPLOYED_PROFESSIONAL = "self_employed_professional"
    SELF_EMPLOYED_BUSINESS = "self_employed_business"
    RETIRED = "retired"
    STUDENT = "student"


class CreditScoreBucket(Enum):
    """
    Credit score classification buckets.
    
    DEVELOPER NOTE:
    ---------------
    Credit bureaus (CIBIL, Experian, Equifax) provide scores from 300-900.
    Banks bucket these for decision-making:
    
    EXCELLENT (750+): Best rates, minimal scrutiny
    GOOD (700-749): Standard approval, slightly higher rates
    FAIR (650-699): Higher scrutiny, may need conditions
    POOR (below 650): Usually rejected, or very high rates
    NO_HISTORY: First-time borrowers, special handling needed
    
    Real-world insight: 750+ is the magic number for most banks!
    """
    EXCELLENT = "excellent"      # 750+
    GOOD = "good"               # 700-749
    FAIR = "fair"               # 650-699
    POOR = "poor"               # Below 650
    NO_HISTORY = "no_history"   # New to credit


class LoanType(Enum):
    """Loan product categories."""
    EDUCATION = "education"
    HOME = "home"
    PERSONAL = "personal"
    VEHICLE = "vehicle"
    BUSINESS = "business"
    GOLD = "gold"


# =============================================================================
# CREDIT SCORE THRESHOLDS BY BANK
# =============================================================================
# Each bank has different risk appetites. These thresholds reflect real
# banking behavior (as of 2026).

BANK_CREDIT_THRESHOLDS = {
    # SBI: Conservative PSU bank - strict thresholds
    "SBI": {
        "min_score": 650,           # Minimum to consider
        "preferred_score": 700,      # For best rates
        "excellent_score": 750,      # For premium treatment
        "no_history_allowed": True,  # PSU banks accept first-timers
    },
    # HDFC: Aggressive private bank - more flexible
    "HDFC": {
        "min_score": 675,
        "preferred_score": 725,
        "excellent_score": 750,
        "no_history_allowed": True,
    },
    # ICICI: Balanced approach
    "ICICI": {
        "min_score": 650,
        "preferred_score": 700,
        "excellent_score": 750,
        "no_history_allowed": True,
    },
    # Axis: Flexible, younger demographic focus
    "Axis": {
        "min_score": 650,
        "preferred_score": 700,
        "excellent_score": 750,
        "no_history_allowed": True,
    },
}


# =============================================================================
# FOIR (Fixed Obligations to Income Ratio) LIMITS BY BANK
# =============================================================================
# FOIR = (Existing EMIs + Proposed EMI) / Net Monthly Income
# Lower FOIR = Better repayment capacity

BANK_FOIR_LIMITS = {
    # SBI: Conservative - leaves more buffer for applicant
    "SBI": {
        "salaried": 0.50,           # Max 50% of income for EMIs
        "self_employed": 0.45,
        "business": 0.40,
    },
    # HDFC: More aggressive - allows higher obligations
    "HDFC": {
        "salaried": 0.55,
        "self_employed": 0.50,
        "business": 0.45,
    },
    # ICICI: Balanced
    "ICICI": {
        "salaried": 0.50,
        "self_employed": 0.45,
        "business": 0.40,
    },
    # Axis: Flexible
    "Axis": {
        "salaried": 0.55,
        "self_employed": 0.50,
        "business": 0.45,
    },
}


# =============================================================================
# DATA CLASSES
# =============================================================================
# Data classes provide structured containers for complex data.
# They auto-generate __init__, __repr__, and comparison methods.

@dataclass
class ApplicantProfile:
    """
    Complete applicant information for underwriting.
    
    DEVELOPER NOTE:
    ---------------
    This is the primary input from the Verification Agent.
    Every field here affects the credit decision.
    
    Real-world insight: In actual banking, this data comes from:
    - KYC documents (identity, address)
    - Income documents (salary slips, ITR)
    - Employment verification
    - Credit bureau pull
    """
    # Basic Information
    name: str
    age: int
    gender: str  # "M" / "F" / "Other"
    
    # Employment & Income (CRITICAL for approval)
    employment_type: EmploymentType
    employer_name: Optional[str] = None
    monthly_income: float = 0.0          # Net take-home income
    annual_income: float = 0.0           # Gross annual income
    years_of_experience: int = 0
    
    # Existing Financial Obligations
    existing_emis: float = 0.0           # Current monthly EMI burden
    credit_card_dues: float = 0.0        # Outstanding credit card balance
    other_loans: List[str] = field(default_factory=list)
    
    # Loan Request Details
    requested_loan_amount: float = 0.0
    requested_tenure_months: int = 0
    loan_type: LoanType = LoanType.PERSONAL
    loan_purpose: Optional[str] = None
    
    # Co-applicant (Optional but can save borderline cases!)
    has_co_applicant: bool = False
    co_applicant_income: float = 0.0
    co_applicant_credit_score: int = 0
    co_applicant_relationship: Optional[str] = None  # "Spouse", "Parent", etc.
    
    # Collateral Information
    has_collateral: bool = False
    collateral_type: Optional[str] = None  # "Property", "FD", "Gold", etc.
    collateral_value: float = 0.0
    
    # Additional Context
    is_existing_customer: bool = False   # Existing bank relationship?
    financial_literacy: str = "medium"   # "low", "medium", "high"


@dataclass
class CreditBureauResult:
    """
    Credit bureau (CIBIL/Experian/Equifax) pull result.
    
    DEVELOPER NOTE:
    ---------------
    This is one of the MOST IMPORTANT inputs for underwriting.
    Credit score alone can make or break an application.
    
    Real-world insight:
    - Banks pull credit reports multiple times during processing
    - Each pull is recorded and too many pulls can hurt the score!
    - Score is just one factor; payment history matters too
    """
    credit_score: int                    # 300-900 range
    score_bucket: CreditScoreBucket
    
    # Credit History Details
    total_accounts: int = 0              # All loan/credit accounts
    active_accounts: int = 0             # Currently active ones
    overdue_accounts: int = 0            # Accounts with missed payments
    
    # Payment Behavior (CRITICAL!)
    days_past_due_30: int = 0            # Times 30+ days late
    days_past_due_60: int = 0            # Times 60+ days late
    days_past_due_90: int = 0            # Times 90+ days late (very bad!)
    
    # Credit Utilization
    total_credit_limit: float = 0.0
    current_balance: float = 0.0
    utilization_ratio: float = 0.0       # balance/limit, lower is better
    
    # Special Flags
    has_write_offs: bool = False         # Past loan defaults (deal breaker!)
    has_settlements: bool = False        # Settled loans for less (red flag)
    
    # Inquiry History
    recent_inquiries: int = 0            # Credit pulls in last 6 months


@dataclass
class VerificationResult:
    """
    Output from the Verification Agent.
    
    DEVELOPER NOTE:
    ---------------
    The Verification Agent checks:
    - KYC: Identity and address verification
    - AML: Anti-money laundering checks
    - Document authenticity
    
    We assume verification is COMPLETE before underwriting.
    """
    kyc_verified: bool = False
    aml_cleared: bool = False
    documents_verified: bool = False
    
    # Specific Document Status
    identity_docs_ok: bool = False
    address_docs_ok: bool = False
    income_docs_ok: bool = False
    employment_verified: bool = False
    
    # Any flags or concerns
    verification_flags: List[str] = field(default_factory=list)


@dataclass
class PolicyFinding:
    """
    Individual policy check result.
    
    DEVELOPER NOTE:
    ---------------
    Each bank policy rule generates a PolicyFinding.
    These are collected to form the complete policy assessment.
    
    Example finding:
    - rule: "minimum_credit_score"
    - passed: False
    - actual_value: 620
    - required_value: 650
    - message: "Credit score 620 is below SBI minimum of 650"
    """
    rule_name: str
    passed: bool
    actual_value: Any = None
    required_value: Any = None
    message: str = ""
    is_waivable: bool = False            # Can this be overridden in OSR?
    severity: str = "medium"              # "low", "medium", "high", "critical"


@dataclass
class DeviationRequest:
    """
    OSR (On Sanction Risk) deviation request.
    
    DEVELOPER NOTE:
    ---------------
    OSR is how real banks handle borderline cases.
    Instead of rejecting, they identify:
    - What rule is being deviated
    - Why deviation should be allowed
    - What conditions make it acceptable
    
    Real-world insight: Most loan approvals involve some deviation!
    A good underwriter knows when to deviate and when to hold firm.
    """
    deviation_type: str                   # "income", "credit_score", "age", etc.
    policy_requirement: str
    actual_situation: str
    deviation_percentage: float           # How much is the deviation?
    
    # Justification
    compensating_factors: List[str] = field(default_factory=list)
    risk_mitigants: List[str] = field(default_factory=list)
    
    # Recommendation
    is_approvable: bool = False
    conditions_required: List[str] = field(default_factory=list)
    approval_level_required: str = "standard"  # "standard", "senior", "credit_head"


@dataclass 
class SanctionData:
    """
    Sanction-ready data for the Sanction Letter Agent.
    
    DEVELOPER NOTE:
    ---------------
    This is the OUTPUT when loan is approved/conditionally approved.
    Contains everything needed to generate the sanction letter.
    
    IMPORTANT: No exact interest rates here (provisional only).
    Final rates are set at disbursement.
    """
    approved_amount: float
    tenure_months: int
    interest_type: str = "Floating"       # "Fixed" or "Floating"
    tentative_rate_range: str = ""        # e.g., "8.65% - 9.25%"
    
    # Repayment Details
    estimated_emi: float = 0.0
    moratorium_months: int = 0
    moratorium_applicable: bool = False
    
    # Processing
    processing_fee_percentage: float = 0.0
    
    # Validity
    sanction_validity_days: int = 90      # Standard 90 days
    
    # Conditions & Notes
    special_conditions: List[str] = field(default_factory=list)
    remarks: str = ""


# =============================================================================
# COMPREHENSIVE BANK POLICIES
# =============================================================================
# These policies are treated as DATA, not hardcoded rules.
# This allows: 
# 1. Easy addition of new banks without code changes
# 2. Policy updates without deployment
# 3. Clear audit trail of what rules are applied
#
# STRUCTURE EXPLAINED:
# - Each bank has policies for each loan type
# - Each policy includes: eligibility, limits, rates, collateral, special rules

BANK_POLICIES = {
    # =========================================================================
    # SBI (State Bank of India) - CONSERVATIVE PSU BANK
    # =========================================================================
    # SBI is India's largest bank with a conservative approach.
    # Characteristics: Lower interest rates, stricter eligibility, slower processing
    "SBI": {
        "bank_type": "PSU",  # Public Sector Undertaking
        "risk_appetite": "conservative",
        "processing_speed": "standard",
        
        # --- EDUCATION LOAN POLICY ---
        "education": {
            "product_name": "SBI Scholar Loan",
            "min_credit_score": 650,
            "min_co_applicant_score": 600,
            
            # Income Requirements
            "min_co_applicant_income": 25000,  # Monthly
            "max_foir": 0.50,
            
            # Loan Limits
            "max_amount_india": 5000000,      # 50 lakh
            "max_amount_abroad": 15000000,     # 1.5 crore
            "min_amount": 100000,              # 1 lakh
            
            # Collateral Rules
            "collateral_threshold": 750000,    # 7.5 lakh (no collateral below this)
            "ltv_ratio": 0.85,                 # 85% of collateral value
            
            # Tenure & Moratorium
            "max_tenure_years": 15,
            "moratorium_months": 12,           # Course + 12 months
            "moratorium_type": "course_plus",
            
            # Interest Rates (indicative ranges)
            "interest_type": "Floating",
            "interest_linked_to": "RLLR",
            "rate_range_india": {"min": 8.65, "max": 10.05},
            "rate_range_abroad": {"min": 8.85, "max": 10.25},
            
            # Concessions
            "girl_student_concession": 0.50,
            "existing_customer_concession": 0.50,
            
            # Processing
            "processing_fee_below_20L": 0.0,
            "processing_fee_above_20L": 0.50,
            "max_processing_fee": 10000,
            
            # Age Limits
            "min_age": 18,
            "max_age_at_maturity": 70,
            
            # Special Rules
            "allow_no_credit_history": True,
            "require_co_applicant": True,
            "part_time_income_allowed": True,
        },
        
        # --- HOME LOAN POLICY ---
        "home": {
            "product_name": "SBI Home Loan",
            "min_credit_score": 650,
            
            # Income Requirements
            "min_income_salaried": 25000,
            "min_income_self_employed": 300000,  # Annual
            "max_foir": 0.50,
            
            # Loan Limits
            "max_ltv_upto_30L": 0.90,
            "max_ltv_30L_to_75L": 0.80,
            "max_ltv_above_75L": 0.75,
            "min_amount": 500000,
            
            # Tenure
            "max_tenure_years": 30,
            "max_age_at_maturity": 70,
            
            # Interest
            "interest_type": "Floating",
            "interest_linked_to": "Repo Rate (EBR)",
            "rate_range": {"min": 8.40, "max": 9.65},
            "women_concession": 0.05,
            
            # Processing
            "processing_fee_percentage": 0.35,
            "min_processing_fee": 2000,
            "max_processing_fee": 10000,
            
            # Age
            "min_age": 21,
            "max_age_at_maturity": 70,
        },
        
        # --- PERSONAL LOAN POLICY ---
        "personal": {
            "product_name": "SBI Xpress Credit",
            "min_credit_score": 700,
            
            # Income
            "min_income_salaried": 15000,
            "max_foir": 0.50,
            
            # Limits
            "min_amount": 25000,
            "max_amount": 2500000,
            "max_multiplier_of_income": 20,  # Max 20x monthly income
            
            # Tenure
            "min_tenure_months": 6,
            "max_tenure_months": 72,
            
            # Interest
            "interest_type": "Fixed",
            "rate_range": {"min": 11.10, "max": 14.30},
            
            # Processing
            "processing_fee_percentage": 1.5,
            
            # Age
            "min_age": 21,
            "max_age": 58,
        },
        
        # --- VEHICLE LOAN POLICY ---
        "vehicle": {
            "product_name": "SBI Car Loan",
            "min_credit_score": 675,
            
            # Income
            "min_income": 20000,
            "max_foir": 0.50,
            
            # Limits
            "max_ltv_new": 0.90,
            "max_ltv_used": 0.85,
            
            # Tenure
            "max_tenure_new": 84,    # 7 years
            "max_tenure_used": 60,   # 5 years
            
            # Interest
            "rate_range_new": {"min": 8.65, "max": 9.30},
            "rate_range_used": {"min": 9.80, "max": 11.50},
            "ev_concession": 0.20,
            
            # Processing
            "processing_fee_percentage": 0.40,
            "max_processing_fee": 10000,
        },
        
        # --- BUSINESS LOAN POLICY ---
        "business": {
            "product_name": "SBI MSME Loan",
            "min_credit_score": 675,
            
            # Business Requirements
            "min_business_vintage_years": 2,
            "require_gst_registration": True,
            "min_annual_turnover": 1000000,  # 10 lakh
            
            # Income/Capacity
            "max_foir": 0.40,
            
            # Limits
            "max_unsecured_under_cgtmse": 50000000,  # 5 crore
            
            # Tenure
            "max_tenure_term_loan": 84,      # 7 years
            
            # Interest
            "interest_type": "Floating",
            "interest_linked_to": "RLLR",
            "rate_range": {"min": 8.75, "max": 11.50},
        },
    },
    
    # =========================================================================
    # HDFC BANK - AGGRESSIVE PRIVATE BANK
    # =========================================================================
    # HDFC is known for faster processing and flexible terms.
    # Characteristics: Slightly higher rates, faster approval, relationship-based
    "HDFC": {
        "bank_type": "Private",
        "risk_appetite": "aggressive",
        "processing_speed": "fast",
        
        # --- EDUCATION LOAN POLICY ---
        "education": {
            "product_name": "HDFC Credila Education Loan",
            "min_credit_score": 675,
            "min_co_applicant_score": 650,
            
            "min_co_applicant_income": 30000,
            "max_foir": 0.55,
            
            "max_amount_without_collateral": 4000000,
            "max_amount_with_collateral": 10000000,
            "min_amount": 100000,
            
            "collateral_threshold": 1000000,
            "ltv_ratio": 0.80,
            
            "max_tenure_years": 12,
            "moratorium_months": 6,
            "moratorium_type": "course_plus",
            
            "interest_type": "Fixed/Semi-Fixed",
            "rate_range": {"min": 9.50, "max": 13.50},
            
            "processing_fee_percentage": 1.5,
            
            "min_age": 18,
            "max_age_at_maturity": 65,
            
            "allow_no_credit_history": True,
            "require_co_applicant": True,
            "forex_disbursement": True,
        },
        
        # --- HOME LOAN POLICY ---
        "home": {
            "product_name": "HDFC Home Loan",
            "min_credit_score": 675,
            
            "min_income_salaried": 25000,
            "min_income_self_employed": 400000,
            "max_foir": 0.55,
            
            "max_ltv": 0.90,
            "no_upper_limit": True,
            
            "max_tenure_salaried": 30,
            "max_tenure_self_employed": 25,
            "max_age_at_maturity": 65,
            
            "interest_type": "Floating",
            "interest_linked_to": "HDFC RPLR",
            "rate_range_salaried": {"min": 8.35, "max": 9.50},
            "rate_range_self_employed": {"min": 8.45, "max": 9.75},
            
            "processing_fee_percentage": 0.50,
            
            "min_age": 21,
            "balance_transfer_available": True,
            "overdraft_available": True,
        },
        
        # --- PERSONAL LOAN POLICY ---
        "personal": {
            "product_name": "HDFC Personal Loan",
            "min_credit_score": 700,
            
            "min_income_salaried": 20000,
            "max_foir": 0.55,
            
            "min_amount": 50000,
            "max_amount": 4000000,
            "max_multiplier_of_income": 24,
            
            "min_tenure_months": 12,
            "max_tenure_months": 60,
            
            "interest_type": "Fixed",
            "rate_range": {"min": 10.50, "max": 21.00},
            
            "processing_fee_percentage": 2.0,
            
            "min_age": 21,
            "max_age": 60,
            
            "instant_approval_existing": True,
        },
        
        # --- VEHICLE LOAN POLICY ---
        "vehicle": {
            "product_name": "HDFC Car Loan",
            "min_credit_score": 700,
            
            "min_income": 25000,
            "max_foir": 0.55,
            
            "max_ltv_new": 0.95,
            "max_ltv_used": 0.80,
            
            "max_tenure_new": 84,
            "max_tenure_used": 60,
            
            "rate_range_new": {"min": 8.75, "max": 9.50},
            "rate_range_used": {"min": 10.00, "max": 12.00},
            
            "processing_fee_percentage": 0.50,
        },
        
        # --- BUSINESS LOAN POLICY ---
        "business": {
            "product_name": "HDFC Business Loan",
            "min_credit_score": 700,
            
            "min_business_vintage_years": 3,
            "require_gst_registration": True,
            "min_annual_turnover": 2000000,
            
            "max_foir": 0.45,
            
            "max_unsecured": 7500000,
            
            "max_tenure_term_loan": 60,
            
            "interest_type": "Fixed/Floating",
            "rate_range": {"min": 11.00, "max": 16.00},
            
            "processing_fee_percentage": 2.0,
        },
    },
    
    # =========================================================================
    # ICICI BANK - BALANCED PRIVATE BANK
    # =========================================================================
    # ICICI offers a balanced approach between PSU strictness and private flexibility
    "ICICI": {
        "bank_type": "Private",
        "risk_appetite": "balanced",
        "processing_speed": "fast",
        
        # --- EDUCATION LOAN POLICY ---
        "education": {
            "product_name": "ICICI Bank Education Loan",
            "min_credit_score": 650,
            "min_co_applicant_score": 625,
            
            "min_co_applicant_income": 25000,
            "max_foir": 0.50,
            
            "max_amount_india": 5000000,
            "max_amount_abroad": 10000000,
            "min_amount": 100000,
            
            "collateral_threshold": 1000000,
            "ltv_ratio": 0.80,
            
            "max_tenure_years": 12,
            "moratorium_months": 12,
            "moratorium_type": "course_plus",
            
            "interest_type": "Floating",
            "interest_linked_to": "I-MCLR",
            "rate_range_india": {"min": 9.25, "max": 11.75},
            "rate_range_abroad": {"min": 9.50, "max": 12.00},
            
            "women_concession": 0.50,
            
            "processing_fee_percentage": 0.75,
            
            "min_age": 18,
            "max_age_at_maturity": 65,
            
            "allow_no_credit_history": True,
            "require_co_applicant": True,
        },
        
        # --- HOME LOAN POLICY ---
        "home": {
            "product_name": "ICICI Home Loan",
            "min_credit_score": 675,
            
            "min_income_salaried": 25000,
            "min_income_self_employed": 350000,
            "max_foir": 0.50,
            
            "max_ltv_upto_30L": 0.90,
            "max_ltv_30L_to_75L": 0.80,
            "max_ltv_above_75L": 0.75,
            
            "max_tenure_years": 30,
            "max_age_at_maturity": 65,
            
            "interest_type": "Floating",
            "interest_linked_to": "I-MCLR",
            "rate_range": {"min": 8.40, "max": 9.50},
            "women_concession": 0.05,
            
            "processing_fee_percentage": 0.50,
            
            "min_age": 23,
        },
        
        # --- PERSONAL LOAN POLICY ---
        "personal": {
            "product_name": "ICICI Personal Loan",
            "min_credit_score": 725,
            
            "min_income_salaried": 17500,
            "max_foir": 0.50,
            
            "min_amount": 50000,
            "max_amount": 5000000,
            "max_multiplier_of_income": 22,
            
            "min_tenure_months": 12,
            "max_tenure_months": 72,
            
            "interest_type": "Fixed",
            "rate_range": {"min": 10.65, "max": 16.00},
            
            "processing_fee_percentage": 1.75,
            
            "min_age": 23,
            "max_age": 58,
        },
        
        # --- VEHICLE LOAN POLICY ---
        "vehicle": {
            "product_name": "ICICI Car Loan",
            "min_credit_score": 700,
            
            "min_income": 20000,
            "max_foir": 0.50,
            
            "max_ltv_new": 0.90,
            "max_ltv_used": 0.80,
            
            "max_tenure_new": 84,
            "max_tenure_used": 60,
            
            "rate_range_new": {"min": 8.50, "max": 9.25},
            "rate_range_used": {"min": 9.75, "max": 11.25},
            
            "processing_fee_percentage": 0.50,
        },
        
        # --- BUSINESS LOAN POLICY ---
        "business": {
            "product_name": "ICICI Business Loan",
            "min_credit_score": 700,
            
            "min_business_vintage_years": 3,
            "require_gst_registration": True,
            "min_annual_turnover": 1500000,
            
            "max_foir": 0.40,
            
            "max_unsecured": 5000000,
            
            "max_tenure_term_loan": 60,
            
            "interest_type": "Floating",
            "rate_range": {"min": 10.50, "max": 15.00},
            
            "processing_fee_percentage": 1.5,
        },
    },
    
    # =========================================================================
    # AXIS BANK - FLEXIBLE PRIVATE BANK
    # =========================================================================
    # Axis focuses on younger demographics with flexible products
    "Axis": {
        "bank_type": "Private",
        "risk_appetite": "flexible",
        "processing_speed": "fast",
        
        # --- EDUCATION LOAN POLICY ---
        "education": {
            "product_name": "Axis Bank Education Loan",
            "min_credit_score": 650,
            "min_co_applicant_score": 625,
            
            "min_co_applicant_income": 25000,
            "max_foir": 0.55,
            
            "max_amount_abroad": 7500000,
            "min_amount": 100000,
            
            "collateral_threshold": 750000,
            "ltv_ratio": 0.80,
            
            "max_tenure_years": 15,
            "moratorium_months": 6,
            "moratorium_type": "course_plus",
            
            "interest_type": "Floating",
            "interest_linked_to": "Axis Base Rate",
            "rate_range": {"min": 9.00, "max": 12.50},
            
            "premier_institution_concession": 0.25,
            
            "processing_fee_percentage": 1.0,
            
            "min_age": 18,
            "max_age_at_maturity": 60,
            
            "allow_no_credit_history": True,
            "require_co_applicant": True,
            "pre_approved_colleges": True,
            "same_day_approval": True,
        },
        
        # --- HOME LOAN POLICY ---
        "home": {
            "product_name": "Axis Home Loan",
            "min_credit_score": 675,
            
            "min_income_salaried": 25000,
            "min_income_self_employed": 350000,
            "max_foir": 0.55,
            
            "max_ltv": 0.85,
            
            "max_tenure_years": 30,
            "max_age_at_maturity": 70,
            
            "interest_type": "Floating",
            "rate_range": {"min": 8.50, "max": 9.50},
            "women_concession": 0.05,
            
            "processing_fee_percentage": 0.50,
            
            "min_age": 21,
            
            "balance_transfer_available": True,
        },
        
        # --- PERSONAL LOAN POLICY ---
        "personal": {
            "product_name": "Axis Personal Loan",
            "min_credit_score": 700,
            
            "min_income_salaried": 15000,
            "max_foir": 0.55,
            
            "min_amount": 50000,
            "max_amount": 4000000,
            "max_multiplier_of_income": 25,
            
            "min_tenure_months": 12,
            "max_tenure_months": 60,
            
            "interest_type": "Fixed",
            "rate_range": {"min": 10.49, "max": 18.00},
            
            "processing_fee_percentage": 2.0,
            
            "min_age": 21,
            "max_age": 60,
        },
        
        # --- VEHICLE LOAN POLICY ---
        "vehicle": {
            "product_name": "Axis Car Loan",
            "min_credit_score": 675,
            
            "min_income": 20000,
            "max_foir": 0.55,
            
            "max_ltv_new": 0.95,
            "max_ltv_used": 0.80,
            
            "max_tenure_new": 84,
            "max_tenure_used": 48,
            
            "rate_range_new": {"min": 8.50, "max": 9.50},
            "rate_range_used": {"min": 10.00, "max": 12.50},
            
            "processing_fee_percentage": 0.50,
        },
        
        # --- BUSINESS LOAN POLICY ---
        "business": {
            "product_name": "Axis Business Loan",
            "min_credit_score": 700,
            
            "min_business_vintage_years": 2,
            "require_gst_registration": True,
            "min_annual_turnover": 1000000,
            
            "max_foir": 0.45,
            
            "max_unsecured": 5000000,
            
            "max_tenure_term_loan": 60,
            
            "interest_type": "Floating",
            "rate_range": {"min": 10.00, "max": 15.50},
            
            "processing_fee_percentage": 1.5,
        },
    },
}


# =============================================================================
# MAIN UNDERWRITING AGENT CLASS
# =============================================================================

class UnderwritingAgent:
    """
    🏦 Underwriting & Credit Operations Agent
    
    This agent automates the entire bank credit backend — applying bank-specific
    policies, evaluating credit risk, handling exceptions (OSR), interacting with
    customers when required, and producing sanction-ready decisions.
    
    DEVELOPER LEARNING GUIDE:
    -------------------------
    This class represents how a real bank credit team works:
    
    1. CREDIT DESK: Receives application from sales
    2. POLICY CHECK: Verifies against bank rules
    3. RISK ASSESSMENT: Evaluates creditworthiness
    4. AFFORDABILITY: Can they repay?
    5. OSR (if needed): Handle borderline cases
    6. DECISION: Approve/Reject/Conditional
    7. SANCTION PREP: Send to sanction letter team
    
    OPERATING MODES:
    ---------------
    - INTERNAL: Silent processing (default)
    - CUSTOMER_CLARIFICATION: When we need info
    - AGENT_SWITCH: When task belongs elsewhere
    
    Usage:
    ------
    >>> agent = UnderwritingAgent()
    >>> result = agent.process_application(
    ...     bank="SBI",
    ...     applicant=applicant_profile,
    ...     credit_bureau=credit_result,
    ...     verification=verification_result
    ... )
    >>> print(result)  # JSON output
    """
    
    def __init__(self, enable_rag: bool = True, rag_config: Optional[Any] = None):
        """
        Initialize the Underwriting Agent.
        
        DEVELOPER NOTE:
        ---------------
        The agent can work with or without RAG:
        - WITH RAG: Queries policy documents for latest info
        - WITHOUT RAG: Uses hardcoded policy data (BANK_POLICIES)
        
        Args:
            enable_rag: Whether to enable RAG for dynamic policy retrieval
            rag_config: Optional configuration for RAG system
        """
        # Current operating mode
        self.current_mode = UnderwritingMode.INTERNAL
        
        # Track policy findings during processing
        self.policy_findings: List[PolicyFinding] = []
        
        # Track any deviations identified
        self.deviations: List[DeviationRequest] = []
        
        # Messages for customer (when in clarification mode)
        self.customer_messages: List[str] = []
        
        # RAG Integration for dynamic policy retrieval
        self.rag_enabled = enable_rag and RAG_AVAILABLE
        self.rag_retriever: Optional[Any] = None
        
        if self.rag_enabled:
            try:
                config = rag_config or (RAGConfig() if RAGConfig else None)
                self.rag_retriever = RAGRetriever(config) if RAGRetriever else None
                print("✅ RAG enabled for UnderwritingAgent")
            except Exception as e:
                print(f"⚠️ RAG initialization failed: {e}. Using static policies.")
                self.rag_enabled = False
        else:
            print("ℹ️ Using static bank policies (RAG disabled)")
    
    # =========================================================================
    # MAIN ENTRY POINT
    # =========================================================================
    
    def process_application(
        self,
        bank: str,
        applicant: ApplicantProfile,
        credit_bureau: CreditBureauResult,
        verification: VerificationResult
    ) -> Dict[str, Any]:
        """
        Main entry point for processing a loan application.
        
        DEVELOPER NOTE:
        ---------------
        This is the PRIMARY function called by the Master Agent.
        It orchestrates all underwriting steps and returns a structured decision.
        
        Flow:
        1. Validate inputs
        2. Load bank-specific policy
        3. Evaluate credit risk
        4. Check policy compliance
        5. Calculate affordability
        6. Handle OSR if needed
        7. Generate final decision
        
        Args:
            bank: Bank name (e.g., "SBI", "HDFC")
            applicant: Complete applicant profile
            credit_bureau: Credit bureau pull results
            verification: Verification agent results
            
        Returns:
            Dictionary with underwriting decision (JSON-serializable)
        """
        # Reset state for new application
        self._reset_state()
        
        # Step 1: Validate we can process this
        if not self._validate_inputs(bank, applicant, verification):
            return self._generate_output(
                bank=bank,
                decision=CreditDecision.REJECTED,
                risk_level=RiskLevel.CRITICAL,
                reason="Input validation failed"
            )
        
        # Step 2: Load bank policy
        loan_type_str = applicant.loan_type.value
        policy = self._get_bank_policy(bank, loan_type_str)
        
        if not policy:
            return self._generate_output(
                bank=bank,
                decision=CreditDecision.REJECTED,
                risk_level=RiskLevel.CRITICAL,
                reason=f"No policy found for {bank} - {loan_type_str} loan"
            )
        
        # Step 3: Evaluate credit risk
        risk_level = self._evaluate_credit_risk(credit_bureau, policy)
        
        # Step 4: Check policy compliance
        policy_passed = self._check_policy_compliance(
            applicant, credit_bureau, policy, bank
        )
        
        # Step 5: Calculate affordability
        is_affordable, proposed_emi = self._calculate_affordability(
            applicant, policy
        )
        
        # Step 6: Handle OSR for borderline cases
        if not policy_passed or not is_affordable:
            # Check if we can approve with conditions
            osr_result = self._handle_osr(
                applicant, credit_bureau, policy, risk_level
            )
            
            if osr_result["approvable"]:
                # Conditional approval
                return self._generate_output(
                    bank=bank,
                    decision=CreditDecision.CONDITIONALLY_APPROVED,
                    risk_level=risk_level,
                    conditions=osr_result["conditions"],
                    sanction_data=self._prepare_sanction_data(
                        applicant, policy, proposed_emi, osr_result.get("adjusted_amount")
                    )
                )
            else:
                # Cannot approve even with OSR
                return self._generate_output(
                    bank=bank,
                    decision=CreditDecision.REJECTED,
                    risk_level=risk_level,
                    reason=osr_result.get("rejection_reason", "Does not meet policy requirements")
                )
        
        # Step 7: Full approval - all checks passed!
        return self._generate_output(
            bank=bank,
            decision=CreditDecision.APPROVED,
            risk_level=risk_level,
            sanction_data=self._prepare_sanction_data(applicant, policy, proposed_emi)
        )
    
    # =========================================================================
    # CREDIT RISK EVALUATION
    # =========================================================================
    
    def _evaluate_credit_risk(
        self,
        credit_bureau: CreditBureauResult,
        policy: Dict[str, Any]
    ) -> RiskLevel:
        """
        Evaluate the credit risk level of an applicant.
        
        DEVELOPER NOTE:
        ---------------
        Risk assessment considers multiple factors, not just credit score:
        
        1. Credit Score - Primary factor
        2. Payment History - DPD (Days Past Due) patterns
        3. Credit Utilization - How much credit is being used
        4. Write-offs/Settlements - Past defaults (very bad!)
        5. Recent Inquiries - Too many = desperate for credit
        
        The final risk level affects:
        - Interest rate offered
        - Collateral requirements
        - Approval authority needed
        
        Returns:
            RiskLevel enum value
        """
        score = credit_bureau.credit_score
        risk_score = 0  # Lower is better
        
        # Factor 1: Credit Score (50% weight)
        # This is the most important single factor
        min_required = policy.get("min_credit_score", 650)
        
        if score >= 750:
            risk_score += 0
        elif score >= 700:
            risk_score += 15
        elif score >= min_required:
            risk_score += 30
        elif score >= min_required - 50:
            risk_score += 50  # Borderline
        else:
            risk_score += 80  # Below minimum
        
        # Factor 2: Payment History (20% weight)
        # DPD (Days Past Due) is a strong indicator of future behavior
        if credit_bureau.days_past_due_90 > 0:
            risk_score += 40  # Major red flag
        elif credit_bureau.days_past_due_60 > 0:
            risk_score += 25
        elif credit_bureau.days_past_due_30 > 2:
            risk_score += 15
        
        # Factor 3: Write-offs and Settlements (15% weight)
        # These are near deal-breakers
        if credit_bureau.has_write_offs:
            risk_score += 50  # Very serious
        if credit_bureau.has_settlements:
            risk_score += 30  # Serious
        
        # Factor 4: Credit Utilization (10% weight)
        # High utilization = higher risk
        if credit_bureau.utilization_ratio > 0.80:
            risk_score += 15
        elif credit_bureau.utilization_ratio > 0.60:
            risk_score += 8
        
        # Factor 5: Recent Inquiries (5% weight)
        # Too many inquiries = credit shopping
        if credit_bureau.recent_inquiries > 5:
            risk_score += 10
        elif credit_bureau.recent_inquiries > 3:
            risk_score += 5
        
        # Convert risk score to risk level
        # DEVELOPER NOTE: These thresholds are calibrated from real banking data
        if risk_score <= 20:
            return RiskLevel.LOW
        elif risk_score <= 45:
            return RiskLevel.MEDIUM
        elif risk_score <= 70:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    # =========================================================================
    # POLICY COMPLIANCE CHECK
    # =========================================================================
    
    def _check_policy_compliance(
        self,
        applicant: ApplicantProfile,
        credit_bureau: CreditBureauResult,
        policy: Dict[str, Any],
        bank: str
    ) -> bool:
        """
        Check if applicant meets all bank policy requirements.
        
        DEVELOPER NOTE:
        ---------------
        This is the core policy enforcement function. It checks:
        
        1. Age limits (min and max at maturity)
        2. Credit score requirements
        3. Income requirements
        4. Loan amount limits
        5. Collateral requirements (if applicable)
        
        Each check generates a PolicyFinding that is stored for reporting.
        Failed checks don't immediately reject - they go to OSR first.
        
        Returns:
            True if ALL policy checks pass, False otherwise
        """
        all_passed = True
        
        # Check 1: Age Requirements
        min_age = policy.get("min_age", 21)
        max_age = policy.get("max_age", 65)
        max_age_at_maturity = policy.get("max_age_at_maturity", 70)
        
        tenure_years = applicant.requested_tenure_months / 12
        age_at_maturity = applicant.age + tenure_years
        
        if applicant.age < min_age:
            self._add_finding(
                rule="minimum_age",
                passed=False,
                actual=applicant.age,
                required=min_age,
                message=f"Applicant age {applicant.age} is below minimum {min_age}",
                severity="high"
            )
            all_passed = False
        
        if applicant.age > max_age:
            self._add_finding(
                rule="maximum_age",
                passed=False,
                actual=applicant.age,
                required=max_age,
                message=f"Applicant age {applicant.age} exceeds maximum {max_age}",
                severity="high",
                waivable=False
            )
            all_passed = False
        
        if age_at_maturity > max_age_at_maturity:
            self._add_finding(
                rule="age_at_maturity",
                passed=False,
                actual=age_at_maturity,
                required=max_age_at_maturity,
                message=f"Age at loan maturity ({age_at_maturity:.0f}) exceeds limit ({max_age_at_maturity})",
                severity="medium",
                waivable=True
            )
            all_passed = False
        
        # Check 2: Credit Score
        min_score = policy.get("min_credit_score", 650)
        
        # Special handling for no credit history
        if credit_bureau.score_bucket == CreditScoreBucket.NO_HISTORY:
            if policy.get("allow_no_credit_history", False):
                self._add_finding(
                    rule="credit_score",
                    passed=True,
                    actual="No history",
                    required=min_score,
                    message="No credit history - accepted per policy"
                )
            else:
                self._add_finding(
                    rule="credit_score",
                    passed=False,
                    actual="No history",
                    required=min_score,
                    message=f"{bank} requires credit history for this product",
                    severity="high"
                )
                all_passed = False
        elif credit_bureau.credit_score < min_score:
            self._add_finding(
                rule="credit_score",
                passed=False,
                actual=credit_bureau.credit_score,
                required=min_score,
                message=f"Credit score {credit_bureau.credit_score} below {bank} minimum of {min_score}",
                severity="high",
                waivable=True  # Can be waived with strong co-applicant
            )
            all_passed = False
        else:
            self._add_finding(
                rule="credit_score",
                passed=True,
                actual=credit_bureau.credit_score,
                required=min_score,
                message=f"Credit score {credit_bureau.credit_score} meets requirement"
            )
        
        # Check 3: Income Requirements
        income_passed = self._check_income_requirements(applicant, policy)
        if not income_passed:
            all_passed = False
        
        # Check 4: Loan Amount Limits
        amount_passed = self._check_loan_amount(applicant, policy)
        if not amount_passed:
            all_passed = False
        
        # Check 5: Collateral Requirements
        collateral_passed = self._check_collateral_requirements(applicant, policy)
        if not collateral_passed:
            all_passed = False
        
        return all_passed
    
    def _check_income_requirements(
        self,
        applicant: ApplicantProfile,
        policy: Dict[str, Any]
    ) -> bool:
        """
        Check if applicant meets income requirements.
        
        DEVELOPER NOTE:
        ---------------
        Income requirements vary by:
        - Employment type (salaried vs self-employed)
        - Loan type (education loans check co-applicant income)
        - Bank (private banks often more flexible)
        """
        employment = applicant.employment_type
        
        # For education loans, check co-applicant income
        if applicant.loan_type == LoanType.EDUCATION:
            min_income = policy.get("min_co_applicant_income", 25000)
            actual_income = applicant.co_applicant_income if applicant.has_co_applicant else 0
            
            if actual_income < min_income:
                self._add_finding(
                    rule="co_applicant_income",
                    passed=False,
                    actual=actual_income,
                    required=min_income,
                    message=f"Co-applicant income ₹{actual_income:,.0f} below minimum ₹{min_income:,.0f}",
                    severity="medium",
                    waivable=True
                )
                return False
            return True
        
        # For other loans, check applicant income
        if employment == EmploymentType.SALARIED:
            min_income = policy.get("min_income_salaried", policy.get("min_income", 15000))
        else:
            min_income = policy.get("min_income_self_employed", policy.get("min_income", 25000))
        
        if applicant.monthly_income < min_income:
            self._add_finding(
                rule="minimum_income",
                passed=False,
                actual=applicant.monthly_income,
                required=min_income,
                message=f"Monthly income ₹{applicant.monthly_income:,.0f} below minimum ₹{min_income:,.0f}",
                severity="high",
                waivable=True
            )
            return False
        
        self._add_finding(
            rule="minimum_income",
            passed=True,
            actual=applicant.monthly_income,
            required=min_income,
            message="Income requirement met"
        )
        return True
    
    def _check_loan_amount(
        self,
        applicant: ApplicantProfile,
        policy: Dict[str, Any]
    ) -> bool:
        """
        Check if requested loan amount is within limits.
        
        DEVELOPER NOTE:
        ---------------
        Loan amount limits depend on:
        - Loan type (education has different limits for India vs abroad)
        - Collateral availability
        - Income multiplier limits
        """
        amount = applicant.requested_loan_amount
        
        # Check minimum
        min_amount = policy.get("min_amount", 50000)
        if amount < min_amount:
            self._add_finding(
                rule="minimum_loan_amount",
                passed=False,
                actual=amount,
                required=min_amount,
                message=f"Requested ₹{amount:,.0f} is below minimum ₹{min_amount:,.0f}",
                severity="low"
            )
            return False
        
        # Check maximum based on loan type
        if applicant.loan_type == LoanType.EDUCATION:
            # Education loans have different limits for India vs abroad
            max_amount = policy.get("max_amount_abroad", policy.get("max_amount_india", 5000000))
            if applicant.has_collateral:
                max_amount = policy.get("max_amount_with_collateral", max_amount)
            else:
                max_amount = min(max_amount, policy.get("max_amount_without_collateral", max_amount))
        else:
            max_amount = policy.get("max_amount", 10000000)
            
            # Also check income multiplier if applicable
            multiplier = policy.get("max_multiplier_of_income")
            if multiplier and applicant.monthly_income > 0:
                income_based_max = applicant.monthly_income * multiplier
                max_amount = min(max_amount, income_based_max)
        
        if amount > max_amount:
            self._add_finding(
                rule="maximum_loan_amount",
                passed=False,
                actual=amount,
                required=max_amount,
                message=f"Requested ₹{amount:,.0f} exceeds maximum ₹{max_amount:,.0f}",
                severity="medium",
                waivable=True
            )
            return False
        
        self._add_finding(
            rule="loan_amount",
            passed=True,
            actual=amount,
            required=f"{min_amount:,.0f} - {max_amount:,.0f}",
            message="Loan amount within limits"
        )
        return True
    
    def _check_collateral_requirements(
        self,
        applicant: ApplicantProfile,
        policy: Dict[str, Any]
    ) -> bool:
        """
        Check if collateral requirements are met.
        
        DEVELOPER NOTE:
        ---------------
        Collateral is typically required:
        - Above certain loan amounts (threshold varies by bank)
        - For higher-risk applicants
        - For longer tenure loans
        
        LTV (Loan-to-Value) ratio limits how much you can borrow
        against the collateral value.
        """
        amount = applicant.requested_loan_amount
        threshold = policy.get("collateral_threshold", float("inf"))
        
        # Check if amount requires collateral
        if amount > threshold:
            if not applicant.has_collateral:
                self._add_finding(
                    rule="collateral_required",
                    passed=False,
                    actual="No collateral",
                    required=f"Required for loans above ₹{threshold:,.0f}",
                    message=f"Loans above ₹{threshold:,.0f} require collateral",
                    severity="high",
                    waivable=False  # This is typically non-negotiable
                )
                return False
            
            # Check LTV ratio
            ltv_ratio = policy.get("ltv_ratio", 0.80)
            max_loan_on_collateral = applicant.collateral_value * ltv_ratio
            
            if amount > max_loan_on_collateral:
                self._add_finding(
                    rule="ltv_ratio",
                    passed=False,
                    actual=amount / applicant.collateral_value if applicant.collateral_value > 0 else 0,
                    required=ltv_ratio,
                    message=f"Loan amount exceeds {ltv_ratio*100:.0f}% of collateral value",
                    severity="medium",
                    waivable=True
                )
                return False
        
        return True
    
    # =========================================================================
    # AFFORDABILITY CALCULATION
    # =========================================================================
    
    def _calculate_affordability(
        self,
        applicant: ApplicantProfile,
        policy: Dict[str, Any]
    ) -> Tuple[bool, float]:
        """
        Calculate if the applicant can afford the loan.
        
        DEVELOPER NOTE:
        ---------------
        Affordability is measured using FOIR:
        FOIR = (Existing EMIs + New EMI) / Net Monthly Income
        
        A lower FOIR is better:
        - 0.30 = Excellent (plenty of buffer)
        - 0.40 = Good
        - 0.50 = Acceptable (most banks' limit)
        - 0.60+ = Risky
        
        Returns:
            Tuple of (is_affordable, proposed_emi)
        """
        # Calculate proposed EMI (simplified calculation)
        # In real banking, exact rate would be used
        principal = applicant.requested_loan_amount
        tenure_months = applicant.requested_tenure_months
        
        # Use average rate from policy for estimation
        rate_range = policy.get("rate_range", {"min": 10, "max": 12})
        annual_rate = (rate_range["min"] + rate_range["max"]) / 2
        monthly_rate = annual_rate / 12 / 100
        
        # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
        if monthly_rate > 0 and tenure_months > 0:
            power = (1 + monthly_rate) ** tenure_months
            proposed_emi = principal * monthly_rate * power / (power - 1)
        else:
            proposed_emi = principal / max(tenure_months, 1)
        
        # Calculate FOIR
        total_income = applicant.monthly_income
        if applicant.has_co_applicant:
            total_income += applicant.co_applicant_income
        
        if total_income <= 0:
            return False, proposed_emi
        
        total_obligations = applicant.existing_emis + proposed_emi
        foir = total_obligations / total_income
        
        # Get FOIR limit from policy
        max_foir = policy.get("max_foir", 0.50)
        
        if foir > max_foir:
            self._add_finding(
                rule="foir_check",
                passed=False,
                actual=f"{foir*100:.1f}%",
                required=f"{max_foir*100:.1f}%",
                message=f"FOIR {foir*100:.1f}% exceeds limit of {max_foir*100:.1f}%",
                severity="high",
                waivable=True
            )
            return False, proposed_emi
        
        self._add_finding(
            rule="foir_check",
            passed=True,
            actual=f"{foir*100:.1f}%",
            required=f"{max_foir*100:.1f}%",
            message=f"FOIR {foir*100:.1f}% within acceptable limit"
        )
        return True, proposed_emi
    
    # =========================================================================
    # OSR (ON SANCTION RISK) HANDLER
    # =========================================================================
    
    def _handle_osr(
        self,
        applicant: ApplicantProfile,
        credit_bureau: CreditBureauResult,
        policy: Dict[str, Any],
        risk_level: RiskLevel
    ) -> Dict[str, Any]:
        """
        Handle borderline cases through OSR (On Sanction Risk) process.
        
        DEVELOPER NOTE:
        ---------------
        OSR is a CRITICAL feature in real banking. It allows approving cases
        that technically fail some policy criteria but have compensating factors.
        
        Common OSR scenarios:
        1. Income slightly below threshold but strong co-applicant
        2. Credit score borderline but excellent payment history
        3. LTV slightly exceeded but additional insurance offered
        4. Age at maturity exceeded but shorter tenure acceptable
        
        This is how real banks actually work - rigid rejection would lose
        many good customers!
        
        Returns:
            Dictionary with:
            - approvable: bool
            - conditions: list of conditions if approvable
            - rejection_reason: reason if not approvable
            - adjusted_amount: modified loan amount if applicable
        """
        # If risk is CRITICAL, no OSR possible
        if risk_level == RiskLevel.CRITICAL:
            return {
                "approvable": False,
                "rejection_reason": "Risk level too high for OSR consideration"
            }
        
        # Analyze failed findings
        failed_findings = [f for f in self.policy_findings if not f.passed]
        waivable_failures = [f for f in failed_findings if f.is_waivable]
        non_waivable_failures = [f for f in failed_findings if not f.is_waivable]
        
        # If there are non-waivable failures, cannot approve
        if non_waivable_failures:
            reasons = [f.message for f in non_waivable_failures]
            return {
                "approvable": False,
                "rejection_reason": "; ".join(reasons)
            }
        
        # No failures or only waivable failures - check compensating factors
        conditions = []
        adjusted_amount = None
        
        # Check for compensating factors
        compensating_factors = self._identify_compensating_factors(
            applicant, credit_bureau
        )
        
        # Evaluate if compensation is sufficient
        for finding in waivable_failures:
            compensation = self._can_compensate(finding, compensating_factors, applicant)
            
            if compensation["can_compensate"]:
                conditions.extend(compensation.get("conditions", []))
                if compensation.get("adjusted_amount"):
                    if adjusted_amount is None:
                        adjusted_amount = applicant.requested_loan_amount
                    adjusted_amount = min(adjusted_amount, compensation["adjusted_amount"])
            else:
                return {
                    "approvable": False,
                    "rejection_reason": f"Cannot compensate for: {finding.message}"
                }
        
        # If we get here, all failures can be compensated
        # Add standard OSR conditions
        if risk_level == RiskLevel.HIGH:
            conditions.append("Requires Credit Head approval")
        elif risk_level == RiskLevel.MEDIUM:
            conditions.append("Requires Senior Credit Officer approval")
        
        return {
            "approvable": True,
            "conditions": conditions,
            "adjusted_amount": adjusted_amount
        }
    
    def _identify_compensating_factors(
        self,
        applicant: ApplicantProfile,
        credit_bureau: CreditBureauResult
    ) -> Dict[str, Any]:
        """
        Identify factors that can compensate for policy deviations.
        
        DEVELOPER NOTE:
        ---------------
        Compensating factors are positive attributes that can offset
        weaknesses in the application. Real underwriters look for:
        
        - Strong co-applicant (great income, excellent credit)
        - Existing customer relationship
        - Collateral with good margin
        - High income stability (long tenure with employer)
        - Clean payment history despite lower score
        """
        factors = {
            "strong_co_applicant": False,
            "existing_customer": applicant.is_existing_customer,
            "has_collateral": applicant.has_collateral,
            "collateral_margin": 0.0,
            "stable_employment": applicant.years_of_experience >= 3,
            "clean_payment_history": (
                credit_bureau.days_past_due_30 == 0 and
                credit_bureau.days_past_due_60 == 0 and
                credit_bureau.days_past_due_90 == 0
            ),
            "low_utilization": credit_bureau.utilization_ratio < 0.30,
        }
        
        # Check co-applicant strength
        if applicant.has_co_applicant:
            if applicant.co_applicant_income >= 50000:
                factors["strong_co_applicant"] = True
            if applicant.co_applicant_credit_score >= 750:
                factors["strong_co_applicant"] = True
        
        # Calculate collateral margin
        if applicant.has_collateral and applicant.collateral_value > 0:
            margin = (applicant.collateral_value - applicant.requested_loan_amount) / applicant.requested_loan_amount
            factors["collateral_margin"] = max(0, margin)
        
        return factors
    
    def _can_compensate(
        self,
        finding: PolicyFinding,
        factors: Dict[str, Any],
        applicant: ApplicantProfile
    ) -> Dict[str, Any]:
        """
        Check if compensating factors can offset a specific policy failure.
        
        DEVELOPER NOTE:
        ---------------
        This is the core OSR logic. Each type of failure has different
        compensation rules:
        
        - Credit score: Strong co-applicant or collateral
        - Income: Co-applicant income or reduced loan amount
        - FOIR: Reduce loan amount or extend tenure
        - Age at maturity: Reduce tenure
        """
        rule = finding.rule_name
        
        # Credit Score Deviation
        if rule == "credit_score":
            if factors["strong_co_applicant"]:
                return {
                    "can_compensate": True,
                    "conditions": ["Co-applicant to be added as co-borrower"]
                }
            if factors["has_collateral"] and factors["collateral_margin"] > 0.20:
                return {
                    "can_compensate": True,
                    "conditions": ["Collateral security mandatory"]
                }
            return {"can_compensate": False}
        
        # Income Deviation
        if rule in ["minimum_income", "co_applicant_income"]:
            if factors["strong_co_applicant"]:
                return {
                    "can_compensate": True,
                    "conditions": ["Co-applicant income to be considered for eligibility"]
                }
            # Offer reduced loan amount
            if hasattr(finding, "actual_value") and hasattr(finding, "required_value"):
                try:
                    actual = float(finding.actual_value) if finding.actual_value else 0
                    required = float(finding.required_value) if finding.required_value else 1
                    if actual > 0 and required > 0:
                        ratio = actual / required
                        if ratio >= 0.85:  # Within 15%
                            adjusted_amount = applicant.requested_loan_amount * ratio
                            return {
                                "can_compensate": True,
                                "conditions": [f"Loan amount reduced to ₹{adjusted_amount:,.0f}"],
                                "adjusted_amount": adjusted_amount
                            }
                except (ValueError, TypeError):
                    pass
            return {"can_compensate": False}
        
        # FOIR Deviation
        if rule == "foir_check":
            # Option 1: Reduce loan amount
            if factors["stable_employment"] or factors["existing_customer"]:
                adjusted_amount = applicant.requested_loan_amount * 0.90
                return {
                    "can_compensate": True,
                    "conditions": [
                        f"Loan amount reduced to ₹{adjusted_amount:,.0f}",
                        "Salary account to be maintained with bank"
                    ],
                    "adjusted_amount": adjusted_amount
                }
            return {"can_compensate": False}
        
        # Age at Maturity Deviation
        if rule == "age_at_maturity":
            # Reduce tenure to meet age limit
            return {
                "can_compensate": True,
                "conditions": ["Tenure to be reduced to meet age limit at maturity"]
            }
        
        # LTV Ratio Deviation
        if rule == "ltv_ratio":
            # Reduce loan amount to meet LTV
            if factors["has_collateral"]:
                ltv = 0.80  # Standard LTV
                adjusted_amount = applicant.collateral_value * ltv
                return {
                    "can_compensate": True,
                    "conditions": [f"Loan amount capped at ₹{adjusted_amount:,.0f} (80% LTV)"],
                    "adjusted_amount": adjusted_amount
                }
            return {"can_compensate": False}
        
        # Loan Amount Deviation
        if rule == "maximum_loan_amount":
            adjusted_amount = float(finding.required_value.replace(",", "").split()[0]) if isinstance(finding.required_value, str) else finding.required_value
            return {
                "can_compensate": True,
                "conditions": [f"Loan amount reduced to maximum eligible: ₹{adjusted_amount:,.0f}"],
                "adjusted_amount": adjusted_amount
            }
        
        # Default: Cannot compensate
        return {"can_compensate": False}
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _reset_state(self):
        """Reset agent state for processing a new application."""
        self.current_mode = UnderwritingMode.INTERNAL
        self.policy_findings = []
        self.deviations = []
        self.customer_messages = []
    
    def _validate_inputs(
        self,
        bank: str,
        applicant: ApplicantProfile,
        verification: VerificationResult
    ) -> bool:
        """
        Validate that inputs are complete and verification passed.
        
        DEVELOPER NOTE:
        ---------------
        This is a safety check. Underwriting should NOT proceed if:
        - KYC is not verified
        - AML checks not cleared
        - Required documents missing
        
        These are pre-requisites handled by Verification Agent.
        """
        # Check bank is valid
        if bank not in BANK_POLICIES:
            self._add_finding(
                rule="bank_validation",
                passed=False,
                message=f"Unknown bank: {bank}. Valid banks: {list(BANK_POLICIES.keys())}",
                severity="critical"
            )
            return False
        
        # Check verification is complete
        if not verification.kyc_verified:
            self.current_mode = UnderwritingMode.AGENT_SWITCH
            self.customer_messages.append("KYC verification incomplete - switching to Verification Agent")
            return False
        
        if not verification.aml_cleared:
            self._add_finding(
                rule="aml_check",
                passed=False,
                message="AML checks not cleared",
                severity="critical"
            )
            return False
        
        return True
    
    def _get_bank_policy(self, bank: str, loan_type: str) -> Optional[Dict[str, Any]]:
        """
        Get bank-specific policy for the loan type.
        
        DEVELOPER NOTE:
        ---------------
        This method now uses a HYBRID approach:
        
        1. STATIC DATA (BANK_POLICIES): Always available, provides base policy
        2. RAG RETRIEVAL: Queries bank_docs for latest policy updates
        3. MERGE: RAG data can override/enhance static data
        
        This ensures:
        - Agent works even without RAG (offline mode)
        - Latest policy changes are picked up from documents
        - Consistent structure for policy rules
        
        Data Flow:
        ----------
        bank_docs/manual/indian_bank_loans_2026.md 
            -> RAG Engine (embeddings in chroma_db)
            -> Query: "{bank} {loan_type} loan policy"
            -> Retrieved context merged with static policy
        """
        # First, get static policy as baseline
        static_policy = None
        if bank in BANK_POLICIES:
            bank_data = BANK_POLICIES[bank]
            if loan_type in bank_data:
                static_policy = bank_data[loan_type].copy()
        
        # If RAG is enabled, try to enhance with latest document data
        if self.rag_enabled and self.rag_retriever:
            rag_policy = self._get_policy_from_rag(bank, loan_type)
            
            if rag_policy and static_policy:
                # Merge RAG data into static policy
                # RAG data takes precedence for overlapping fields
                merged_policy = static_policy.copy()
                merged_policy.update(rag_policy)
                merged_policy["_source"] = "rag_enhanced"
                print(f"✅ Policy enhanced with RAG data for {bank} {loan_type}")
                return merged_policy
            elif rag_policy:
                # Only RAG data available
                rag_policy["_source"] = "rag_only"
                return rag_policy
        
        # Fall back to static policy
        if static_policy:
            static_policy["_source"] = "static"
            return static_policy
        
        return None
    
    def _get_policy_from_rag(self, bank: str, loan_type: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve policy information from RAG (bank documents).
        
        DEVELOPER NOTE:
        ---------------
        This queries the ChromaDB vector store that was populated by ingest_documents.py
        with policy documents from bank_docs/ folder.
        
        The RAG retriever returns relevant text chunks which we then parse
        to extract structured policy data.
        
        IMPORTANT: RAG provides TEXT context, not structured data.
        We extract key values using pattern matching.
        """
        if not self.rag_retriever:
            return None
        
        try:
            # Build query for policy retrieval
            query = f"{bank} {loan_type} loan interest rate eligibility collateral tenure"
            
            # Retrieve from RAG
            results = self.rag_retriever.retrieve(query, top_k=3)
            
            if not results:
                return None
            
            # Parse retrieved content to extract policy values
            extracted_policy = self._parse_rag_results(results, bank, loan_type)
            
            if extracted_policy:
                print(f"📄 Retrieved policy from documents: {bank} {loan_type}")
            
            return extracted_policy
            
        except Exception as e:
            print(f"⚠️ RAG retrieval failed: {e}")
            return None
    
    def _parse_rag_results(
        self, 
        results: List[Any], 
        bank: str, 
        loan_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse RAG retrieval results to extract structured policy data.
        
        DEVELOPER NOTE:
        ---------------
        RAG returns text chunks. We need to extract structured data like:
        - Interest rates (min/max)
        - Loan amounts
        - Credit score requirements
        - Tenure limits
        
        This uses regex patterns to find specific values in the text.
        It's not perfect but provides real-time document data.
        """
        import re
        
        policy = {}
        
        # Combine all retrieved content
        combined_text = ""
        for result in results:
            if hasattr(result, 'content'):
                combined_text += result.content + "\n"
            elif isinstance(result, dict) and 'content' in result:
                combined_text += result['content'] + "\n"
            elif isinstance(result, str):
                combined_text += result + "\n"
        
        if not combined_text:
            return None
        
        # Check if content is relevant to the bank
        if bank.lower() not in combined_text.lower():
            return None
        
        # Extract interest rate range
        rate_patterns = [
            r'(\d+\.?\d*)\s*%?\s*[-–to]\s*(\d+\.?\d*)\s*%',
            r'(\d+\.?\d*)\s*%\s*onwards',
            r'interest.*?(\d+\.?\d*)\s*%',
        ]
        
        for pattern in rate_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    policy["rate_range"] = {
                        "min": float(match.group(1)),
                        "max": float(match.group(2))
                    }
                else:
                    policy["rate_range"] = {
                        "min": float(match.group(1)),
                        "max": float(match.group(1)) + 2.0
                    }
                break
        
        # Extract loan amount limits
        amount_patterns = [
            r'up\s*to\s*₹?\s*([\d,]+)\s*(lakh|crore)?',
            r'maximum.*?₹?\s*([\d,]+)\s*(lakh|crore)?',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                amount = float(match.group(1).replace(',', ''))
                multiplier = 1
                if match.group(2):
                    if 'lakh' in match.group(2).lower():
                        multiplier = 100000
                    elif 'crore' in match.group(2).lower():
                        multiplier = 10000000
                
                if loan_type == "education":
                    policy["max_amount_abroad"] = amount * multiplier
                else:
                    policy["max_amount"] = amount * multiplier
                break
        
        # Extract collateral threshold
        collateral_match = re.search(
            r'no\s*collateral.*?up\s*to\s*₹?\s*([\d,]+)\s*(lakh)?', 
            combined_text, 
            re.IGNORECASE
        )
        if collateral_match:
            amount = float(collateral_match.group(1).replace(',', ''))
            if collateral_match.group(2) and 'lakh' in collateral_match.group(2).lower():
                amount *= 100000
            policy["collateral_threshold"] = amount
        
        # Extract tenure
        tenure_match = re.search(
            r'tenure.*?(\d+)\s*years?|up\s*to\s*(\d+)\s*years?', 
            combined_text, 
            re.IGNORECASE
        )
        if tenure_match:
            years = int(tenure_match.group(1) or tenure_match.group(2))
            policy["max_tenure_years"] = years
        
        # Extract moratorium
        moratorium_match = re.search(
            r'moratorium.*?(\d+)\s*months?|course.*?\+\s*(\d+)\s*months?',
            combined_text,
            re.IGNORECASE
        )
        if moratorium_match:
            months = int(moratorium_match.group(1) or moratorium_match.group(2))
            policy["moratorium_months"] = months
        
        return policy if policy else None
    
    def _add_finding(
        self,
        rule: str,
        passed: bool,
        actual: Any = None,
        required: Any = None,
        message: str = "",
        severity: str = "medium",
        waivable: bool = True
    ):
        """Add a policy finding to the list."""
        finding = PolicyFinding(
            rule_name=rule,
            passed=passed,
            actual_value=actual,
            required_value=required,
            message=message,
            severity=severity,
            is_waivable=waivable
        )
        self.policy_findings.append(finding)
    
    def _prepare_sanction_data(
        self,
        applicant: ApplicantProfile,
        policy: Dict[str, Any],
        proposed_emi: float,
        adjusted_amount: Optional[float] = None
    ) -> SanctionData:
        """
        Prepare sanction-ready data for the Sanction Letter Agent.
        
        DEVELOPER NOTE:
        ---------------
        This creates the output that goes to the Sanction Letter Generator.
        Note: Interest rates are provisional (ranges only).
        Final rates are fixed at disbursement.
        """
        amount = adjusted_amount or applicant.requested_loan_amount
        
        # Get rate range from policy
        rate_range = policy.get("rate_range", 
                               policy.get("rate_range_india",
                               policy.get("rate_range_new", {"min": 10, "max": 12})))
        
        rate_range_str = f"{rate_range['min']}% - {rate_range['max']}%"
        
        # Check for moratorium
        moratorium = policy.get("moratorium_months", 0)
        
        # Recalculate EMI if amount was adjusted
        if adjusted_amount and adjusted_amount != applicant.requested_loan_amount:
            tenure_months = applicant.requested_tenure_months
            annual_rate = (rate_range["min"] + rate_range["max"]) / 2
            monthly_rate = annual_rate / 12 / 100
            if monthly_rate > 0 and tenure_months > 0:
                power = (1 + monthly_rate) ** tenure_months
                proposed_emi = amount * monthly_rate * power / (power - 1)
        
        return SanctionData(
            approved_amount=amount,
            tenure_months=applicant.requested_tenure_months,
            interest_type=policy.get("interest_type", "Floating"),
            tentative_rate_range=rate_range_str,
            estimated_emi=proposed_emi,
            moratorium_months=moratorium,
            moratorium_applicable=moratorium > 0,
            processing_fee_percentage=policy.get("processing_fee_percentage", 1.0),
            sanction_validity_days=90
        )
    
    def _generate_output(
        self,
        bank: str,
        decision: CreditDecision,
        risk_level: RiskLevel,
        sanction_data: Optional[SanctionData] = None,
        conditions: Optional[List[str]] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate the final structured output (JSON-serializable).
        
        DEVELOPER NOTE:
        ---------------
        This output follows the STRICT format specified in the system prompt.
        It's designed to be:
        1. Machine-readable (JSON)
        2. Auditable (includes policy findings)
        3. Ready for next agent (sanction data included)
        """
        # Collect policy findings as strings
        policy_finding_messages = [f.message for f in self.policy_findings if f.message]
        
        output = {
            "mode": self.current_mode.value,
            "bank": bank,
            "credit_decision": decision.value,
            "risk_summary": risk_level.value,
            "policy_findings": policy_finding_messages,
        }
        
        # Add conditions for conditional approval
        if conditions:
            output["conditions"] = conditions
        elif decision == CreditDecision.CONDITIONALLY_APPROVED:
            output["conditions"] = []
        
        # Add rejection reason
        if reason and decision == CreditDecision.REJECTED:
            output["rejection_reason"] = reason
        
        # Add sanction data for approvals
        if sanction_data and decision in [CreditDecision.APPROVED, CreditDecision.CONDITIONALLY_APPROVED]:
            output["sanction_data"] = {
                "approved_amount": sanction_data.approved_amount,
                "tenure_months": sanction_data.tenure_months,
                "interest_type": sanction_data.interest_type,
                "tentative_rate_range": sanction_data.tentative_rate_range,
                "estimated_emi": round(sanction_data.estimated_emi, 2),
                "moratorium_applicable": sanction_data.moratorium_applicable,
                "moratorium_months": sanction_data.moratorium_months,
                "processing_fee_percentage": sanction_data.processing_fee_percentage,
                "validity_days": sanction_data.sanction_validity_days
            }
        
        return output


# =============================================================================
# TEST FUNCTION
# =============================================================================

def test_underwriting_agent():
    """
    Test the Underwriting Agent with sample cases.
    
    DEVELOPER NOTE:
    ---------------
    Run this function to see the agent in action:
    
    >>> python -c "from underWritingAgent import test_underwriting_agent; test_underwriting_agent()"
    
    This tests three scenarios:
    1. Good applicant (should be approved)
    2. Borderline case (should be conditionally approved with OSR)
    3. Poor applicant (should be rejected)
    """
    print("=" * 60)
    print("🏦 UNDERWRITING AGENT TEST")
    print("=" * 60)
    
    # Initialize agent (without RAG for testing)
    agent = UnderwritingAgent(enable_rag=False)
    
    # Verification result (assume all verified)
    verification = VerificationResult(
        kyc_verified=True,
        aml_cleared=True,
        documents_verified=True,
        identity_docs_ok=True,
        address_docs_ok=True,
        income_docs_ok=True,
        employment_verified=True
    )
    
    # -------------------------------------------------------------------------
    # TEST 1: Good Applicant - Should be APPROVED
    # -------------------------------------------------------------------------
    print("\n" + "-" * 60)
    print("TEST 1: Good Applicant (Expected: APPROVED)")
    print("-" * 60)
    
    good_applicant = ApplicantProfile(
        name="Rahul Sharma",
        age=32,
        gender="M",
        employment_type=EmploymentType.SALARIED,
        employer_name="TCS",
        monthly_income=85000,
        annual_income=1020000,
        years_of_experience=8,
        existing_emis=15000,
        requested_loan_amount=2000000,
        requested_tenure_months=180,  # 15 years
        loan_type=LoanType.HOME,
        is_existing_customer=True
    )
    
    good_credit = CreditBureauResult(
        credit_score=765,
        score_bucket=CreditScoreBucket.EXCELLENT,
        total_accounts=5,
        active_accounts=2,
        overdue_accounts=0,
        days_past_due_30=0,
        days_past_due_60=0,
        days_past_due_90=0,
        utilization_ratio=0.25
    )
    
    result1 = agent.process_application(
        bank="SBI",
        applicant=good_applicant,
        credit_bureau=good_credit,
        verification=verification
    )
    
    print(f"Decision: {result1['credit_decision']}")
    print(f"Risk Level: {result1['risk_summary']}")
    if result1.get('sanction_data'):
        print(f"Approved Amount: ₹{result1['sanction_data']['approved_amount']:,.0f}")
        print(f"Estimated EMI: ₹{result1['sanction_data']['estimated_emi']:,.0f}")
    
    # -------------------------------------------------------------------------
    # TEST 2: Borderline Case - Should be CONDITIONALLY APPROVED
    # -------------------------------------------------------------------------
    print("\n" + "-" * 60)
    print("TEST 2: Borderline Case (Expected: CONDITIONALLY APPROVED)")
    print("-" * 60)
    
    borderline_applicant = ApplicantProfile(
        name="Priya Patel",
        age=28,
        gender="F",
        employment_type=EmploymentType.SALARIED,
        employer_name="Infosys",
        monthly_income=45000,
        annual_income=540000,
        years_of_experience=4,
        existing_emis=10000,
        requested_loan_amount=800000,
        requested_tenure_months=60,  # 5 years
        loan_type=LoanType.PERSONAL,
        has_co_applicant=True,
        co_applicant_income=60000,
        co_applicant_credit_score=780,
        co_applicant_relationship="Spouse"
    )
    
    borderline_credit = CreditBureauResult(
        credit_score=680,  # Below HDFC's preferred score of 700
        score_bucket=CreditScoreBucket.FAIR,
        total_accounts=3,
        active_accounts=2,
        overdue_accounts=0,
        days_past_due_30=0,
        days_past_due_60=0,
        days_past_due_90=0,
        utilization_ratio=0.40
    )
    
    result2 = agent.process_application(
        bank="HDFC",
        applicant=borderline_applicant,
        credit_bureau=borderline_credit,
        verification=verification
    )
    
    print(f"Decision: {result2['credit_decision']}")
    print(f"Risk Level: {result2['risk_summary']}")
    if result2.get('conditions'):
        print(f"Conditions: {result2['conditions']}")
    
    # -------------------------------------------------------------------------
    # TEST 3: Poor Applicant - Should be REJECTED
    # -------------------------------------------------------------------------
    print("\n" + "-" * 60)
    print("TEST 3: Poor Applicant (Expected: REJECTED)")
    print("-" * 60)
    
    poor_applicant = ApplicantProfile(
        name="Amit Kumar",
        age=45,
        gender="M",
        employment_type=EmploymentType.SELF_EMPLOYED_BUSINESS,
        monthly_income=25000,
        annual_income=300000,
        years_of_experience=5,
        existing_emis=20000,  # High existing burden
        requested_loan_amount=2000000,
        requested_tenure_months=120,
        loan_type=LoanType.BUSINESS
    )
    
    poor_credit = CreditBureauResult(
        credit_score=580,  # Very low
        score_bucket=CreditScoreBucket.POOR,
        total_accounts=8,
        active_accounts=5,
        overdue_accounts=2,
        days_past_due_30=3,
        days_past_due_60=2,
        days_past_due_90=1,  # Major red flag
        utilization_ratio=0.85,
        has_write_offs=True  # Deal breaker
    )
    
    result3 = agent.process_application(
        bank="ICICI",
        applicant=poor_applicant,
        credit_bureau=poor_credit,
        verification=verification
    )
    
    print(f"Decision: {result3['credit_decision']}")
    print(f"Risk Level: {result3['risk_summary']}")
    if result3.get('rejection_reason'):
        print(f"Reason: {result3['rejection_reason']}")
    
    print("\n" + "=" * 60)
    print("🏦 TEST COMPLETE")
    print("=" * 60)
    
    return {
        "test_1_approved": result1['credit_decision'] == "Approved",
        "test_2_conditional": result2['credit_decision'] == "Conditionally Approved",
        "test_3_rejected": result3['credit_decision'] == "Rejected"
    }


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Run tests when file is executed directly
    results = test_underwriting_agent()
    
    print("\n📊 Test Results Summary:")
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test}: {status}")



# ============================================================================
# MASTER AGENT ENTRY POINT
# ============================================================================

_underwriting_agent_instance = UnderwritingAgent()

def handle_underwriting(user_message: str):
    """
    Entry point used by master_agent
    """
    return _underwriting_agent_instance.process_message(user_message)

