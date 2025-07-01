from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict
import os

from backend.embedder import InstructorEmbedder
from backend.vector_store import QdrantVectorStore
from backend.llm import QwenLLM
from backend.document_processor import DocumentProcessor
from backend.config import config

# Initialize components
app = FastAPI(title="Offline RAG Chatbot")
embedder = InstructorEmbedder()
vector_store = QdrantVectorStore()
llm = QwenLLM()
document_processor = DocumentProcessor()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Dict]

class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_processed: int

@app.post("/api/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Process a user question and return an answer with sources"""
    try:
        # Embed the question
        query_embedding = embedder.embed_query(request.question)
        
        # Search for relevant documents
        relevant_docs = vector_store.search(
            query_embedding, 
            top_k=config.TOP_K_RESULTS
        )
        
        if not relevant_docs:
            return AnswerResponse(
                answer="I couldn't find any relevant information to answer your question.",
                sources=[]
            )
        
        # Generate answer using LLM
        answer = llm.generate_answer(request.question, relevant_docs)
        
        return AnswerResponse(
            answer=answer,
            sources=relevant_docs
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF, DOCX, or TXT)"""
    try:
        # Validate filename
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Process the document
        documents = await document_processor.process_uploaded_file(file_content, file.filename)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")
        
        # Generate embeddings
        texts = [doc["text"] for doc in documents]
        embeddings = embedder.embed_documents(texts)
        
        # Store in vector database
        vector_store.add_documents(embeddings, documents)
        
        return UploadResponse(
            message="Document uploaded and processed successfully",
            filename=file.filename,
            chunks_processed=len(documents)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Serve frontend
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT) 