from typing import List, Dict, Tuple
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from backend.config import config
import uuid

class QdrantVectorStore:
    def __init__(self):
        self.client = QdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT
        )
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if config.QDRANT_COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=config.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=config.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {config.QDRANT_COLLECTION_NAME}")
    
    def add_documents(self, embeddings: np.ndarray, documents: List[Dict]):
        """Add documents with their embeddings to Qdrant"""
        points = []
        for i, (embedding, doc) in enumerate(zip(embeddings, documents)):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "text": doc["text"],
                    "filename": doc["filename"],
                    "chunk_id": doc.get("chunk_id", i)
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=config.QDRANT_COLLECTION_NAME,
            points=points
        )
        print(f"Added {len(points)} documents to Qdrant")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        results = self.client.search(
            collection_name=config.QDRANT_COLLECTION_NAME,
            query_vector=query_embedding.tolist(),
            limit=top_k
        )
        
        return [
            {
                "text": result.payload["text"],
                "filename": result.payload["filename"],
                "score": result.score
            }
            for result in results
        ]
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        self.client.delete_collection(collection_name=config.QDRANT_COLLECTION_NAME)
        self._ensure_collection() 