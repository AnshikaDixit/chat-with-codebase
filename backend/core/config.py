import os
from dotenv import load_dotenv

# Load env variables from the parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class Settings:
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str | None = os.getenv("QDRANT_API_KEY", None)
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY", None)
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    COLLECTION_NAME: str = "codebase_collection"
    VECTOR_SIZE: int = 384

settings = Settings()
