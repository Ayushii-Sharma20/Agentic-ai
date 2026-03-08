from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
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

def detect_clauses(text):

    result = classifier(text[:1000], labels)

    detected = {}

    for label, score in zip(result["labels"], result["scores"]):
        if score > 0.5:
            detected[label] = round(score,2)

    return detected