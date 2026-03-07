clauses = {
    "Data Sharing": ["share", "third party", "partners"],
    "Arbitration": ["arbitration", "dispute"],
    "Auto Renewal": ["auto renew", "automatic renewal"],
    "Liability": ["not responsible", "liability"]
}

def extract_clauses(text):

    detected = {}

    for clause, keywords in clauses.items():

        for word in keywords:

            if word.lower() in text.lower():
                detected[clause] = "Detected"

    return detected