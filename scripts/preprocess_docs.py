import os
import sys
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.embedder import InstructorEmbedder
from backend.vector_store import QdrantVectorStore
from backend.config import config

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

def process_documents():
    """Process all documents in the documents folder"""
    embedder = InstructorEmbedder()
    vector_store = QdrantVectorStore()
    
    # Clear existing data
    print("Clearing existing vector store...")
    vector_store.clear_collection()
    
    # Process all .txt files
    documents = []
    texts = []
    
    for file_path in config.DOCUMENTS_PATH.glob("*.txt"):
        print(f"Processing: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chunk the document
        chunks = chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            documents.append({
                "text": chunk,
                "filename": file_path.name,
                "chunk_id": i
            })
            texts.append(chunk)
    
    if not documents:
        print("No documents found in the documents folder!")
        return
    
    # Generate embeddings
    print(f"Generating embeddings for {len(documents)} chunks...")
    embeddings = embedder.embed_documents(texts)
    
    # Save embeddings to cache
    doc_ids = [f"{doc['filename']}_{doc['chunk_id']}" for doc in documents]
    embedder.save_embeddings(embeddings, doc_ids)
    
    # Add to vector store
    print("Adding documents to vector store...")
    vector_store.add_documents(embeddings, documents)
    
    print(f"Successfully processed {len(documents)} document chunks!")

if __name__ == "__main__":
    process_documents() 