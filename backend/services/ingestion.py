from fastapi import Depends
from langchain_qdrant import QdrantVectorStore
from services.git_service import GitService
from services.chunking_service import ChunkingService
from core.database import get_vector_store

class IngestionService:
    def __init__(
        self,
        git_service: GitService = Depends(),
        chunking_service: ChunkingService = Depends(),
        vector_store: QdrantVectorStore = Depends(get_vector_store)
    ):
        self.git_service = git_service
        self.chunking_service = chunking_service
        self.vector_store = vector_store
        
    def process_repository(self, repo_url: str) -> int:
        """Orchestrates the ingestion process: cloning, chunking, and saving to vector store."""
        with self.git_service.clone_repository(repo_url) as temp_dir:
            documents = self.chunking_service.process_directory(temp_dir, repo_url)
            
            if not documents:
                return 0
                
            self.vector_store.add_documents(documents)
            return len(documents)
