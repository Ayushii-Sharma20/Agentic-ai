from agents.summarize_agent import summarize_text
from agents.clause_agent import extract_clauses
from agents.risk_agent import detect_risk

def analyze_document(text):

    summary = summarize_text(text)

    clauses = extract_clauses(text)

    risks = detect_risk(clauses)

    return {
        "summary": summary,
        "clauses": clauses,
        "risks": risks
    }