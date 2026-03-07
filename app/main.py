from fastapi import FastAPI
from pydantic import BaseModel
from controller.controller import analyze_document

app = FastAPI()

class Document(BaseModel):
    text: str


@app.get("/")
def home():
    return {"message": "Agentic AI backend running"}


@app.post("/analyze")
def analyze(doc: Document):
    result = analyze_document(doc.text)
    return result