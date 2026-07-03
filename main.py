from fetch_data import DataFetcher, DataMatcher

character_fetcher = DataFetcher("character")
episode_fetcher = DataFetcher("episode")

characters = character_fetcher.fetch_pages()
episodes = episode_fetcher.fetch_pages()

DataMatcher(characters, episodes).matching()

print(episodes)