from fastapi import FastAPI
from pydantic import BaseModel
from main import answer_question

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = answer_question(request.message)
    return ChatResponse(answer=answer)