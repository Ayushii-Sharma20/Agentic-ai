from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="typeform/distilbert-base-uncased-mnli"
)

labels = [
    "Data sharing",
    "Arbitration",
    "Auto renewal",
    "Liability",
    "Tracking",
    "User rights",
    "Subscription"
]

def analyze_clauses(text):

    clauses = []

    result = classifier(text[:1200], labels)

    for label, score in zip(result["labels"], result["scores"]):
        if score > 0.5:
            clauses.append(label)

    return clauses