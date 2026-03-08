from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="typeform/distilbert-base-uncased-mnli"
)
labels = [
    "Data Sharing",
    "Arbitration",
    "Auto Renewal",
    "Liability",
    "Tracking",
    "User Rights",
    "Subscription"
]
def analyze_clauses(text):

    clauses = []

    text = text.lower()

    if "data" in text and "share" in text:
        clauses.append("Data Sharing Clause")

    if "track" in text or "tracking" in text:
        clauses.append("User Tracking")

    if "third party" in text:
        clauses.append("Third‑Party Data Access")

    if "terminate" in text:
        clauses.append("Account Termination Rights")

    return clauses