import sys
import os
import pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app
from services.ingestion import IngestionService
from services.rag import RagService

# Create mock classes for our services
class MockIngestionService:
    def process_repository(self, repo_url: str) -> int:
        return 42  # Return a mock chunk count

class MockRagService:
    def chat_with_repo(self, query: str, filters: dict = None) -> dict:
        return {
            "answer": "This is a mocked answer for the tests.",
            "citations": [{"file_path": "mock_file.py", "content": "mock content"}]
        }

# Setup dependency overrides for testing
app.dependency_overrides[IngestionService] = MockIngestionService
app.dependency_overrides[RagService] = MockRagService

client = TestClient(app)

def test_ingest_repo_success():
    response = client.post("/ingest_repo", json={"repo_url": "https://github.com/octocat/Spoon-Knife"})
    assert response.status_code == 200
    assert response.json() == {
        "status": "success", 
        "message": "Repository ingested successfully. Created 42 chunks."
    }

def test_ingest_repo_invalid_url():
    response = client.post("/ingest_repo", json={"repo_url": "https://gitlab.com/test/repo"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid GitHub URL"

def test_chat_success():
    response = client.post("/chat", json={"query": "What is this?", "filters": {}})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a mocked answer for the tests."
    assert len(data["citations"]) == 1
    assert data["citations"][0]["file_path"] == "mock_file.py"
