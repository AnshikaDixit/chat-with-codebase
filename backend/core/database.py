import functools
from fastapi import Depends
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore

from core.config import settings
from core.llm import get_embeddings

@functools.lru_cache()
def get_qdrant_client():
    return QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

def get_vector_store(client: QdrantClient = Depends(get_qdrant_client)):
    # Ensure collection exists
    if not client.collection_exists(settings.COLLECTION_NAME):
        client.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=VectorParams(size=settings.VECTOR_SIZE, distance=Distance.COSINE),
        )
    
    # Try to ensure indexes exist (Qdrant requires this for filtering)
    try:
        from qdrant_client.http.models import PayloadSchemaType
        client.create_payload_index(
            collection_name=settings.COLLECTION_NAME,
            field_name="metadata.repo_url",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        client.create_payload_index(
            collection_name=settings.COLLECTION_NAME,
            field_name="metadata.folder_path",
            field_schema=PayloadSchemaType.KEYWORD,
        )
    except Exception:
        pass # Ignore if they already exist
        
    return QdrantVectorStore(
        client=client,
        collection_name=settings.COLLECTION_NAME,
        embedding=get_embeddings(),
    )
