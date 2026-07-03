from dataclasses import dataclass
from typing import List, Dict
from enum import Enum
from abc import ABC

class CharacterStatus(Enum):
    ALIVE = "Alive"
    DEAD = "Dead"
    UNKNOWN = "unknown"

class CharacterSpecies(Enum):
    ALIEN = "Alien"
    HUMAN = "Human"
    HUMANOID = "Humanoid"
    UNKNOWN = "unknown"
    POPPYBUTTHOLE = "Poopybutthole"
    MYTHOLOGICAL_CREATURE = "Mythological Creature"
    ANIMAL = "Animal"
    ROBOT = "Robot"
    CRONENBERG= "Cronenberg"
    DISEASE = "Disease"
    
    
class CharacterGender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    UKNOWN = "unknown"
    GENDERLESS = "Genderless"
    
class Entity(ABC):
    def __repr__(self) -> str:
        fields = []
        for name, value in vars(self).items():
            if isinstance(value, Enum):
                value = value.value
            fields.append(f"{name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(fields)})"

class Character(Entity):
    def __init__(self, id: int, name: str, status: str, species: str, type: str, gender: str, origin: Dict, location: Dict, image: str, episode: List[str], url: str, created: str):
        self.id = id
        self.name = name
        self.status = CharacterStatus(status)
        self.species = CharacterSpecies(species)
        self.type = type
        self.gender = CharacterGender(gender)
        self.origin = origin
        self.location = location
        self.image = image
        self.episode = episode
        self.url = url
        self.created = created

@dataclass(repr=False)
class Episode(Entity):
    id: int
    name: str
    air_date: str
    episode: str
    characters: List[str]
    url: str
    created: str   

@dataclass(repr=False)
class Location(Entity):
    id: int
    name: str
    type: str
    dimension: str
    residents: List[str]
    url: str
    created: str
