import streamlit as st
import os
import json
import uuid
import re
from datetime import datetime
from langdetect import detect
from pypdf import PdfReader
import spacy
import openai
from dotenv import load_dotenv

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="GenAI Legal Assistant for Indian SMEs",
    layout="wide"
)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
import spacy
from spacy.cli import download

try:
    nlp = spacy.load("en_core_web_sm")
except:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# -------------------- STANDARD SME TEMPLATES --------------------
STANDARD_CLAUSES = {
    "Termination": "Either party may terminate this agreement by giving reasonable prior written notice without cause.",
    "Indemnity": "Each party shall indemnify the other only for direct losses arising from breach, subject to reasonable limits.",
    "Non-Compete": "The employee shall not engage in competing business during employment only, within reasonable limits.",
    "Jurisdiction": "This agreement shall be governed by Indian law and subject to courts where the company is registered.",
    "Confidentiality": "Confidential information shall not be disclosed during or after employment except as required by law."
}

# -------------------- UTILS --------------------
def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text


def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"


def translate_to_english(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Translate this legal document into English:\n{text}"}],
        temperature=0
    )
    return response["choices"][0]["message"]["content"]


def extract_clauses(text):
    clauses = []
    current_text = ""
    current_number = None

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        match = re.match(r"^(\d+)\s*[\.\)]?\s*(.*)", line)

        if match:
            if current_text:
                clauses.append({"number": current_number, "text": current_text.strip()})
            current_number = match.group(1)
            current_text = line
        else:
            current_text += " " + line

    if current_text:
        clauses.append({"number": current_number, "text": current_text.strip()})

    return clauses


def extract_entities(text):
    doc = nlp(text)
    entities = {"Parties": [], "Dates": [], "Amounts": [], "Locations": []}
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PERSON"]:
            entities["Parties"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["Dates"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["Amounts"].append(ent.text)
        elif ent.label_ in ["GPE", "LOC"]:
            entities["Locations"].append(ent.text)
    return entities


def classify_contract_type(text):
    t = text.lower()
    if "employee" in t and "employer" in t:
        return "Employment Agreement"
    if "service" in t and "fees" in t:
        return "Service Agreement"
    if "vendor" in t or "supply" in t:
        return "Vendor Agreement"
    if "lease" in t or "rent" in t:
        return "Lease Agreement"
    if "partnership" in t:
        return "Partnership Deed"
    return "Unknown / Other"


def obligation_type(clause):
    c = clause.lower()
    if "shall not" in c:
        return "Prohibition"
    if "shall" in c or "must" in c:
        return "Obligation"
    if "may" in c:
        return "Right"
    return "Neutral"


def clause_risk(clause):
    risky_terms = [
        "indemnify", "penalty", "terminate at any time",
        "non-compete", "exclusive", "without limitation",
        "auto-renew", "lock-in", "sole discretion"
    ]
    hits = [t for t in risky_terms if t in clause.lower()]
    if len(hits) >= 2:
        return "High", hits
    elif len(hits) == 1:
        return "Medium", hits
    return "Low", []


def detect_ambiguity(clause):
    ambiguous_terms = [
        "reasonable", "material", "as applicable",
        "from time to time", "best efforts",
        "commercially reasonable", "sole discretion",
        "as required", "as necessary"
    ]
    found = [t for t in ambiguous_terms if t in clause.lower()]
    return (True, found) if found else (False, [])


def identify_clause_category(clause):
    c = clause.lower()
    if "terminate" in c:
        return "Termination"
    if "indemnify" in c:
        return "Indemnity"
    if "non-compete" in c or "competing" in c:
        return "Non-Compete"
    if "jurisdiction" in c or "court" in c:
        return "Jurisdiction"
    if "confidential" in c:
        return "Confidentiality"
    return None


def clause_similarity_score(clause, standard):
    return round(nlp(clause).similarity(nlp(standard)), 2)


def explain_clause(clause):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Explain this clause in simple business language and suggest a safer alternative:\n{clause}"}],
        temperature=0.1
    )
    return response["choices"][0]["message"]["content"]


def generate_contract_summary(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Summarize this contract in simple business English:\n{text[:4000]}"}],
        temperature=0.2
    )
    return response["choices"][0]["message"]["content"]


def save_audit(data):
    os.makedirs("audit_logs", exist_ok=True)
    with open(f"audit_logs/{data['audit_id']}.json", "w") as f:
        json.dump(data, f, indent=2)


# -------------------- UI --------------------
st.title("⚖️ GenAI-Powered Legal Assistant")
st.caption("Indian SMEs • Risk • Ambiguity • Compliance")
st.warning("⚠️ Informational only. Not legal advice.")

uploaded = st.file_uploader("Upload Contract (PDF only)", type=["pdf"])

if uploaded:
    raw_text = extract_pdf_text(uploaded)
    text = translate_to_english(raw_text) if detect_language(raw_text) == "hi" else raw_text

    clauses = extract_clauses(text)
    entities = extract_entities(text)
    contract_type = classify_contract_type(text)

    audit = {
        "audit_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "contract_type": contract_type,
        "entities": entities,
        "clauses": []
    }

    st.subheader("📄 Contract Classification")
    st.success(contract_type)

    st.subheader("📌 Extracted Entities")
    st.json(entities)

    st.subheader("📝 Contract Summary")
    st.write(generate_contract_summary(text))

    st.subheader("📜 Clause-by-Clause Analysis")

    unfavorable_clauses = []
    high_risk_count = 0

    for clause in clauses[:12]:
        clause_text = clause["text"]
        clause_number = clause["number"]

        risk, triggers = clause_risk(clause_text)
        ambiguous, amb_terms = detect_ambiguity(clause_text)
        category = identify_clause_category(clause_text)

        similarity_score = similarity_flag = None
        if category and category in STANDARD_CLAUSES:
            similarity_score = clause_similarity_score(clause_text, STANDARD_CLAUSES[category])
            similarity_flag = (
                "Aligned with standard"
                if similarity_score >= 0.75
                else "Partially deviates"
                if similarity_score >= 0.5
                else "Significantly deviates"
            )

        if risk in ["Medium", "High"]:
            unfavorable_clauses.append({
                "number": clause_number,
                "clause": clause_text,
                "risk": risk,
                "triggers": triggers
            })

        if risk == "High":
            high_risk_count += 1

        with st.expander(f"Clause {clause_number} | Risk: {risk}"):
            st.write(clause_text)
            st.write("Type:", obligation_type(clause_text))
            st.write("Risk Triggers:", triggers)

            if ambiguous:
                st.warning(f"⚠️ Ambiguous Language Detected: {amb_terms}")

            if similarity_flag:
                st.info(f"📐 Clause Similarity ({category}): {similarity_score} → {similarity_flag}")

            st.markdown(explain_clause(clause_text))

        audit["clauses"].append({
            "number": clause_number,
            "clause": clause_text,
            "risk": risk,
            "risk_triggers": triggers,
            "ambiguous": ambiguous,
            "ambiguity_terms": amb_terms,
            "category": category,
            "similarity_score": similarity_score,
            "similarity_flag": similarity_flag
        })

    st.subheader("⚠️ Unfavourable Clauses (Require Attention)")
    if unfavorable_clauses:
        for item in unfavorable_clauses:
            with st.expander(f"Clause {item['number']} | Risk: {item['risk']}"):
                st.write(item["clause"])
                st.write("Risk Indicators:", item["triggers"])
    else:
        st.success("No significantly unfavourable clauses detected.")

    overall_risk = "High" if high_risk_count >= 3 else "Medium" if high_risk_count == 2 else "Low"
    audit["overall_risk"] = overall_risk

    st.subheader("📊 Overall Contract Risk")
    st.metric("Risk Level", overall_risk)

    save_audit(audit)

    st.download_button(
        "Download Audit Report (JSON)",
        json.dumps(audit, indent=2),
        file_name="legal_audit_report.json"
    )
