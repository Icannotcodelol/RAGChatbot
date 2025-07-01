# Offline RAG Chatbot System

A complete offline RAG (Retrieval-Augmented Generation) chatbot that runs entirely on your local machine.

## Quick Start

1. **First, rename the environment file:**
   ```bash
   mv env_example.txt .env
   ```

2. **Install dependencies and set up the system:**
   ```bash
   python scripts/setup.py
   ```

3. **Process your documents:**
   ```bash
   python scripts/preprocess_docs.py
   ```

4. **Start the server:**
   ```bash
   python backend/main.py
   ```

5. **Open your browser to:**
   ```
   http://localhost:8000
   ```

## Requirements

- Python 3.8+
- Docker
- 16GB+ RAM (recommended: 32GB)
- ~20GB free storage for models

## Adding Documents

1. Put your `.txt` files in the `documents/` folder
2. Run `python scripts/preprocess_docs.py` to update the embeddings
3. The system will automatically use the new documents

## Note

The first run will download ~20GB of AI models. After that, everything runs offline!
