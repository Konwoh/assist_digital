from pydantic_ai import Agent, ModelSettings
from .agents_schema import RewrittenQuery, ConfidenceEvaluation, RAGAnswer
from typing import Literal

class AgentFactory:
    def create_rag_agent(self, model, chroma_client, prompt: str) -> Agent[object, RAGAnswer]:
        rag_agent = Agent(
            model=model,
            output_type=RAGAnswer,
            system_prompt=prompt,
        )

        @rag_agent.tool_plain
        def retrieve_info(entity_group: Literal["characters", "episodes"]):
            """Retrieve count/page info for characters or episodes."""
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
                "source": f"Rick and Morty API {entity_group} info"
            }

        @rag_agent.tool_plain
        def retrieval_tool(query: str):
            """Retrieve information to help answer a query."""
            query_vector = chroma_client.text_to_vector(query)

            return chroma_client.collection.query(
                query_embeddings=[query_vector],
                n_results=5,
                include=["documents", "metadatas"],
            )

        @rag_agent.tool_plain
        def get_episode_by_id(episode_id: int):
            """Use this for questions about a specific overall episode number."""
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

        return rag_agent

    def create_rewrite_agent(self, model, prompt: str) -> Agent[object, RewrittenQuery]:
        return Agent(
            model=model,
            output_type=RewrittenQuery,
            model_settings=ModelSettings(temperature=0.0),
            system_prompt=prompt,
        )

    def create_confidence_agent(self, model, prompt: str) -> Agent[object, ConfidenceEvaluation]:
        return Agent(
            model=model,
            output_type=ConfidenceEvaluation,
            model_settings=ModelSettings(temperature=0.0),
            system_prompt=prompt,
        )
