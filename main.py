from pydantic_ai import UsageLimits
from pydantic import BaseModel
from agents.agents_schema import RAGAnswer, ConfidenceEvaluation
from agents.agents_factory import AgentFactory
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
import os
from database import ChromaDB
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

PROMPT_DIR = Path(__file__).parent / "system_prompts"
RAG_AGENT_PROMPT_PATH = PROMPT_DIR / "rag_agent_prompt.md"
REWRITE_AGENT_PROMPT_PATH = PROMPT_DIR / "rewrite_agent_prompt.md"
CONFIDENCE_AGENT_PROMPT_PATH = PROMPT_DIR / "confidence_agent_prompt.md"
RAG_AGENT_PROMPT = RAG_AGENT_PROMPT_PATH.read_text(encoding="utf-8")
REWRITE_AGENT_PROMPT = REWRITE_AGENT_PROMPT_PATH.read_text(encoding="utf-8")
CONFIDENCE_AGENT_PROMPT = CONFIDENCE_AGENT_PROMPT_PATH.read_text(encoding="utf-8")

model = OpenAIChatModel(
    "gpt-4o-mini",
    provider=AzureProvider(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_API"),
    ),
)

chroma_client = ChromaDB(model="mixedbread-ai/mxbai-embed-large-v1", collection="rick_and_morty")

agent_factory = AgentFactory()
rag_agent = agent_factory.create_rag_agent(model, chroma_client, RAG_AGENT_PROMPT)
rewrite_agent = agent_factory.create_rewrite_agent(model, REWRITE_AGENT_PROMPT)
confidence_agent = agent_factory.create_confidence_agent(model, CONFIDENCE_AGENT_PROMPT)

MAX_HISTORY_MESSAGES = 20
conversation_history = []

class ChatAnswer(BaseModel):
    rag_agent_response: RAGAnswer
    confidence_agent_response: ConfidenceEvaluation

def answer_question(user_query: str) -> ChatAnswer:
    global conversation_history

    rewrite_result = rewrite_agent.run_sync(
        user_query,
        usage_limits=UsageLimits(request_limit=1),
    )

    improved_query = rewrite_result.output.search_query

    prompt = f"""
    original user prompt: {user_query}
    
    improved user prompt: {improved_query}
    
    entity focus: {rewrite_result.output.entity_focus}
    """
    
    
    result = rag_agent.run_sync(
        prompt,
        message_history=conversation_history,
    )
    conversation_history = result.all_messages()[-MAX_HISTORY_MESSAGES:]
    rag_answer = result.output

    confidence_prompt = f"""
    original user prompt: {user_query}

    improved user prompt: {improved_query}

    entity focus: {rewrite_result.output.entity_focus}

    rag answer:
    {rag_answer.response}

    rag sources:
    {rag_answer.sources}

    rag messages and retrieved context:
    {result.all_messages()}
    """

    confidence_result = confidence_agent.run_sync(
        confidence_prompt,
        usage_limits=UsageLimits(request_limit=3),
    )
    confidence = confidence_result.output

    response = ChatAnswer(rag_agent_response=rag_answer, confidence_agent_response=confidence)

    return response

if __name__ == '__main__':
    response = answer_question("Auf welchen Planeten im Rick and Morty Universum leben die meisten Einwohner?")
    print(response)
