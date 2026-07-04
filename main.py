from pydantic_ai import Agent, ModelSettings, UsageLimits
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider
from dotenv import load_dotenv
import os
from pathlib import Path
from database import ChromaDB
from typing import Literal
load_dotenv()

PROMPT_DIR = Path(__file__).parent / "system_prompts"
RAG_AGENT_PROMPT_PATH = PROMPT_DIR / "rag_agent_prompt.md"
REWRITE_AGENT_PROMPT_PATH = PROMPT_DIR / "rewrite_agent_prompt.md"
RAG_AGENT_PROMPT = RAG_AGENT_PROMPT_PATH.read_text(encoding="utf-8")
REWRITE_AGENT_PROMPT = REWRITE_AGENT_PROMPT_PATH.read_text(encoding="utf-8")


chroma_client = ChromaDB(model="mixedbread-ai/mxbai-embed-large-v1", collection="rick_and_morty")

model = OpenAIChatModel(
    "gpt-4o-mini",
    provider=AzureProvider(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_API"),
    ),
)

class RewrittenQuery(BaseModel):
    search_query: str = Field(description="Optimierte Query für die semantische Suche")
    entity_focus: list[Literal["character", "episode", "location"]] = Field(
        default_factory=list,
        description="Welche Entitätstypen wahrscheinlich relevant sind",
    )


query_rewriter = Agent(
    model=model,
    output_type=RewrittenQuery,
    model_settings=ModelSettings(temperature=0.0),
    system_prompt=REWRITE_AGENT_PROMPT,
)

rag_agent = Agent(
    model=model,
    system_prompt=RAG_AGENT_PROMPT,
)

@rag_agent.tool_plain
def retrieve_info(entity_group: Literal["characters", "episodes"]):
    """Retrieve count/page info for characters or episodes. Use it for general informatioon about the entities"""
    
    result = chroma_client.collection.get(
        ids=[f"info:{entity_group}"],
        include=["documents", "metadatas"],
    )

    documents = result.get("documents")
    metadatas = result.get("metadatas")
    
    if not result["ids"] or not documents:
        return {"found": False, "entity_group": entity_group}
    
    return {
        "found": True,
        "entity_group": entity_group,
        "document": documents[0],
        "metadata": metadatas[0] if metadatas else None,
    }
    
@rag_agent.tool_plain
def retrieval_tool(query: str):
    """Retrieve information to help answer a query"""
    query_vector = chroma_client.text_to_vector(query)

    results = chroma_client.collection.query(
        query_embeddings=[query_vector],
        n_results=5,
        include=["documents", "metadatas"]
    )
    return results


@rag_agent.tool_plain
def get_episode_by_id(episode_id: int):
    """Use this for questions like 'Episode 1', 'Episode 2', 'erste Folge', 'zweite Episode', 'letzte Episode'. The id is the overall episode number."""
    result = chroma_client.collection.get(
        ids=[f"episodes:{episode_id}"],
        include=["documents", "metadatas"],
    )

    documents = result.get("documents")
    metadatas = result.get("metadatas")
    
    if not result["ids"] or not documents:
        return {
            "found": False,
            "episode_id": episode_id,
        }

    return {
        "found": True,
        "episode_id": episode_id,
        "id": result["ids"][0],
        "document": documents[0],
        "metadata": metadatas[0] if metadatas else None,
    }


def answer_question(user_query: str) -> str:
    rewrite_result = query_rewriter.run_sync(
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
    )

    return result.output

if __name__ == '__main__':
    response = answer_question("Wann wurde die erste Folge ausgestrahlt?")
    print(response)
