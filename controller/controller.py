def analyze_document(text):

    summary = summarize_text(text)
    clauses = detect_clauses(text)

    risk = "Low"

    if "Data Sharing" in clauses:
        risk = "Medium"

    if "Arbitration" in clauses or "Auto Renewal" in clauses:
        risk = "High"

    return {
        "summary": summary,
        "clauses": clauses,
        "risk": risk
    }