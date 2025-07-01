#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} - Complete!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}")
        print(f"Error: {e}")
        sys.exit(1)

def main():
    print("\n🚀 Setting up Offline RAG Chatbot System")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    directories = ["documents", "embeddings", "qdrant_storage", "backend", "frontend", "scripts"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Directories created!")
    
    # Install Python dependencies
    run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies"
    )
    
    # Start Qdrant using Docker Compose
    run_command(
        "docker-compose up -d",
        "Starting Qdrant vector database"
    )
    
    # Download models (this will cache them locally)
    print("\n🤖 Downloading models (this may take a while on first run)...")
    print("Models will be cached locally for offline use.")
    
    # Create a test script to download models
    test_script = """
import sys
sys.path.append('.')
from backend.embedder import InstructorEmbedder
from backend.llm import QwenLLM

print("Downloading Instructor-XL...")
embedder = InstructorEmbedder()
print("✅ Instructor-XL ready!")

print("\\nDownloading Qwen model...")
print("⚠️  Note: Qwen-7B is ~14GB. This will take time on first download.")
llm = QwenLLM()
print("✅ Qwen model ready!")
"""
    
    with open("test_models.py", "w") as f:
        f.write(test_script)
    
    run_command(
        "python test_models.py",
        "Downloading and testing models"
    )
    
    os.remove("test_models.py")
    
    print("\n" + "="*60)
    print("✅ Setup complete!")
    print("="*60)
    print("\n📝 Next steps:")
    print("1. Add your .txt documents to the 'documents' folder")
    print("2. Run: python scripts/preprocess_docs.py")
    print("3. Start the server: python backend/main.py")
    print("4. Open http://localhost:8000 in your browser")
    print("\n💡 The system is now fully offline-capable!")

if __name__ == "__main__":
    main() 