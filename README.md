# Genai-legal-assistant-sme
GenAI-powered legal assistant for Indian SMEs to analyze contracts, identify risks, and explain clauses in plain language.

# GenAI-Powered Legal Assistant for Indian SMEs

A GenAI-powered legal assistant built to help **small and medium business owners in India** understand complex contracts, identify legal risks, and receive **plain-language explanations and actionable insights**.

> Disclaimer: This tool is for informational purposes only and does not constitute legal advice.

---

## Problem Statement

Indian SMEs frequently sign contracts they do not fully understand due to:
- Complex legal language  
- Lack of affordable legal support  
- Time constraints  

This leads to:
- Unfavourable clauses  
- Excessive liabilities  
- Compliance and legal risks  

---

## Solution Overview

This application allows users to **upload business contracts** and receive:
- Clause-by-clause explanations  
- Risk scoring  
- Identification of unfavourable and ambiguous clauses  
- SME-friendly alternatives  
- Multilingual (English + Hindi) support  

Built using **GenAI + NLP**, the system converts legal jargon into **simple business language**.

---

## Key Features

### Core Legal NLP Tasks
- Contract type classification  
- Clause & sub-clause extraction  
- Named Entity Recognition (Parties, Dates, Locations, Amounts)  
- Obligation vs Right vs Prohibition identification  
- Ambiguity detection & flagging  
- Clause similarity comparison with standard SME-friendly clauses  

### Risk Assessment
- Clause-level risk scoring (Low / Medium / High)  
- Overall contract risk score  
- Detection of:
  - Indemnity clauses  
  - Unilateral termination  
  - Non-compete clauses  
  - Jurisdiction & governing law  
  - Unlimited liability  
  - Ambiguous legal language  

### User-Facing Outputs
- Simplified contract summary  
- Clause-by-clause plain-language explanation  
- Highlighting of unfavourable clauses  
- Suggested safer alternatives  
- Downloadable audit report (JSON)  

---

## Multilingual Support
- English contracts supported directly  
- Hindi contracts are automatically translated to English for analysis  
- All outputs shown in **simple business English**

---

## Tech Stack

- **Frontend:** Streamlit  
- **LLM:** GPT-4 (legal reasoning only)  
- **NLP:** spaCy  
- **PDF Parsing:** PyPDF  
- **Language Detection:** langdetect  
- **Storage:** Local JSON audit logs  

>  No external legal databases, case laws, or APIs used (as per rules)

---

## Repository Structure
genai-legal-assistant-sme/
│
├── app.py # Main Streamlit application
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── .gitignore # Ignored files
├── sample_contracts/ # Test contract PDFs
│ ├── sample_employment_agreement.pdf
│ └── sample_employment_agreement_hindi.pdf
└── audit_logs/ # Generated audit reports (local)


---

## How to Run Locally

```bash
# Clone repository
git clone https://github.com/<your-username>/genai-legal-assistant-sme.git
cd genai-legal-assistant-sme

# Install dependencies
pip install -r requirements.txt

# Add OpenAI API key
Create a .env file:
OPENAI_API_KEY=your_api_key_here

# Run the app
streamlit run app.py


