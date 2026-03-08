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

    # limit text length for performance
    text = text[:3000]

    result = classifier(text, labels)

    for label, score in zip(result["labels"], result["scores"]):

        if score > 0.3 and label not in clauses:
            clauses.append(label)

    return clauses