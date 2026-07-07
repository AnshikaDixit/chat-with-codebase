import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.chunking_service import ChunkingService
from core.database import get_qdrant_client, get_vector_store
from services.rag import RagService
from core.llm import get_llm
from core.config import settings

def test_similarity_search():
    print("=== Testing Similarity Search Manually ===")
    
    # 1. Chunk a large file (e.g. backend/services/rag.py)
    chunker = ChunkingService()
    file_to_embed = os.path.join(os.path.dirname(__file__), "services", "rag.py")
    
    with open(file_to_embed, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We use RecursiveCharacterTextSplitter for Python
    from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
    from services.chunking_service import tiktoken_len
    
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, 
        chunk_size=250, 
        chunk_overlap=50,
        length_function=tiktoken_len
    )
    
    chunks = splitter.create_documents(
        [content], 
        metadatas=[{"file_name": "rag.py", "language": ".py", "folder_path": "backend/services", "repo_url": "local"}]
    )
    print(f"Generated {len(chunks)} chunks from rag.py.")
    
    # 2. Embed into Qdrant
    print("Embedding chunks into Qdrant...")
    client = get_qdrant_client()
    vector_store = get_vector_store(client)
    
    # Add chunks to vector store
    vector_store.add_documents(chunks)
    print("Chunks successfully embedded into Qdrant!")
    
    # 3. Query for "How does the database connect?"
    query = "How does the database connect?"
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    print(f"\nQuerying Qdrant for: '{query}'")
    results = retriever.invoke(query)
    
    print("\n--- Top 3 Similar Chunks ---")
    for i, doc in enumerate(results):
        print(f"\nResult {i+1} (Source: {doc.metadata.get('file_name')}):")
        print(doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content)
    
    print("\nTest complete.\n")

def test_full_rag_flow():
    print("=== Full RAG Flow vs No Context ===")
    client = get_qdrant_client()
    vector_store = get_vector_store(client)
    llm = get_llm()
    rag_service = RagService(vector_store=vector_store, llm=llm)
    
    query = "How is the context injected into the prompt in RagService?"
    
    # 1. Ask with Context (Full RAG Flow)
    print(f"\n1. RAG Flow (With Context)")
    print(f"Query: {query}")
    rag_response = rag_service.chat_with_repo(query)
    print(f"RAG Answer:\n{rag_response['answer']}")
    print(f"Citations: {rag_response['citations']}")
    
    # 2. Ask without Context
    print(f"\n2. LLM Only (Without Context)")
    no_context_prompt = f"Answer this question about a codebase you haven't seen: {query}"
    no_context_response = llm.invoke(no_context_prompt)
    print(f"LLM Only Answer:\n{no_context_response.content}")
    
    print("\nTest complete.")

if __name__ == "__main__":
    test_similarity_search()
    test_full_rag_flow()
