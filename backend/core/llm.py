import functools
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_openai import ChatOpenAI
from core.config import settings

@functools.lru_cache()
def get_embeddings():
    return FastEmbedEmbeddings(model_name=settings.EMBEDDING_MODEL)

def get_llm():
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set.")
    return ChatOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model="openrouter/free",
    )
