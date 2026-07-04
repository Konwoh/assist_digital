from chromadb import PersistentClient
import hashlib
from fastembed import TextEmbedding
from typing import List, Optional
from models.entities import Entity

class ChromaDB:
    def __init__(self, model, collection):
            self.client = PersistentClient(path="chromadb/")
            self.model = TextEmbedding(model)
            self.collection = self.client.get_or_create_collection(name=collection)
            #self.r_splitter = RecursiveCharacterTextSplitter(chunk_size=splitter_chunksize, chunk_overlap=150)
    
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
