from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

def summarize_text(text):

    # limit text length to avoid model crash
    text = text[:2000]

    result = summarizer(
        text,
        max_length=180,
        min_length=30,
        do_sample=False
    )

    return result[0]["summary_text"]