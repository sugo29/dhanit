"""
🧠 LOAN SALES AGENT (INDIA)
===========================
A human-like, ethical, persuasive AI sales representative for Indian loan products.

This agent builds trust, educates users, personalizes recommendations,
and respects user autonomy at all times.

Now with RAG (Retrieval-Augmented Generation) for accurate, citation-backed
bank policy information.
"""

from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
import re

# RAG Engine Integration
try:
    from rag_engine import RAGRetriever, RAGConfig
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    RAGRetriever = None
    RAGConfig = None


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class Tone(Enum):
    CASUAL = "casual"
    NEUTRAL = "neutral"
    FORMAL = "formal"


class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    HESITANT = "hesitant"
    SKEPTICAL = "skeptical"


class FinancialLiteracy(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AgentMode(Enum):
    SALES = "sales"
    EDUCATION = "education"


class LoanType(Enum):
    EDUCATION = "education"
    HOME = "home"
    PERSONAL = "personal"
    VEHICLE = "vehicle"
    BUSINESS = "business"
    GOLD = "gold"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class UserContext:
    """Session-only memory for personalization."""
    profession: Optional[str] = None
    monthly_income: Optional[str] = None
    loan_purpose: Optional[str] = None
    loan_type: Optional[LoanType] = None
    risk_sensitivity: Optional[str] = None
    past_objections: List[str] = field(default_factory=list)
    study_destination: Optional[str] = None  # For education loans
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    fast_track_eligible: bool = False
    trust_score: int = 0  # 0-100
    
    def add_objection(self, objection: str):
        if objection not in self.past_objections:
            self.past_objections.append(objection)
    
    def update_trust_score(self, delta: int):
        self.trust_score = max(0, min(100, self.trust_score + delta))


@dataclass
class UserAnalysis:
    """Real-time analysis of user's communication style."""
    tone: Tone = Tone.NEUTRAL
    sentiment: Sentiment = Sentiment.NEUTRAL
    financial_literacy: FinancialLiteracy = FinancialLiteracy.MEDIUM


@dataclass
class LoanProduct:
    """Generic loan product information (no hallucinated rates)."""
    name: str
    type: LoanType
    interest_type: str  # "Fixed" or "Floating"
    typical_tenure: str
    moratorium: Optional[str]
    repayment_structure: str
    advantages: List[str]
    disadvantages: List[str]
    eligibility_criteria: List[str]


# ============================================================================
# LOAN PRODUCT DATABASE (Generic Information Only)
# ============================================================================

LOAN_PRODUCTS: Dict[LoanType, List[LoanProduct]] = {
    LoanType.EDUCATION: [
        LoanProduct(
            name="Public Sector Bank Education Loan",
            type=LoanType.EDUCATION,
            interest_type="Floating (linked to MCLR/RLLR)",
            typical_tenure="Up to 15 years after moratorium",
            moratorium="Course period + 6-12 months",
            repayment_structure="EMI-based after moratorium ends",
            advantages=[
                "Generally lower interest rates",
                "Government subsidy schemes available (e.g., CSIS for EWS)",
                "No collateral for loans up to ₹7.5 lakh",
                "Tax benefits under Section 80E"
            ],
            disadvantages=[
                "Processing can be slower",
                "More documentation required",
                "May require co-applicant with income proof"
            ],
            eligibility_criteria=[
                "Indian citizen",
                "Admission secured in recognized institution",
                "Co-applicant (parent/guardian) required"
            ]
        ),
        LoanProduct(
            name="Private Bank/NBFC Education Loan",
            type=LoanType.EDUCATION,
            interest_type="Fixed or Floating options",
            typical_tenure="Up to 12-15 years",
            moratorium="Course period + 6 months typically",
            repayment_structure="EMI-based, some offer partial EMI during study",
            advantages=[
                "Faster processing and disbursement",
                "Higher loan amounts available",
                "Flexible repayment options",
                "Digital-first application process"
            ],
            disadvantages=[
                "Generally higher interest rates",
                "Collateral often required for higher amounts",
                "Processing fees may be higher"
            ],
            eligibility_criteria=[
                "Indian citizen",
                "Admission to recognized course",
                "Co-applicant with stable income"
            ]
        )
    ],
    LoanType.HOME: [
        LoanProduct(
            name="Home Loan - Floating Rate",
            type=LoanType.HOME,
            interest_type="Floating (linked to repo rate)",
            typical_tenure="Up to 30 years",
            moratorium="None (EMI starts immediately)",
            repayment_structure="EMI-based with prepayment options",
            advantages=[
                "Benefit from rate cuts automatically",
                "Tax benefits on principal (80C) and interest (24b)",
                "Long tenure reduces EMI burden",
                "Balance transfer options available"
            ],
            disadvantages=[
                "EMI increases if rates rise",
                "Uncertainty in long-term planning"
            ],
            eligibility_criteria=[
                "Age 21-65 years",
                "Stable income source",
                "Property as collateral"
            ]
        )
    ],
    LoanType.PERSONAL: [
        LoanProduct(
            name="Personal Loan",
            type=LoanType.PERSONAL,
            interest_type="Fixed (mostly)",
            typical_tenure="1-5 years typically",
            moratorium="None",
            repayment_structure="Fixed EMI throughout tenure",
            advantages=[
                "No collateral required",
                "Quick disbursement",
                "Flexible end-use",
                "Predictable EMI amount"
            ],
            disadvantages=[
                "Higher interest rates than secured loans",
                "Lower loan amounts",
                "No tax benefits"
            ],
            eligibility_criteria=[
                "Salaried or self-employed",
                "Minimum income threshold",
                "Good credit score"
            ]
        )
    ],
    LoanType.VEHICLE: [
        LoanProduct(
            name="Vehicle Loan",
            type=LoanType.VEHICLE,
            interest_type="Fixed or Floating",
            typical_tenure="3-7 years",
            moratorium="None",
            repayment_structure="EMI-based",
            advantages=[
                "Lower rates than personal loans",
                "High LTV ratio (up to 100% for new cars)",
                "Quick processing"
            ],
            disadvantages=[
                "Vehicle acts as security",
                "Depreciation risk",
                "No tax benefits for personal use"
            ],
            eligibility_criteria=[
                "Age 21-65 years",
                "Stable income",
                "Vehicle as hypothecation"
            ]
        )
    ],
    LoanType.BUSINESS: [
        LoanProduct(
            name="Business Loan",
            type=LoanType.BUSINESS,
            interest_type="Fixed or Floating",
            typical_tenure="1-5 years (working capital), up to 15 years (term loan)",
            moratorium="Varies by lender",
            repayment_structure="EMI or bullet repayment options",
            advantages=[
                "Helps business expansion",
                "Government schemes available (MUDRA, CGTMSE)",
                "Interest is tax-deductible"
            ],
            disadvantages=[
                "May require collateral for large amounts",
                "Higher rates for unsecured loans",
                "Extensive documentation"
            ],
            eligibility_criteria=[
                "Business vintage of 2-3 years typically",
                "Profitability track record",
                "GST registration (for many schemes)"
            ]
        )
    ]
}


# ============================================================================
# PERSUASIVE MICROCOPY TEMPLATES
# ============================================================================

MICROCOPY = {
    "ask_income": {
        "standard": "What's your monthly take-home so I can find the best rate for you?",
        "formal": "May I know your approximate monthly income to suggest suitable options?",
        "casual": "Roughly what's your monthly income? This helps me avoid suggesting the wrong banks."
    },
    "eligible": {
        "standard": "Good news! You qualify for options most people don't — want to see them?",
        "formal": "Based on your profile, you're eligible for some premium options. Shall I elaborate?",
        "casual": "Hey, you've got some great options! Want me to show you?"
    },
    "submit_cta": {
        "standard": "Let's lock this offer while it's available — takes about 2 minutes.",
        "formal": "Shall we proceed with the application? It typically takes just a few minutes.",
        "casual": "Ready to grab this? Super quick, I promise!"
    },
    "check_eligibility": {
        "standard": "Want to quickly check eligibility? No commitment at all.",
        "formal": "Would you like to verify your eligibility? This is purely informational.",
        "casual": "Wanna see if you qualify? Takes like 30 seconds!"
    },
    "no_pressure": {
        "standard": "No pressure at all — we'll go at your pace.",
        "formal": "Please take your time. There's absolutely no obligation.",
        "casual": "Totally cool, no rush at all!"
    }
}


# ============================================================================
# HESITATION PHRASES DETECTION
# ============================================================================

HESITATION_PHRASES = [
    "just checking",
    "just looking",
    "not sure",
    "maybe later",
    "i'll think",
    "let me think",
    "need to discuss",
    "have to ask",
    "not ready",
    "just exploring",
    "browsing",
    "considering"
]

EDUCATION_TRIGGER_PHRASES = [
    "i assume",
    "what does",
    "what is",
    "can you explain",
    "i don't understand",
    "i'm confused",
    "what do you mean",
    "how does",
    "tell me about",
    "confused about",
    "not sure what"
]

FAST_TRACK_INDICATORS = [
    "yes",
    "sure",
    "let's do it",
    "go ahead",
    "sounds good",
    "proceed",
    "apply",
    "check eligibility",
    "show me",
    "what's next"
]


# ============================================================================
# MAIN AGENT CLASS
# ============================================================================

class LoanSalesAgent:
    """
    Loan Sales Agent for Indian loan products.
    
    Activated by Master/Orchestrator Agent and assumes full control
    of the conversation once routed.
    
    Features:
    - Adaptive persuasion and micro-questions
    - Education mode for financial literacy
    - RAG integration for accurate bank policy information
    """
    
    def __init__(self, enable_rag: bool = True, rag_config: Optional[Any] = None):
        """
        Initialize Loan Sales Agent.
        
        Args:
            enable_rag: Whether to enable RAG for bank info retrieval
            rag_config: Optional RAGConfig for customization
        """
        self.user_context = UserContext()
        self.user_analysis = UserAnalysis()
        self.current_mode = AgentMode.SALES
        self.conversation_stage = "greeting"
        self.pending_questions: List[str] = []
        
        # RAG Integration
        self.rag_enabled = enable_rag and RAG_AVAILABLE
        self.rag_retriever: Optional[Any] = None
        self.last_citations: List[str] = []
        
        if self.rag_enabled:
            try:
                config = rag_config or (RAGConfig() if RAGConfig else None)
                self.rag_retriever = RAGRetriever(config) if RAGRetriever else None
                print("✅ RAG enabled for LoanSalesAgent")
            except Exception as e:
                print(f"⚠️ RAG initialization failed: {e}. Falling back to static data.")
                self.rag_enabled = False
        else:
            if not RAG_AVAILABLE:
                print("ℹ️ RAG not available. Using static loan data.")
        
    # -------------------------------------------------------------------------
    # Core Response Generation
    # -------------------------------------------------------------------------
    
    def process_message(self, user_message: str) -> str:
        """
        Main entry point for processing user messages.
        
        Args:
            user_message: The user's input message
            
        Returns:
            Agent's response string
        """
        # Store in conversation history
        self.user_context.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Analyze user's communication style
        self._analyze_user_style(user_message)
        
        # Check for mode switches
        self._check_mode_switch(user_message)
        
        # Check for hesitation
        if self._detect_hesitation(user_message):
            response = self._handle_hesitation(user_message)
        # Check for fast-track eligibility
        elif self._detect_fast_track(user_message):
            response = self._handle_fast_track(user_message)
        # Process based on current stage
        else:
            response = self._generate_contextual_response(user_message)
        
        # Store agent response
        self.user_context.conversation_history.append({
            "role": "agent",
            "content": response
        })
        
        return response
    
    # -------------------------------------------------------------------------
    # User Analysis Pipeline
    # -------------------------------------------------------------------------
    
    def _analyze_user_style(self, message: str) -> None:
        """
        Analyze user's tone, sentiment, and financial literacy before every response.
        Updates self.user_analysis.
        """
        message_lower = message.lower()
        
        # Tone detection
        formal_indicators = ["kindly", "please", "would you", "could you", "i would like", "i wish to"]
        casual_indicators = ["hey", "hi", "ya", "yeah", "cool", "awesome", "gonna", "wanna"]
        
        if any(indicator in message_lower for indicator in formal_indicators):
            self.user_analysis.tone = Tone.FORMAL
        elif any(indicator in message_lower for indicator in casual_indicators):
            self.user_analysis.tone = Tone.CASUAL
        else:
            self.user_analysis.tone = Tone.NEUTRAL
        
        # Sentiment detection
        positive_words = ["great", "good", "interested", "yes", "sure", "perfect", "excellent"]
        skeptical_words = ["not sure", "doubt", "risky", "scam", "hidden", "catch", "trust"]
        hesitant_words = ["maybe", "perhaps", "later", "thinking", "consider"]
        
        if any(word in message_lower for word in skeptical_words):
            self.user_analysis.sentiment = Sentiment.SKEPTICAL
        elif any(word in message_lower for word in hesitant_words):
            self.user_analysis.sentiment = Sentiment.HESITANT
        elif any(word in message_lower for word in positive_words):
            self.user_analysis.sentiment = Sentiment.POSITIVE
        else:
            self.user_analysis.sentiment = Sentiment.NEUTRAL
        
        # Financial literacy detection
        high_literacy_terms = ["emi", "mclr", "repo rate", "floating", "fixed rate", 
                               "collateral", "moratorium", "amortization", "ltv", "cibil"]
        low_literacy_indicators = ["what is", "what does", "confused", "don't understand",
                                    "explain", "simple terms"]
        
        if any(term in message_lower for term in high_literacy_terms):
            self.user_analysis.financial_literacy = FinancialLiteracy.HIGH
        elif any(indicator in message_lower for indicator in low_literacy_indicators):
            self.user_analysis.financial_literacy = FinancialLiteracy.LOW
        # Otherwise keep current assessment
    
    def _check_mode_switch(self, message: str) -> None:
        """Check if we should switch to education mode."""
        message_lower = message.lower()
        
        if any(phrase in message_lower for phrase in EDUCATION_TRIGGER_PHRASES):
            self.current_mode = AgentMode.EDUCATION
        elif self.current_mode == AgentMode.EDUCATION:
            # Check if user seems satisfied with explanation
            if any(word in message_lower for word in ["thanks", "got it", "understand", "clear", "okay"]):
                self.current_mode = AgentMode.SALES
    
    # -------------------------------------------------------------------------
    # Detection Methods
    # -------------------------------------------------------------------------
    
    def _detect_hesitation(self, message: str) -> bool:
        """Detect if user is showing hesitation."""
        message_lower = message.lower()
        return any(phrase in message_lower for phrase in HESITATION_PHRASES)
    
    def _detect_fast_track(self, message: str) -> bool:
        """Detect if user is showing high trust/confidence."""
        message_lower = message.lower()
        
        # Quick, confident responses indicate fast-track eligibility
        if len(message.split()) <= 5 and any(indicator in message_lower for indicator in FAST_TRACK_INDICATORS):
            self.user_context.fast_track_eligible = True
            self.user_context.update_trust_score(15)
            return True
        return False
    
    def _detect_loan_type(self, message: str) -> Optional[LoanType]:
        """Detect which type of loan the user is interested in."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["education", "study", "college", "university", "abroad studies", "mba", "course"]):
            return LoanType.EDUCATION
        elif any(word in message_lower for word in ["home", "house", "flat", "property", "apartment"]):
            return LoanType.HOME
        elif any(word in message_lower for word in ["personal", "emergency", "wedding", "medical"]):
            return LoanType.PERSONAL
        elif any(word in message_lower for word in ["car", "vehicle", "bike", "auto"]):
            return LoanType.VEHICLE
        elif any(word in message_lower for word in ["business", "startup", "shop", "working capital"]):
            return LoanType.BUSINESS
        
        return None
    
    def _detect_bank_name(self, message: str) -> Optional[str]:
        """Detect if user mentions a specific bank name."""
        message_lower = message.lower()
        
        # Major Indian banks and NBFCs
        banks = {
            "sbi": "SBI",
            "state bank": "SBI",
            "hdfc": "HDFC",
            "icici": "ICICI",
            "axis": "Axis Bank",
            "pnb": "PNB",
            "punjab national": "PNB",
            "bank of baroda": "Bank of Baroda",
            "bob": "Bank of Baroda",
            "canara": "Canara Bank",
            "union bank": "Union Bank",
            "idbi": "IDBI",
            "kotak": "Kotak Mahindra",
            "yes bank": "Yes Bank",
            "indusind": "IndusInd",
            "federal bank": "Federal Bank",
            "idfc": "IDFC First",
            "bajaj": "Bajaj Finserv",
            "tata capital": "Tata Capital",
            "credila": "HDFC Credila",
            "avanse": "Avanse",
            "incred": "InCred"
        }
        
        for keyword, bank_name in banks.items():
            if keyword in message_lower:
                return bank_name
        
        return None
    
    # -------------------------------------------------------------------------
    # Response Handlers
    # -------------------------------------------------------------------------
    
    def _handle_hesitation(self, message: str) -> str:
        """Handle user hesitation with empathy and reassurance."""
        self.user_context.add_objection(message)
        
        tone_key = self.user_analysis.tone.value if self.user_analysis.tone != Tone.NEUTRAL else "standard"
        no_pressure = MICROCOPY["no_pressure"].get(tone_key, MICROCOPY["no_pressure"]["standard"])
        
        responses = [
            f"Totally get it — big loan decisions feel risky. {no_pressure}",
            f"Many people pause here because they don't want hidden surprises. I'm here just to give you clarity, nothing more.",
            f"Completely understand! Would you prefer I just explain how these loans work first, so you can decide later?",
            f"No worries at all. Tell you what — would you like me to notify you if there are any better offers next month?"
        ]
        
        # Choose response based on sentiment
        if self.user_analysis.sentiment == Sentiment.SKEPTICAL:
            return responses[1]  # Address hidden surprises concern
        elif "later" in message.lower():
            return responses[3]  # Offer re-entry path
        else:
            return responses[0]  # General reassurance
    
    def _handle_fast_track(self, message: str) -> str:
        """Handle high-trust users with direct CTAs."""
        if self.user_context.loan_type:
            return f"Perfect! Shall we check eligibility and shortlist the best banks for your {self.user_context.loan_type.value} loan now? Takes just a minute."
        else:
            return "Great! Let's move forward. To find you the best options — is this for education, home, personal, vehicle, or business needs?"
    
    def _generate_contextual_response(self, message: str) -> str:
        """Generate response based on conversation context and stage."""
        
        # Check for loan type mention
        detected_loan_type = self._detect_loan_type(message)
        if detected_loan_type:
            self.user_context.loan_type = detected_loan_type
            # Use RAG-powered response if available
            if self.rag_enabled:
                return self._present_loan_options_with_rag(detected_loan_type)
            return self._present_loan_options(detected_loan_type)
        
        # Check for specific bank inquiry
        bank_name = self._detect_bank_name(message)
        if bank_name and self.rag_enabled:
            return self.get_specific_bank_info(bank_name)
        
        # Education mode response - use RAG for better answers
        if self.current_mode == AgentMode.EDUCATION:
            if self.rag_enabled:
                return self.answer_with_rag(message)
            return self._generate_educational_response(message)
        
        # Extract information from message
        self._extract_user_info(message)
        
        # Conversation flow based on stage
        if self.conversation_stage == "greeting":
            return self._greeting_response()
        elif self.conversation_stage == "discovery":
            return self._discovery_response()
        elif self.conversation_stage == "recommendation":
            return self._recommendation_response()
        elif self.conversation_stage == "commitment":
            return self._commitment_response()
        
        # Default: Ask clarifying question
        return self._ask_micro_question()
    
    def _greeting_response(self) -> str:
        """Initial greeting and purpose establishment."""
        self.conversation_stage = "discovery"
        
        greetings = {
            Tone.CASUAL: "Hey there! 👋 Looking for a loan? I'm here to help you find the best options. What kind of loan are you exploring?",
            Tone.FORMAL: "Good day! I'm here to assist you in finding the most suitable loan options. May I know what type of loan you're considering?",
            Tone.NEUTRAL: "Hello! I'm here to help you explore loan options. What type of loan are you interested in — education, home, personal, vehicle, or business?"
        }
        
        return greetings.get(self.user_analysis.tone, greetings[Tone.NEUTRAL])
    
    def _discovery_response(self) -> str:
        """Gather information through micro-questions."""
        return self._ask_micro_question()
    
    def _recommendation_response(self) -> str:
        """Provide personalized recommendations."""
        if self.user_context.loan_type:
            return self._present_loan_options(self.user_context.loan_type)
        return self._ask_micro_question()
    
    def _commitment_response(self) -> str:
        """Guide towards small, voluntary commitments."""
        tone_key = self.user_analysis.tone.value if self.user_analysis.tone != Tone.NEUTRAL else "standard"
        eligibility_cta = MICROCOPY["check_eligibility"].get(tone_key, MICROCOPY["check_eligibility"]["standard"])
        
        return f"Based on what you've shared, I think I can find you some great options. {eligibility_cta}"
    
    # -------------------------------------------------------------------------
    # Micro-Questions (Time-Respectful)
    # -------------------------------------------------------------------------
    
    def _ask_micro_question(self) -> str:
        """Ask short, natural questions one at a time."""
        
        # Determine what information we're missing
        if not self.user_context.loan_type:
            return "What type of loan are you looking for — education, home, personal, vehicle, or business?"
        
        if not self.user_context.profession:
            justification = "This helps me understand which lenders would be the best fit for you."
            if self.user_analysis.tone == Tone.CASUAL:
                return f"Quick one — what do you do for work? {justification}"
            elif self.user_analysis.tone == Tone.FORMAL:
                return f"May I ask about your profession? {justification}"
            return f"Can I ask what you do for a living? {justification}"
        
        if not self.user_context.monthly_income:
            tone_key = self.user_analysis.tone.value if self.user_analysis.tone != Tone.NEUTRAL else "standard"
            return MICROCOPY["ask_income"].get(tone_key, MICROCOPY["ask_income"]["standard"])
        
        if self.user_context.loan_type == LoanType.EDUCATION and not self.user_context.study_destination:
            return "Is this loan for studies in India or abroad? This affects which schemes you can access."
        
        # All basic info collected, move to commitment stage
        self.conversation_stage = "commitment"
        return self._commitment_response()
    
    # -------------------------------------------------------------------------
    # Product Discovery & Comparison
    # -------------------------------------------------------------------------
    
    def _present_loan_options(self, loan_type: LoanType) -> str:
        """Present loan schemes with gradual information layering."""
        products = LOAN_PRODUCTS.get(loan_type, [])
        
        if not products:
            return f"I'd be happy to help you explore {loan_type.value} loans. Let me gather some basic information first to give you personalized recommendations."
        
        intro = self._get_loan_intro(loan_type)
        
        response_parts = [
            intro,
            "\nLet me give you a clear picture first, then we'll narrow it down together.\n"
        ]
        
        for i, product in enumerate(products, 1):
            response_parts.append(f"\n**Option {i}: {product.name}**")
            response_parts.append(f"• Interest Type: {product.interest_type}")
            response_parts.append(f"• Typical Tenure: {product.typical_tenure}")
            if product.moratorium:
                response_parts.append(f"• Moratorium: {product.moratorium}")
            response_parts.append(f"• Repayment: {product.repayment_structure}")
        
        response_parts.append("\nWould you like me to break down the pros and cons of each option?")
        
        self.conversation_stage = "discovery"
        return "\n".join(response_parts)
    
    def _get_loan_intro(self, loan_type: LoanType) -> str:
        """Get appropriate introduction based on loan type and user context."""
        intros = {
            LoanType.EDUCATION: "Great choice! Education loans in India have some really helpful features. Here's what's available:",
            LoanType.HOME: "Home loans are a big decision, but also one of the most tax-efficient loans. Here's an overview:",
            LoanType.PERSONAL: "Personal loans offer flexibility with minimal paperwork. Here's what you should know:",
            LoanType.VEHICLE: "Vehicle loans typically offer competitive rates since the vehicle acts as security. Here's a quick overview:",
            LoanType.BUSINESS: "Business loans can really accelerate your growth. Let me show you the options:"
        }
        return intros.get(loan_type, "Let me show you the available options:")
    
    def present_comparison(self) -> str:
        """Present detailed comparison with advantages and disadvantages."""
        if not self.user_context.loan_type:
            return "Which loan type would you like me to compare options for?"
        
        products = LOAN_PRODUCTS.get(self.user_context.loan_type, [])
        
        if not products:
            return "I don't have detailed comparison data for this loan type yet."
        
        response_parts = ["Here's a detailed comparison:\n"]
        
        for product in products:
            response_parts.append(f"\n**{product.name}**\n")
            
            response_parts.append("✅ Advantages:")
            for adv in product.advantages:
                response_parts.append(f"  • {adv}")
            
            response_parts.append("\n⚠️ Points to Consider:")
            for disadv in product.disadvantages:
                response_parts.append(f"  • {disadv}")
            
            response_parts.append("")  # Empty line between products
        
        response_parts.append("\nWhich aspects matter most to you? This will help me suggest the best fit.")
        
        return "\n".join(response_parts)
    
    # -------------------------------------------------------------------------
    # RAG-Powered Bank Information Retrieval
    # -------------------------------------------------------------------------
    
    def get_bank_info_with_rag(self, query: str, bank_name: Optional[str] = None) -> Tuple[str, List[str]]:
        """
        Retrieve bank information using RAG with citations.
        
        Args:
            query: The question or topic to search for
            bank_name: Optional specific bank to filter by
            
        Returns:
            Tuple of (formatted_response, list_of_citations)
        """
        if not self.rag_enabled or not self.rag_retriever:
            return "", []
        
        try:
            # Build search query
            search_query = query
            if bank_name:
                search_query = f"{bank_name} {query}"
            if self.user_context.loan_type:
                search_query = f"{self.user_context.loan_type.value} loan {search_query}"
            
            # Retrieve with context and citations
            context, citations = self.rag_retriever.retrieve_with_context(search_query, top_k=3)
            
            self.last_citations = citations
            return context, citations
            
        except Exception as e:
            print(f"⚠️ RAG retrieval error: {e}")
            return "", []
    
    def _present_loan_options_with_rag(self, loan_type: LoanType) -> str:
        """Present loan options using RAG retrieval for accurate bank data."""
        intro = self._get_loan_intro(loan_type)
        
        # Try to get RAG-powered info
        query = f"{loan_type.value} loan interest rate eligibility features"
        context, citations = self.get_bank_info_with_rag(query)
        
        if context:
            response_parts = [
                intro,
                "\nLet me give you a clear picture based on current bank policies:\n",
                context,
                "\n\n📌 **Sources:**"
            ]
            for cite in citations[:3]:  # Limit to top 3 citations
                response_parts.append(f"  {cite}")
            
            response_parts.append("\nWould you like me to compare specific banks or explain any terms?")
            
            self.conversation_stage = "discovery"
            return "\n".join(response_parts)
        else:
            # Fall back to static data
            return self._present_loan_options(loan_type)
    
    def get_specific_bank_info(self, bank_name: str, info_type: str = "all") -> str:
        """
        Get information about a specific bank's loan offerings.
        
        Args:
            bank_name: Name of the bank (e.g., "SBI", "HDFC")
            info_type: Type of info - "interest", "eligibility", "features", "all"
            
        Returns:
            Formatted bank information with citations
        """
        if not self.rag_enabled:
            return f"For the most accurate information about {bank_name}, please visit their official website or nearest branch."
        
        loan_type_str = self.user_context.loan_type.value if self.user_context.loan_type else "loan"
        
        queries = {
            "interest": f"{bank_name} {loan_type_str} loan interest rate",
            "eligibility": f"{bank_name} {loan_type_str} loan eligibility criteria requirements",
            "features": f"{bank_name} {loan_type_str} loan features tenure repayment",
            "all": f"{bank_name} {loan_type_str} loan details interest eligibility features"
        }
        
        query = queries.get(info_type, queries["all"])
        context, citations = self.get_bank_info_with_rag(query, bank_name)
        
        if context:
            response = f"Here's what I found about **{bank_name}** {loan_type_str} loan:\n\n"
            response += context
            
            if citations:
                response += "\n\n📌 **Source:** " + citations[0]
            
            return response
        else:
            return f"I don't have detailed information about {bank_name} {loan_type_str} loans in my knowledge base yet. Please check their official website for the latest details."
    
    def compare_banks_with_rag(self, bank_names: List[str]) -> str:
        """
        Compare multiple banks using RAG retrieval.
        
        Args:
            bank_names: List of bank names to compare
            
        Returns:
            Formatted comparison with citations
        """
        if not self.rag_enabled:
            return self.present_comparison()
        
        loan_type_str = self.user_context.loan_type.value if self.user_context.loan_type else "loan"
        
        response_parts = [f"## Comparing {', '.join(bank_names)} for {loan_type_str.title()} Loans\n"]
        all_citations = []
        
        for bank in bank_names:
            query = f"{bank} {loan_type_str} loan interest rate eligibility tenure"
            context, citations = self.get_bank_info_with_rag(query, bank)
            
            if context:
                response_parts.append(f"\n### {bank}\n")
                # Take only first 300 chars of context per bank for readability
                response_parts.append(context[:500] + "..." if len(context) > 500 else context)
                all_citations.extend(citations)
        
        if all_citations:
            response_parts.append("\n\n📌 **Sources:**")
            for cite in list(set(all_citations))[:5]:  # Unique citations, max 5
                response_parts.append(f"  {cite}")
        
        response_parts.append("\n\nWhich bank would you like to know more about?")
        
        return "\n".join(response_parts)
    
    def answer_with_rag(self, question: str) -> str:
        """
        Answer any loan-related question using RAG.
        
        Args:
            question: User's question
            
        Returns:
            RAG-powered answer with citations
        """
        if not self.rag_enabled:
            return self._generate_educational_response(question)
        
        # Add context from user profile
        enhanced_query = question
        if self.user_context.loan_type:
            enhanced_query = f"{self.user_context.loan_type.value} loan {question}"
        
        context, citations = self.get_bank_info_with_rag(enhanced_query)
        
        if context:
            # Format response based on user's financial literacy
            if self.user_analysis.financial_literacy == FinancialLiteracy.LOW:
                response = "Let me explain that in simple terms:\n\n"
            else:
                response = "Based on available information:\n\n"
            
            response += context
            
            if citations:
                response += "\n\n📌 *" + citations[0] + "*"
            
            response += "\n\nDoes that answer your question? Want me to clarify anything?"
            return response
        else:
            # Fall back to static educational response
            return self._generate_educational_response(question)
    
    # -------------------------------------------------------------------------
    # Education Mode
    # -------------------------------------------------------------------------
    
    def _generate_educational_response(self, message: str) -> str:
        """Generate educational content without selling."""
        message_lower = message.lower()
        
        # Financial term explanations
        explanations = {
            "emi": """
**EMI (Equated Monthly Installment)** is the fixed amount you pay every month to repay your loan.

Think of it like a subscription — same amount, same date, every month until the loan is paid off.

EMI consists of two parts:
• **Principal**: The actual loan amount you're paying back
• **Interest**: The cost of borrowing

In the beginning, more of your EMI goes toward interest. Over time, more goes toward principal.

Does that make things clearer? Want me to apply this to your case?""",
            
            "mclr": """
**MCLR (Marginal Cost of Funds based Lending Rate)** is a benchmark rate banks use to set loan interest rates.

In simple terms: When MCLR goes down, your loan interest rate typically goes down too (for floating rate loans).

This is why floating rate loans can be beneficial when interest rates are expected to fall.

Does this help? Would you like to know how this affects your specific situation?""",
            
            "moratorium": """
**Moratorium** is a break period where you don't have to pay EMIs.

For education loans, this typically means:
• No payments during your course
• No payments for 6-12 months after course completion
• EMI starts only after you get a job

It's like a "payment holiday" to give you time to settle in.

Does that clarify things? Want me to show you which banks offer the best moratorium terms?""",
            
            "floating": """
**Floating Rate** means your interest rate can change over the loan tenure.

It moves up or down based on:
• RBI's repo rate
• Bank's MCLR/RLLR

**Advantage**: You benefit when rates fall
**Consideration**: EMI may increase if rates rise

**Fixed Rate** stays the same throughout — predictable but usually slightly higher initially.

Would you prefer stability or the chance to benefit from rate cuts?""",
            
            "collateral": """
**Collateral** is an asset you pledge as security for the loan.

Common examples:
• For home loan: The property itself
• For education loan (higher amounts): Property, FD, LIC policy

If you can't repay, the bank can take this asset.

**Good news**: Many loans don't require collateral up to certain limits. For example, education loans up to ₹7.5 lakh often don't need collateral.

Does this answer your question?"""
        }
        
        # Find matching explanation
        for term, explanation in explanations.items():
            if term in message_lower:
                return explanation
        
        # General educational response
        return """I'd be happy to explain! Could you tell me specifically which term or concept you'd like me to clarify?

Common terms I can explain:
• EMI (monthly payment)
• Interest types (fixed vs floating)
• Moratorium (payment break)
• Collateral (security)
• Processing fees

Just ask about any of these, or something else entirely!"""
    
    # -------------------------------------------------------------------------
    # Information Extraction
    # -------------------------------------------------------------------------
    
    def _extract_user_info(self, message: str) -> None:
        """Extract and store user information from message."""
        message_lower = message.lower()
        
        # Profession extraction
        profession_patterns = [
            r"i am a (\w+)",
            r"i'm a (\w+)",
            r"i work as (\w+)",
            r"working as (\w+)",
            r"i do (\w+)",
            r"(\w+) professional",
            r"(\w+) by profession"
        ]
        
        for pattern in profession_patterns:
            match = re.search(pattern, message_lower)
            if match:
                self.user_context.profession = match.group(1).title()
                self.user_context.update_trust_score(10)
                break
        
        # Income extraction (looking for numbers with lakh/k patterns)
        income_patterns = [
            r"(\d+)\s*(?:lakh|lac|l)\s*(?:per\s*)?(?:month|monthly)?",
            r"(\d+)\s*k\s*(?:per\s*)?(?:month|monthly)?",
            r"(?:around|about|approximately)?\s*(\d+)",
        ]
        
        for pattern in income_patterns:
            match = re.search(pattern, message_lower)
            if match:
                self.user_context.monthly_income = match.group(1)
                self.user_context.update_trust_score(10)
                break
        
        # Study destination (for education loans)
        if "abroad" in message_lower or "foreign" in message_lower or "usa" in message_lower or "uk" in message_lower:
            self.user_context.study_destination = "abroad"
        elif "india" in message_lower or "domestic" in message_lower:
            self.user_context.study_destination = "india"
    
    # -------------------------------------------------------------------------
    # Social Proof & Personalization
    # -------------------------------------------------------------------------
    
    def get_social_proof(self) -> str:
        """Generate contextual social proof based on user profile."""
        if self.user_context.profession:
            return f"Most {self.user_context.profession.lower()}s with a similar profile prefer options that offer flexibility in repayment."
        
        if self.user_context.loan_type == LoanType.EDUCATION:
            if self.user_context.study_destination == "abroad":
                return "Students going abroad usually prefer banks that offer higher loan limits and forex facilities."
            return "Most students looking for education loans prioritize banks with longer moratorium periods."
        
        return "Based on similar profiles, most people find value in comparing at least 2-3 options before deciding."
    
    def reflect_past_context(self) -> str:
        """Reflect back on information shared earlier."""
        reflections = []
        
        if self.user_context.profession:
            reflections.append(f"your profession as a {self.user_context.profession}")
        
        if self.user_context.past_objections:
            reflections.append("your earlier concern about " + self.user_context.past_objections[-1])
        
        if reflections:
            return f"Keeping in mind {' and '.join(reflections)}, "
        
        return ""
    
    # -------------------------------------------------------------------------
    # Commitment Ladder
    # -------------------------------------------------------------------------
    
    def offer_commitment_options(self) -> str:
        """Offer small, reversible actions."""
        tone_key = self.user_analysis.tone.value if self.user_analysis.tone != Tone.NEUTRAL else "standard"
        
        options = [
            f"1️⃣ {MICROCOPY['check_eligibility'].get(tone_key, MICROCOPY['check_eligibility']['standard'])}",
            "2️⃣ See your approximate loan amount you could get",
            "3️⃣ Compare the best options — no application yet"
        ]
        
        prefix = self.reflect_past_context()
        
        return f"""{prefix}Here are some quick things we can do:

{chr(10).join(options)}

Which sounds good to you? Or would you prefer something else?"""
    
    # -------------------------------------------------------------------------
    # Public API Methods
    # -------------------------------------------------------------------------
    
    def start_conversation(self) -> str:
        """Initialize and return greeting message."""
        self.conversation_stage = "greeting"
        return self._greeting_response()
    
    def reset(self) -> None:
        """Reset agent state for new conversation."""
        self.user_context = UserContext()
        self.user_analysis = UserAnalysis()
        self.current_mode = AgentMode.SALES
        self.conversation_stage = "greeting"
        self.pending_questions = []
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of the current session."""
        return {
            "loan_type": self.user_context.loan_type.value if self.user_context.loan_type else None,
            "profession": self.user_context.profession,
            "monthly_income": self.user_context.monthly_income,
            "trust_score": self.user_context.trust_score,
            "fast_track_eligible": self.user_context.fast_track_eligible,
            "current_mode": self.current_mode.value,
            "conversation_stage": self.conversation_stage,
            "messages_exchanged": len(self.user_context.conversation_history)
        }
    
    def was_session_successful(self) -> Dict[str, Any]:
        """
        Determine if the session was successful.
        Success = any voluntary action or education provided.
        """
        actions_taken = []
        
        if self.user_context.loan_type:
            actions_taken.append("loan_type_identified")
        
        if self.user_context.profession or self.user_context.monthly_income:
            actions_taken.append("user_info_collected")
        
        if self.user_context.trust_score > 30:
            actions_taken.append("trust_established")
        
        if self.current_mode == AgentMode.EDUCATION or any(
            "explain" in msg.get("content", "").lower() 
            for msg in self.user_context.conversation_history 
            if msg.get("role") == "agent"
        ):
            actions_taken.append("education_provided")
        
        return {
            "successful": len(actions_taken) > 0,
            "actions": actions_taken,
            "trust_score": self.user_context.trust_score
        }


# ============================================================================
# INTEGRATION HELPER FUNCTIONS
# ============================================================================

def create_agent(enable_rag: bool = True) -> LoanSalesAgent:
    """
    Factory function to create a new LoanSalesAgent instance.
    
    Args:
        enable_rag: Whether to enable RAG for bank info retrieval
        
    Returns:
        Configured LoanSalesAgent instance
    """
    return LoanSalesAgent(enable_rag=enable_rag)


def create_agent_with_rag_config(config: Any = None) -> LoanSalesAgent:
    """Create agent with custom RAG configuration."""
    return LoanSalesAgent(enable_rag=True, rag_config=config)


def handle_orchestrator_handoff(agent: LoanSalesAgent, initial_context: Dict[str, Any] = None) -> str:
    """
    Handle handoff from Master/Orchestrator Agent.
    
    Args:
        agent: LoanSalesAgent instance
        initial_context: Optional context from orchestrator (e.g., detected loan type)
        
    Returns:
        Initial greeting message
    """
    if initial_context:
        # Apply any context from orchestrator
        if "loan_type" in initial_context:
            try:
                agent.user_context.loan_type = LoanType(initial_context["loan_type"])
            except ValueError:
                pass
        
        if "user_tone" in initial_context:
            try:
                agent.user_analysis.tone = Tone(initial_context["user_tone"])
            except ValueError:
                pass
    
    return agent.start_conversation()


def ingest_bank_documents(docs_dir: str = "./bank_docs") -> bool:
    """
    Helper to ingest bank documents for RAG.
    
    Args:
        docs_dir: Directory containing bank documents
        
    Returns:
        True if successful, False otherwise
    """
    if not RAG_AVAILABLE:
        print("❌ RAG not available. Install: pip install sentence-transformers chromadb")
        return False
    
    try:
        from rag_engine import RAGRetriever
        rag = RAGRetriever()
        rag.ingest_directory(docs_dir)
        return True
    except Exception as e:
        print(f"❌ Error ingesting documents: {e}")
        return False


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("LOAN SALES AGENT - DEMO CONVERSATION")
    print("=" * 60)
    
    # Check for --no-rag flag
    enable_rag = "--no-rag" not in sys.argv
    
    # Create agent
    print(f"\n🔧 Creating agent (RAG {'enabled' if enable_rag else 'disabled'})...")
    agent = create_agent(enable_rag=enable_rag)
    
    # If RAG is enabled, try to ingest sample data
    if agent.rag_enabled:
        print("\n📥 Checking for bank documents to ingest...")
        if agent.rag_retriever:
            try:
                agent.rag_retriever.ingest_directory("./bank_docs")
            except Exception as e:
                print(f"⚠️ Could not ingest documents: {e}")
    
    # Start conversation
    greeting = agent.start_conversation()
    print(f"\n🤖 Agent: {greeting}")
    
    # Simulate user messages
    demo_messages = [
        "Hi, I'm looking for an education loan",
        "What's SBI's interest rate for education loan?",
        "Compare SBI and HDFC for me",
        "What does moratorium mean?",
        "Got it, thanks! Let's check eligibility"
    ]
    
    for user_msg in demo_messages:
        print(f"\n👤 User: {user_msg}")
        response = agent.process_message(user_msg)
        print(f"\n🤖 Agent: {response}")
        print("-" * 40)
    
    # Show session summary
    print("\n" + "=" * 60)
    print("SESSION SUMMARY")
    print("=" * 60)
    summary = agent.get_session_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Show RAG status
    print(f"\n  RAG Enabled: {agent.rag_enabled}")
    if agent.last_citations:
        print(f"  Last Citations: {len(agent.last_citations)}")
    
    success = agent.was_session_successful()
    print(f"\n  Session Successful: {success['successful']}")
    print(f"  Actions Taken: {', '.join(success['actions'])}")

    # ============================================================================
# MASTER AGENT ENTRY POINT
# ============================================================================

# Single instance (session-based can be expanded later)
# _sales_agent_instance = LoanSalesAgent(enable_rag=True)

# def handle_sales(user_message: str) -> str:
#     """
#     Entry point for Master Agent → Sales Agent.
#     """
#     return _sales_agent_instance.process_message(user_message)
_sales_agent_instance = LoanSalesAgent(enable_rag=True)

def handle_sales(user_message: str) -> dict:
    """
    Entry point for Master Agent → Sales Agent.
    Always return structured JSON.
    """
    sales_text = _sales_agent_instance.process_message(user_message)

    return {
        "message": sales_text,
        "signals": {
            "ready_for_underwriting": True
        }
    }



