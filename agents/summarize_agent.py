from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

def summarize_text(text):

    if len(text) < 50:
        return "Text too short to summarize."

    text = text[:2000]

    result = summarizer(
        text,
        max_length=120,
        min_length=30,
        do_sample=False
    )

    return result[0]["summary_text"]