from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
from dotenv import load_dotenv
import os
from pathlib import Path
from database import ChromaDB

load_dotenv()

SYSTEM_PROMPT_PATH = Path(__file__).with_name("system_prompt.md")
SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

model = OpenAIChatModel(
    "gpt-4o-mini",
    provider=AzureProvider(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_API"),
    ),
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
)


def get_collection():
    chroma_client = ChromaDB(model="nomic-ai/nomic-embed-text-v1", collection="rick_and_morty")
    return chroma_client.collection


@agent.tool_plain
def retrieval_tool(query: str):
    """Retrieve information to help answer a query"""
    chroma_client = ChromaDB(model="nomic-ai/nomic-embed-text-v1", collection="rick_and_morty")
    
    query_vector = chroma_client.text_to_vector(query)

    results = chroma_client.collection.query(
        query_embeddings=[query_vector],
        n_results=5
    )
    return results


@agent.tool_plain
def get_episode_by_id(episode_id: int):
    """Use this for questions like 'Episode 1', 'Episode 2', 'erste Folge', 'zweite Episode', 'letzte Episode'. The id is the overall episode number."""
    result = get_collection().get(
        ids=[f"episode:{episode_id}"],
        include=["documents", "metadatas"],
    )

    if not result["ids"]:
        return {
            "found": False,
            "episode_id": episode_id,
        }

    return {
        "found": True,
        "episode_id": episode_id,
        "id": result["ids"][0],
        "document": result["documents"][0],
        "metadata": result["metadatas"][0],
    }


result = agent.run_sync("Wie heißt die letzte Episode von Rick and Morty?")
print(result.output)
print(result.all_messages())
