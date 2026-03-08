from agents.summarize_agent import summarize_text
from agents.clause_agent import analyze_clauses

def analyze_document(text):

    summary = summarize_text(text)

    clauses = analyze_clauses(text)

    # simple risk logic
    if len(clauses) > 2:
        risk = "High"
    elif len(clauses) > 0:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "summary": summary,
        "risk": risk,
        "clauses": clauses
    }