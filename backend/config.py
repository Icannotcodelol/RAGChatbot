import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Qdrant settings
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "documents")
    
    # Model settings
    INSTRUCTOR_MODEL = os.getenv("INSTRUCTOR_MODEL", "hkunlp/instructor-xl")
    QWEN_MODEL = os.getenv("QWEN_MODEL", "Qwen/Qwen-7B-Chat")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 768))
    
    # Paths
    DOCUMENTS_PATH = Path(os.getenv("DOCUMENTS_PATH", "./documents"))
    EMBEDDINGS_CACHE_PATH = Path(os.getenv("EMBEDDINGS_CACHE_PATH", "./embeddings"))
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # RAG settings
    TOP_K_RESULTS = 5
    MAX_CONTEXT_LENGTH = 2000
    
    @classmethod
    def ensure_directories(cls):
        cls.DOCUMENTS_PATH.mkdir(exist_ok=True)
        cls.EMBEDDINGS_CACHE_PATH.mkdir(exist_ok=True)

config = Config()
config.ensure_directories() 