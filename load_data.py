from fetch_data import DataFetcher, DataMatcher
from database import ChromaDB

chroma_client = ChromaDB(model="Qwen/Qwen3-Embedding-0.6B", collection="rick_and_morty")

character_fetcher = DataFetcher("character")
episode_fetcher = DataFetcher("episode")

characters = character_fetcher.fetch_pages()
episodes = episode_fetcher.fetch_pages()

DataMatcher(episodes, characters).matching()
DataMatcher(characters, episodes).matching()


for char in characters:
    print(char)
    vector = chroma_client.text_to_vector(char)
    chroma_client.collection.upsert(
        ids=[f"character:{char.id}"],
        embeddings=[vector],
        documents=[str(char)],
        metadatas=[{
            "type": "character",
            "name": char.name,
        }],
    )
    
for episode in episodes:
    vector = chroma_client.text_to_vector(episode)
    chroma_client.collection.upsert(
        ids=[f"episode:{episode.id}"],
        embeddings=[vector],
        documents=[str(episode)],
        metadatas=[{
            "type": "episode",
            "name": episode.name,
        }],
    )

