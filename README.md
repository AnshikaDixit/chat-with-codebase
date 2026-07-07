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

### Core theoretical concepts of Retrieval-Augmented Generation (RAG):

1. Metadata Filtering (Pre-filtering)
The Concept: Before running a computationally expensive vector similarity search, you can narrow down the search space using structured metadata (like tags, dates, or file paths). This dramatically reduces hallucinations by preventing the system from pulling context from completely irrelevant areas of the codebase.
In code: We build must_conditions using Qdrant's FieldCondition. If a user specifies a folder_path or repo_url, the Qdrant engine filters out any vector embeddings that don't match those strings before measuring cosine similarity.

2. Vector Retrieval
The Concept: The core of the "R" in RAG. The user's text query is converted into a vector embedding (using FastEmbed in your case). The vector database (Qdrant) then compares this query vector against all chunk vectors in the database, typically using Cosine Similarity, and returns the most mathematically similar ones.
In code: self.vector_store.as_retriever(search_kwargs={"k": 20}) sets this up, and .invoke(query) executes it, returning the top_k=20 most semantically relevant codebase chunks.

3. Targeted / Exact Match Retrieval (Fallback/Hybrid Search)
The Concept: Pure semantic similarity struggles with exact keyword matching. For example, if a user asks "Show me the contents of main.py", the vector space might think a file named core.py is semantically similar to the word "main" and retrieve the wrong file. Hybrid search combines semantic search with exact keyword matching to solve this.
In code: We use a Regex to detect if the user is asking for a specific file (e.g. read config.py). If detected, we run a second retrieval query that enforces a strict metadata filter (metadata.file_name = target_file), ensuring the LLM is fed the exact file it needs, regardless of semantic similarity. We then merge and deduplicate these results with the standard vector search results.

4. Context Assembly (The "Augmentation")
The Concept: The LLM doesn't read the vector database directly. The retrieved chunks must be formatted into a plain text string that fits within the LLM's context window. This string is "injected" into the prompt alongside the user's original question.
In code: We iterate through the retrieved docs, extract the file names to build a citations list, and concatenate the actual chunk contents (doc.page_content) into one large context_str, formatted with headings --- filename ---.

5. Generation
The Concept: The final step where the Large Language Model takes the newly augmented prompt (User Query + Injected Context) and generates a human-readable, synthesized answer based only on the provided context.
In code: We use LangChain's LCEL (LangChain Expression Language) pipeline (chain = ... | prompt | self.llm | StrOutputParser()). This automatically pipes the assembled context_str and the user's question into your PromptTemplate, sends it to the OpenRouter Chat model, and parses the raw output back into a string.
