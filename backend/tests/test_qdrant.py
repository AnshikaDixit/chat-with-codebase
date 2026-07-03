import os
from dotenv import load_dotenv
load_dotenv(".env")
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
try:
    print(client.get_collection("codebase_collection"))
    res = client.scroll(
        collection_name="codebase_collection",
        scroll_filter=Filter(
            must=[FieldCondition(key="metadata.repo_url", match=MatchValue(value="https://github.com/some/repo"))]
        ),
        limit=1
    )
    print("Search by metadata.repo_url:", res)
except Exception as e:
    print(e)
