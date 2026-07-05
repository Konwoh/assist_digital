import hashlib
import os
from pathlib import Path
from typing import List, Optional

from chromadb import PersistentClient
from fastembed import TextEmbedding

from backend.models.entities import Entity


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CHROMA_PATH = PROJECT_ROOT / "chromadb"


class ChromaDB:
    def __init__(self, model, collection):
            chroma_path = Path(os.getenv("CHROMA_PATH", DEFAULT_CHROMA_PATH))
            self.client = PersistentClient(path=str(chroma_path))
            self.model = TextEmbedding(model)
            self.collection = self.client.get_or_create_collection(name=collection)
    
    def text_to_vector(self, text) -> list[float]:
        embedding = next(iter(self.model.embed([str(text)])))
        return embedding.tolist()

    def chunk_id(self, source: str, chunk_index: int, text: str) -> str:
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        return f"{source}:{chunk_index}:{h}"

    def _upload_vectordb(self, obj, ids: List, metadata_type: str, metadata_name: Optional[str] = None):
        vector = self.text_to_vector(obj)
        
        metadata = {
        "type": metadata_type,
        }
        if metadata_name is not None:
            metadata["name"] = metadata_name
        
        self.collection.upsert(
            ids=ids,
            embeddings=[vector],
            documents=[str(obj)],
            metadatas=[metadata],
        )
    
    def upload_entity_list(self, entity_list: List[Entity], entity_group: str):
        for entity in entity_list:
            self._upload_vectordb(entity, [f"{entity_group}:{entity.id}"], entity_group, entity.name)
    
    def upload_info(self, info: str, entity_group: str):
        self._upload_vectordb(info, [f"info:{entity_group}"], "info")
