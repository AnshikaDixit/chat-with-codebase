import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_ingest_repo():
    # Using a small repo that definitely has .md files
    response = client.post("/ingest_repo", json={"repo_url": "https://github.com/octocat/Spoon-Knife"})
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "success"
    assert "Created" in response.json()["message"]

def test_chat():
    response = client.post("/chat", json={"query": "What is FastAPI?", "filters": {}})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert isinstance(data["citations"], list)
