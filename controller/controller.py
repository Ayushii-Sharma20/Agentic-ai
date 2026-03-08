from agents.summarize_agent import summarize_text
from agents.clause_agent import analyze_clauses

# meaning of each clause
clause_meanings = {
    "Data sharing": "Your personal data may be shared with third-party companies or partners.",
    
    "Tracking": "The website may track your activity, behavior, or device information.",
    
    "Liability": "The company limits its responsibility if something goes wrong while using the service.",
    
    "Arbitration": "Legal disputes must be resolved through arbitration instead of court.",
    
    "Auto renewal": "Subscriptions may renew automatically unless you cancel them.",
    
    "User rights": "Users may have rights to access, modify, or delete their personal data.",
    
    "Subscription": "The service may require recurring payments or membership."
}


def analyze_document(text):

    summary = summarize_text(text)

    detected_clauses = analyze_clauses(text)

    # attach meaning to each clause
    clauses = []
    for clause in detected_clauses:
        clauses.append({
            "clause": clause,
            "meaning": clause_meanings.get(clause, "Explanation not available")
        })

    # risk logic
    if len(detected_clauses) > 2:
        risk = "High"
        recommendation = "❌ Not Recommended to Accept"
    elif len(detected_clauses) > 0:
        risk = "Medium"
        recommendation = "⚠️ Read Carefully Before Accepting"
    else:
        risk = "Low"
        recommendation = "✅ Safe to Accept"

    return {
        "summary": summary,
        "risk": risk,
        "clauses": clauses,
        "recommendation": recommendation
    }