from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

def summarize_text(text):

    text = text[:1500]
    simple_prompt = "Explain this in very simple English for a class 2 student: " + text
    result = summarizer(
        simple_prompt,
        max_length=60,
        min_length=25,
        do_sample=False
    )


    return result[0]["summary_text"]