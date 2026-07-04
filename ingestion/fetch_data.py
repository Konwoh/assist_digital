import requests
from logger import logger 
from models.entities import Entity, Character, Episode, Location
from models.factory import EntityFactory
from typing import List, Optional
import time

class DataFetcher:
    def __init__(self, entity: str) -> None:
        self.entity = entity

    def _build_url(self, id: Optional[int] = None , page: Optional[int] = None) -> str:
        if id is None:
            if page is not None:
                return f"https://rickandmortyapi.com/api/{self.entity}?page={page}"
            else:
                return f"https://rickandmortyapi.com/api/{self.entity}"
        else:
            return f"https://rickandmortyapi.com/api/{self.entity}/{id}"
    
    def _fetch_internal_url(self, url: str, entity_type: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            entity = EntityFactory.create_entity(entity_type, data)
            return entity.name
        
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error occurred: %s", e)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("A request error occurred: %s", e)
            raise
        except Exception as e:
            logger.error("Error: %s", e)
            raise  
    
    def fetch_info(self) -> str:
        try:
            url = self._build_url()
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            info = data["info"]
            return info
        
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error occurred: %s", e)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("A request error occurred: %s", e)
            raise
        except Exception as e:
            logger.error("Error: %s", e)
            raise
           
    def fetch_pages(self) -> List[Entity]:
        result_list = []
        try:
            url = self._build_url(page=1)
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            pages = data["info"]["pages"]
            
            for page in range(1, pages + 1):
                response = requests.get(self._build_url(page=page))
                response.raise_for_status()
                data = response.json()
                results = data["results"]
                for result in results:
                    entity = EntityFactory.create_entity(self.entity, result)
                    result_list.append(entity)
                time.sleep(0.5)
            return result_list
        
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error occurred: %s", e)
            raise
        except requests.exceptions.RequestException as e:
            logger.error("A request error occurred: %s", e)
            raise
        except Exception as e:
            logger.error("Error: %s", e)
            raise

class DataMatcher:
    def __init__(self, entity1: List[Entity], entity2: List[Entity]) -> None:
        self.entity1 = entity1
        self.entity2 = entity2
    
    def matching(self):
        entity_by_url = {
            entity.url: entity
            for entity in self.entity1
        }
        
        for entity in self.entity2:
            if isinstance(entity, Character):
                entity.episode = [
                    entity_by_url[episode_url].name
                    for episode_url in entity.episode
                ]
            elif isinstance(entity, Episode):
                entity.characters = [
                    entity_by_url[character_url].name
                    for character_url in entity.characters
                ]
            elif isinstance(entity, Location):
                entity.residents = [
                    entity_by_url[character_url].name
                    for character_url in entity.residents
                ]