from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import answer_question

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: str
    confidence_score: float
    confidence_label: str

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = answer_question(request.message)
    response = answer.rag_agent_response.response
    sources = answer.rag_agent_response.sources
    confidence_label = answer.confidence_agent_response.label
    confidence_score = answer.confidence_agent_response.score
    return ChatResponse(answer=response, sources=sources, confidence_score= confidence_score, confidence_label=confidence_label)
