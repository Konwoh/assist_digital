from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import hashlib
from fastembed import TextEmbedding

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
