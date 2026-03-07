risk_map = {
    "Data Sharing": "High Risk",
    "Arbitration": "High Risk",
    "Auto Renewal": "Medium Risk",
    "Liability": "Medium Risk"
}

def detect_risk(clauses):

    risks = {}

    for clause in clauses:
        risks[clause] = risk_map.get(clause, "Low Risk")

    return risks