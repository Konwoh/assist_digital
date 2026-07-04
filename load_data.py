from fetch_data import DataFetcher, DataMatcher
from database import ChromaDB

chroma_client = ChromaDB(model="mixedbread-ai/mxbai-embed-large-v1", collection="rick_and_morty")

character_fetcher = DataFetcher("character")
episode_fetcher = DataFetcher("episode")
location_fetcher = DataFetcher("location")

characters = character_fetcher.fetch_pages()
characters_info = character_fetcher.fetch_info()
episodes = episode_fetcher.fetch_pages()
episodes_info = episode_fetcher.fetch_info()
locations = location_fetcher.fetch_pages()
locations_info = location_fetcher.fetch_info()

DataMatcher(episodes, characters).matching()
DataMatcher(characters, episodes).matching()
DataMatcher(characters, locations).matching()


chroma_client.upload_entity_list(characters, entity_group="characters")
chroma_client.upload_entity_list(episodes, entity_group="episodes")
chroma_client.upload_entity_list(locations, entity_group="locations")
chroma_client.upload_info(characters_info, "characters")
chroma_client.upload_info(episodes_info, "episodes")
chroma_client.upload_info(locations_info, "locations")