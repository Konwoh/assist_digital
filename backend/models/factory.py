from backend.models.entities import Character, Entity, Episode, Location

class EntityFactory:
    @staticmethod
    def create_entity(entity: str, data: dict) -> Entity:
        if entity == "character":
            return Character(**data)
        elif entity == "location":
            return Location(**data)
        elif entity == "episode":
            return Episode(**data)
        else:
            raise ValueError("Entity type unknown")
