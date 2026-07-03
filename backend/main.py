from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

# This must be imported first to ensure env variables load properly
from core.config import settings

from models.schemas import IngestRequest, ChatRequest
from services.ingestion import IngestionService
from services.rag import RagService

app = FastAPI(title="Chat with Codebase API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest_repo")
async def ingest_repo(request: IngestRequest, ingestion_service: IngestionService = Depends()):
    if not request.repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    
    try:
        num_chunks = ingestion_service.process_repository(request.repo_url)
        return {"status": "success", "message": f"Repository ingested successfully. Created {num_chunks} chunks."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest, rag_service: RagService = Depends()):
    try:
        result = rag_service.chat_with_repo(request.query, request.filters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
