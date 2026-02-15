# Dhanit Banking System - Risk Assumptions & Transparency

## 1. Credit Risk Assumptions

### 1.1 Credit Score Thresholds

#### Bank-Specific Minimum Scores
| Bank | Education | Home | Personal | Vehicle | Business |
|------|-----------|------|----------|---------|----------|
| SBI | 650 | 700 | 675 | 650 | 675 |
| HDFC | 675 | 725 | 700 | 675 | 700 |
| ICICI | 650 | 700 | 675 | 650 | 675 |
| Axis | 675 | 725 | 700 | 675 | 700 |

#### Score Interpretation
- **750+**: Excellent - Auto-approve eligible, best rates
- **700-749**: Good - Standard approval, competitive rates
- **650-699**: Fair - Conditional approval, higher rates
- **<650**: Poor - Likely rejection or require co-applicant
- **No History**: First-time borrowers - Evaluated on income and employment

**Assumption Rationale**: Based on industry standards and public bank documentation. Actual thresholds may vary based on bank's risk appetite and market conditions.

### 1.2 FOIR (Fixed Obligations to Income Ratio) Limits

#### Bank-Specific FOIR Caps
| Bank | Salaried | Self-Employed | Business |
|------|----------|---------------|----------|
| SBI | 50% | 45% | 40% |
| HDFC | 55% | 50% | 45% |
| ICICI | 50% | 45% | 40% |
| Axis | 55% | 50% | 45% |

**Formula**: FOIR = (Existing EMIs + Proposed EMI) / Net Monthly Income

**Example Calculation**:
- Net Monthly Income: ₹50,000
- Existing EMIs: ₹10,000
- Proposed EMI: ₹15,000
- FOIR = (₹10,000 + ₹15,000) / ₹50,000 = 50%

**Assumption Rationale**: Conservative estimates based on RBI guidelines and bank practices. Actual limits may be higher for premium customers or lower during tight credit conditions.

### 1.3 Loan-to-Value (LTV) Ratios

#### Home Loans
| Loan Amount | LTV Ratio | Down Payment |
|-------------|-----------|--------------|
| Up to ₹30 lakh | 90% | 10% |
| ₹30-75 lakh | 80% | 20% |
| Above ₹75 lakh | 75% | 25% |

#### Vehicle Loans
| Vehicle Type | LTV Ratio |
|--------------|-----------|
| New Car | 90-95% |
| Used Car | 80-85% |
| Two-Wheeler | 90-95% |
| Commercial Vehicle | 70-80% |

#### Gold Loans
| Gold Purity | LTV Ratio |
|-------------|-----------|
| 22K | 75% |
| 18K | 70% |

**Assumption Rationale**: Based on RBI LTV norms and standard bank practices. Actual LTV may vary based on property location, vehicle age, and market conditions.

### 1.4 Income Multiplier Limits

#### Personal Loans
- **Salaried**: 20-24x monthly net income
- **Self-Employed**: 15-20x monthly net income
- **Business**: 12-18x monthly net income

**Example**:
- Monthly Income: ₹50,000
- Maximum Personal Loan: ₹50,000 × 24 = ₹12,00,000

#### Education Loans
- **Domestic**: Up to ₹50 lakh (no income multiplier, based on course and institution)
- **International**: Up to ₹1.5 crore (co-applicant income considered)

**Assumption Rationale**: Industry-standard multipliers. Actual limits depend on credit profile, existing obligations, and bank policies.

## 2. Interest Rate Assumptions

### 2.1 Indicative Interest Rate Ranges

#### By Loan Type (Annual Percentage Rate)
| Loan Type | Minimum | Maximum | Typical |
|-----------|---------|---------|---------|
| Education (Domestic) | 8.50% | 11.50% | 9.50% |
| Education (International) | 9.00% | 12.00% | 10.50% |
| Home Loan | 8.00% | 10.50% | 8.75% |
| Personal Loan | 10.50% | 18.00% | 14.00% |
| Vehicle Loan | 8.50% | 12.00% | 9.50% |
| Business Loan | 9.00% | 14.00% | 11.00% |
| Gold Loan | 7.50% | 10.00% | 8.50% |

#### Rate Determinants
- **Credit Score**: Higher score = lower rate
- **Loan Amount**: Larger loans may get better rates
- **Tenure**: Longer tenure may have higher rates
- **Employment Type**: Salaried typically get better rates
- **Existing Customer**: Relationship discount (0.25-0.50%)
- **Gender**: Some banks offer concessions for women borrowers
- **Collateral**: Secured loans have lower rates

**Assumption Rationale**: Rates are indicative ranges based on market conditions as of February 2026. Actual rates are linked to MCLR/RLLR and subject to bank approval. System provides ranges, not exact rates.

### 2.2 Interest Rate Type

| Loan Type | Rate Type | Benchmark |
|-----------|-----------|-----------|
| Education | Floating | RLLR/MCLR |
| Home | Floating | Repo Rate/RLLR |
| Personal | Fixed | Internal Benchmark |
| Vehicle | Fixed/Floating | MCLR |
| Business | Floating | MCLR |

**Floating Rate Reset**: Quarterly or annually based on bank policy

**Assumption Rationale**: Most retail loans in India are floating rate. Personal loans are typically fixed. Actual rate type depends on bank product and customer choice.

## 3. Eligibility Assumptions

### 3.1 Age Criteria

| Loan Type | Minimum Age | Maximum Age at Maturity |
|-----------|-------------|-------------------------|
| Education | 18 years | 65 years (co-applicant) |
| Home | 21 years | 70 years |
| Personal | 21 years | 60 years |
| Vehicle | 21 years | 65 years |
| Business | 21 years | 65 years |

**Assumption Rationale**: Standard industry practice. Some banks may extend upper age limits for salaried employees with pension benefits.

### 3.2 Income Criteria

#### Minimum Monthly Income
| Loan Type | Salaried | Self-Employed | Business |
|-----------|----------|---------------|----------|
| Education | ₹25,000 (co-applicant) | ₹30,000 | ₹40,000 |
| Home | ₹30,000 | ₹40,000 | ₹50,000 |
| Personal | ₹15,000 | ₹20,000 | ₹25,000 |
| Vehicle | ₹20,000 | ₹25,000 | ₹30,000 |
| Business | N/A | ₹50,000 | ₹1,00,000 (turnover) |

**Assumption Rationale**: Conservative estimates. Actual requirements vary by bank and loan amount. Metro cities may have higher thresholds.

### 3.3 Employment Criteria

#### Salaried
- **Minimum Experience**: 2 years total, 1 year with current employer
- **Employment Type**: Permanent/confirmed (probation not eligible)
- **Employer Type**: Reputed companies preferred (PSU, MNC, listed companies)

#### Self-Employed
- **Business Vintage**: 3 years minimum
- **ITR Filing**: Last 2 years mandatory
- **GST Registration**: Required for business loans
- **Profitability**: Positive net income in last 2 years

#### Business
- **Business Vintage**: 3-5 years
- **Annual Turnover**: Minimum ₹10 lakh
- **Udyam Registration**: Required for MSME loans
- **Bank Statements**: 12 months mandatory

**Assumption Rationale**: Standard bank requirements. Some banks may relax criteria for premium customers or specific sectors.

### 3.4 Document Requirements

#### Mandatory Documents
- **Identity**: PAN card, Aadhaar card
- **Address**: Utility bill, rental agreement, Aadhaar
- **Income**: Salary slips (3 months), bank statements (6 months), ITR (2 years)
- **Employment**: Employment letter, offer letter, ID card

#### Loan-Specific Documents
- **Education**: Admission letter, fee structure, collateral documents
- **Home**: Property documents, builder agreement, valuation report
- **Vehicle**: Proforma invoice, insurance quote
- **Business**: Business registration, GST returns, financial statements

**Assumption Rationale**: Standard KYC and income verification requirements as per RBI and bank policies.

## 4. Risk Scoring Assumptions

### 4.1 Risk Score Calculation

**Risk Score Formula** (0-100 scale, lower is better):
```
Risk Score = (Credit Score Weight × Credit Score Factor) +
             (FOIR Weight × FOIR Factor) +
             (Employment Weight × Employment Factor) +
             (Verification Weight × Verification Factor) +
             (AML Weight × AML Factor)
```

#### Weight Distribution
- Credit Score: 35%
- FOIR: 25%
- Employment Stability: 20%
- Verification Confidence: 15%
- AML Score: 5%

#### Factor Calculation
- **Credit Score Factor**: (900 - Credit Score) / 600 × 100
- **FOIR Factor**: FOIR × 100
- **Employment Factor**: Based on type and vintage (0-100)
- **Verification Factor**: (1 - Confidence Score) × 100
- **AML Factor**: AML Risk Score (0-100)

**Example Calculation**:
- Credit Score: 750 → Factor = (900-750)/600×100 = 25
- FOIR: 40% → Factor = 40
- Employment: Salaried, 5 years → Factor = 20
- Verification: 95% confidence → Factor = 5
- AML: Low risk → Factor = 10

Risk Score = (0.35×25) + (0.25×40) + (0.20×20) + (0.15×5) + (0.05×10) = 23.25

#### Risk Level Classification
- **0-25**: Low Risk - Auto-approve eligible
- **26-50**: Medium Risk - Standard approval
- **51-75**: High Risk - Conditional approval or rejection
- **76-100**: Critical Risk - Likely rejection

**Assumption Rationale**: Proprietary risk model based on industry best practices. Actual bank models may use different weights and factors. This is a simplified model for demonstration.

### 4.2 Decision Matrix

| Credit Score | FOIR | Risk Level | Decision |
|--------------|------|------------|----------|
| 750+ | <40% | Low | Auto-Approve |
| 700-749 | <45% | Medium | Approve |
| 650-699 | <50% | Medium-High | Conditional |
| <650 | >50% | High | Reject |

**Conditional Approval Conditions**:
- Co-applicant required
- Higher down payment
- Collateral required
- Reduced loan amount
- Higher interest rate

**Assumption Rationale**: Simplified decision matrix for demonstration. Actual underwriting considers 20+ factors including repayment history, credit utilization, industry type, etc.

## 5. Mocked API Data

### 5.1 PAN Verification API

**Mock Response Structure**:
```json
{
  "verified": true,
  "pan": "ABCDE1234F",
  "name": "John Doe",
  "name_match_score": 0.95,
  "status": "Active",
  "category": "Individual"
}
```

**Test Scenarios**:
- Valid PAN: Returns verified=true
- Invalid PAN: Returns verified=false
- Name mismatch: Returns low name_match_score
- Inactive PAN: Returns status="Inactive"

### 5.2 Aadhaar Verification API

**Mock Response Structure**:
```json
{
  "verified": true,
  "aadhaar": "XXXX-XXXX-1234",
  "name": "John Doe",
  "address": "123 Main St, Mumbai",
  "dob": "1990-01-01",
  "gender": "M"
}
```

**Test Scenarios**:
- Valid Aadhaar + OTP: Returns verified=true
- Invalid OTP: Returns verified=false
- Aadhaar not found: Returns error

### 5.3 Credit Bureau API

**Mock Response Structure**:
```json
{
  "credit_score": 750,
  "score_range": "300-900",
  "total_accounts": 5,
  "active_accounts": 3,
  "overdue_accounts": 0,
  "total_debt": 500000,
  "credit_utilization": 0.35,
  "payment_history": "Excellent",
  "delinquencies_30_days": 0,
  "delinquencies_60_days": 0,
  "delinquencies_90_days": 0,
  "write_offs": 0,
  "settlements": 0
}
```

**Test Scenarios**:
- Excellent profile: Score 750+, no delinquencies
- Good profile: Score 700-749, minor issues
- Fair profile: Score 650-699, some delinquencies
- Poor profile: Score <650, write-offs/settlements
- No history: New to credit

### 5.4 AML Screening API

**Mock Response Structure**:
```json
{
  "blacklisted": false,
  "risk_score": 15,
  "pep_status": false,
  "sanctions_match": false,
  "adverse_media": false,
  "risk_level": "Low"
}
```

**Test Scenarios**:
- Clean profile: risk_score <30, no flags
- Medium risk: risk_score 30-70, minor flags
- High risk: risk_score >70, blacklisted or PEP

**Assumption Rationale**: Mocked data for development and testing. Production system will use real API integrations with proper error handling and retry logic.

## 6. Policy Deviation Handling (OSR)

### 6.1 Acceptable Deviations

#### Minor Deviations (Auto-Approvable)
- Credit score 10-25 points below threshold
- FOIR 5% above limit
- Income 10% below minimum
- Age 2 years above maximum

**Compensating Factors**:
- Existing customer with good history
- Higher down payment
- Co-applicant with strong profile
- Collateral provided

#### Major Deviations (Requires Approval)
- Credit score >25 points below threshold
- FOIR >5% above limit
- Income >10% below minimum
- Multiple minor deviations

**Approval Authority**:
- Minor: Credit Manager
- Major: Regional Credit Head
- Critical: Chief Credit Officer

### 6.2 Non-Negotiable Criteria

❌ **Automatic Rejection**:
- AML blacklist match
- Active write-offs or settlements
- Fraudulent documents
- Age below minimum
- No income proof
- Negative net worth (business loans)

**Assumption Rationale**: Based on standard bank credit policies. Actual deviation limits and approval authorities vary by bank and loan amount.

## 7. Transparency & Limitations

### 7.1 Data Accuracy Disclaimer

⚠️ **Important**: All assumptions in this document are based on:
- Publicly available bank documentation
- Industry best practices
- RBI guidelines as of February 2026
- Market research and analysis

**Actual bank policies may differ** based on:
- Internal risk appetite
- Market conditions
- Regulatory changes
- Customer segment
- Loan amount and type

### 7.2 System Limitations

⚠️ **Decision Support, Not Final Decision**:
- System provides recommendations
- Human oversight required for borderline cases
- Credit officers can override AI decisions
- Complex cases escalated to manual review

⚠️ **Data Dependency**:
- Accuracy depends on external API data
- Document authenticity not guaranteed
- Income verification based on provided documents
- Credit score accuracy depends on bureau data

⚠️ **No Guarantee of Approval**:
- Meeting criteria does not guarantee approval
- Final decision rests with the bank
- Additional verification may be required
- Market conditions may affect approval

### 7.3 Regulatory Compliance

✅ **Compliance Measures**:
- All decisions are explainable and auditable
- Audit trail maintained for 7 years
- Fair lending practices (no discrimination)
- Transparent pricing disclosure
- Customer consent for data processing
- Right to data deletion upon request

---

**Document Version:** 1.0  
**Last Updated:** February 15, 2026  
**Author:** Dhanit Project Team  
**Status:** Risk Assumptions & Transparency  
**Related Documents:** design.md, requirements.md, system_boundaries.md

**Disclaimer**: This document is for demonstration and educational purposes. Actual lending decisions should be made by qualified credit professionals following bank-specific policies and regulatory requirements.
