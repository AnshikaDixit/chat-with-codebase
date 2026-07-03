from pydantic import BaseModel
from typing import Dict, Any, Optional

class IngestRequest(BaseModel):
    repo_url: str

class ChatRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
