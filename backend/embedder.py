import numpy as np
from typing import List, Union
from InstructorEmbedding import INSTRUCTOR
import torch
import pickle
from pathlib import Path
from backend.config import config

class InstructorEmbedder:
    def __init__(self):
        # Detect best available device
        if torch.backends.mps.is_available():
            self.device = 'mps'
            print("Using MPS (Apple Silicon GPU) for embedding acceleration")
        elif torch.cuda.is_available():
            self.device = 'cuda'
            print("Using CUDA GPU for embedding acceleration")
        else:
            self.device = 'cpu'
            print("Using CPU for embeddings (no GPU acceleration available)")
        
        print(f"Loading Instructor model: {config.INSTRUCTOR_MODEL}")
        self.model = INSTRUCTOR(config.INSTRUCTOR_MODEL, device=self.device)
        
    def embed_documents(self, texts: List[str]) -> np.ndarray:
        """Embed documents for storage"""
        instructions = ["Represent the document for retrieval:"] * len(texts)
        embeddings = self.model.encode(
            [(inst, text) for inst, text in zip(instructions, texts)],
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a user query for search"""
        instruction = "Represent the question for retrieving supporting documents:"
        embedding = self.model.encode(
            [[instruction, query]],
            convert_to_numpy=True
        )
        return embedding[0]
    
    def save_embeddings(self, embeddings: np.ndarray, doc_ids: List[str]):
        """Cache embeddings to disk"""
        cache_file = config.EMBEDDINGS_CACHE_PATH / "embeddings_cache.pkl"
        data = {"embeddings": embeddings, "doc_ids": doc_ids}
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    
    def load_embeddings(self):
        """Load cached embeddings from disk"""
        cache_file = config.EMBEDDINGS_CACHE_PATH / "embeddings_cache.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None 