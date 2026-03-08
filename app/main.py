from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from controller.controller import analyze_document

app = FastAPI()

# Enable CORS so Chrome extension can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins (safe for local dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Document(BaseModel):
    text: str


@app.get("/")
def home():
    return {"message": "Agentic AI backend running"}


@app.post("/analyze")
def analyze(doc: Document):
    result = analyze_document(doc.text)
    return result