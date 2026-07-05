from chat_service import ChatService
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
def create_chat_service() -> ChatService:
    chroma_client = ChromaDB(model="mixedbread-ai/mxbai-embed-large-v1", collection="rick_and_morty")

    agent_factory = AgentFactory()
    rag_agent = agent_factory.create_rag_agent(model, chroma_client, RAG_AGENT_PROMPT)
    rewrite_agent = agent_factory.create_rewrite_agent(model, REWRITE_AGENT_PROMPT)
    confidence_agent = agent_factory.create_confidence_agent(model, CONFIDENCE_AGENT_PROMPT)

    return ChatService(rag_agent, rewrite_agent, confidence_agent)


chat_service = create_chat_service()


def answer_question(query: str):
    return chat_service.answer_question(query)


def add_feedback_to_history(feedback: bool) -> None:
    chat_service.add_feedback_to_history(feedback)
    
if __name__ == '__main__':
    print(answer_question("Auf welchen Planeten im Rick and Morty Universum leben die meisten Einwohner?"))
