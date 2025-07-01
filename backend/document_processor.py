import PyPDF2
import docx
from typing import List, Dict
import re
from pathlib import Path
import tempfile
import os

class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        return text
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    def extract_text(self, file_path: str, filename: str) -> str:
        """Extract text based on file extension"""
        file_extension = Path(filename).suffix.lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise Exception(f"Unsupported file type: {file_extension}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\(\)]', '', text)
        return text.strip()
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        words = text.split()
        if len(words) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            if end >= len(words):
                break
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_file(self, file_path: str, filename: str) -> List[Dict]:
        """Process a file and return chunks with metadata"""
        try:
            # Extract text
            raw_text = self.extract_text(file_path, filename)
            
            if not raw_text.strip():
                raise Exception("No text could be extracted from the file")
            
            # Clean text
            cleaned_text = self.clean_text(raw_text)
            
            # Chunk text
            chunks = self.chunk_text(cleaned_text)
            
            # Create document objects
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    "text": chunk,
                    "filename": filename,
                    "chunk_id": i,
                    "total_chunks": len(chunks)
                })
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error processing file {filename}: {str(e)}")
    
    async def process_uploaded_file(self, file_content: bytes, filename: str) -> List[Dict]:
        """Process uploaded file content"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            documents = self.process_file(temp_file_path, filename)
            return documents
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path) 