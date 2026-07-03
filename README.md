# Chat with Codebase

A sleek web application that allows developers to paste a GitHub URL, ingest the repository into a vector database using syntax-aware chunking, and chat with the codebase using an advanced RAG (Retrieval-Augmented Generation) pipeline.

## Features
- **Intelligent Ingestion:** Automatically clones and chunks `.py`, `.md`, and `.dart` files using LangChain's `LanguageTextSplitters`.
- **Hybrid Search & Metadata:** Embeddings are stored in Qdrant with metadata (file name, path, language).
- **Citations:** The AI explicitly cites the source files used to generate the answer.
- **Sleek UI:** A beautiful, dark-themed Flutter web interface for interacting with the codebase.
- **Evaluated Pipeline:** The RAG pipeline was evaluated using **DeepEval** for Faithfulness and Contextual Relevancy to ensure high-quality and non-hallucinated responses.

## Architecture

The backend follows **SOLID principles** and is highly modular, heavily utilizing **Dependency Injection** (via FastAPI's `Depends`) for clean and testable code.

1. **Frontend:** Flutter Web UI communicating with the backend.
2. **Backend Services (`backend/services/`):** 
   - `git_service.py`: Handles cloning repositories.
   - `chunking_service.py`: Handles reading files and syntax-aware text splitting.
   - `ingestion.py`: Orchestrates the git, chunking, and database services.
   - `rag.py`: Handles hybrid search and LLM interaction.
3. **Core Infrastructure (`backend/core/`):** Centralizes configuration (`config.py`), vector store initialization (`database.py`), and Embeddings/LLM clients (`llm.py`).
4. **Data Pipeline:** `gitpython` for cloning, LangChain for chunking, and `fastembed` for local lightweight embeddings.
5. **Vector DB:** Qdrant Cloud for storing embeddings and metadata.
6. **LLM:** OpenRouter (Gemini Pro) for generating answers with citations.

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the root directory with the following keys:
   ```env
   QDRANT_URL=your_qdrant_cluster_url
   QDRANT_API_KEY=your_qdrant_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```
3. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Fetch dependencies and run:
   ```bash
   flutter pub get
   flutter run -d chrome
   ```


### Further Improvements which i will be making in upcoming days
1. Hybrid Search (BM25 + Vector)
The Problem: Standard vector search is great for "concepts" but terrible at exact keyword matching. If someone searches for a highly specific variable name like AUTH_TOKEN_V2, the dense vector embeddings might completely miss it. The Fix: Qdrant supports Hybrid Search. We can combine sparse vectors (BM25 for exact keyword matches) with your dense embeddings. This gives you the best of both worlds and drastically improves codebase RAG accuracy.

2. Conversational Memory (Follow-ups)
The Problem: Your /chat endpoint is currently stateless. If a user asks "Show me the main() function", and then follows up with "What does the second line do?", the AI has no memory of the previous question and will get confused. The Fix: We can add LangChain's conversational memory (using SQLite or just in-memory storage) and require a session_id from the Flutter frontend. This allows true back-and-forth debugging sessions.

3. AST-based Code Chunking
The Problem: Right now, your RecursiveCharacterTextSplitter just chops Python code into 1000-character blocks. This means a single 50-line function might get sliced right down the middle, separating the def from its return statement. The Fix: We can implement a code-aware AST (Abstract Syntax Tree) splitter. Instead of splitting by arbitrary character limits, it splits by classes and functions, ensuring chunks represent whole, logical blocks of code.

4. Streaming Responses (Typing Effect)
The Problem: Because AI takes time to generate long answers, the user has to wait a few seconds staring at a loading spinner before the entire answer appears at once. The Fix: We can use FastAPI's StreamingResponse and update the Flutter frontend to receive Server-Sent Events (SSE). The answer will stream in word-by-word instantly, making the app feel incredibly fast and premium.

5. LLM Tool Calling (Agentic RAG)
The Problem: The current setup only gets one shot to search the database. If it doesn't find the answer in the top 20 chunks, it fails. The Fix: Instead of basic RAG, we can upgrade the LLM to an Agent. We can give it tools like search_codebase and view_file. If its first search doesn't find the answer, the AI can autonomously decide to perform a second search with different keywords before answering the user.
