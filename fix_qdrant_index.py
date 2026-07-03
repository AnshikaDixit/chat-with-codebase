import os
from dotenv import load_dotenv
load_dotenv(".env")
from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
try:
    print("Creating index for metadata.repo_url...")
    client.create_payload_index(
        collection_name="codebase_collection",
        field_name="metadata.repo_url",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    print("Creating index for metadata.folder_path...")
    client.create_payload_index(
        collection_name="codebase_collection",
        field_name="metadata.folder_path",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    print("Indexes created successfully.")
except Exception as e:
    print(f"Failed to create index: {e}")
