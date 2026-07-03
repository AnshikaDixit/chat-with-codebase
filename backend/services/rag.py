import os
from typing import Dict, Any, List
from fastapi import Depends
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http import models
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from core.database import get_vector_store
from core.llm import get_llm

class RagService:
    def __init__(
        self,
        vector_store: QdrantVectorStore = Depends(get_vector_store),
        llm: ChatOpenAI = Depends(get_llm)
    ):
        self.vector_store = vector_store
        self.llm = llm

    def chat_with_repo(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retrieves context and generates an answer using LLM."""
        # We apply a metadata filter if provided
        search_kwargs = {"k": 20}
        must_conditions = []
        
        if filters:
            if filters.get("folder_path"):
                must_conditions.append(models.FieldCondition(key="metadata.folder_path", match=models.MatchValue(value=filters["folder_path"])))
            if filters.get("repo_url"):
                must_conditions.append(models.FieldCondition(key="metadata.repo_url", match=models.MatchValue(value=filters["repo_url"])))
                
        if must_conditions:
            search_kwargs["filter"] = models.Filter(must=must_conditions)
            
        retriever = self.vector_store.as_retriever(search_kwargs=search_kwargs)
        
        # Get relevant chunks
        docs = retriever.invoke(query)
        
        # If the user explicitly asks for file contents, try to find that file specifically
        import re
        # Require a file extension in the regex so we don't accidentally match function names
        file_match = re.search(r'(?:contents of|show me|what is in|code for|read)\s+([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)', query.lower())
        if file_match:
            target_file = file_match.group(1)
            file_conditions = must_conditions.copy()
            file_conditions.append(models.FieldCondition(key="metadata.file_name", match=models.MatchValue(value=target_file)))
            file_filter = models.Filter(must=file_conditions)
            
            file_retriever = self.vector_store.as_retriever(search_kwargs={"k": 20, "filter": file_filter})
            file_docs = file_retriever.invoke(query)
            
            # Merge and deduplicate docs
            seen_content = set([d.page_content for d in docs])
            for d in file_docs:
                if d.page_content not in seen_content:
                    seen_content.add(d.page_content)
                    docs.append(d)
        
        citations = []
        context_str = ""
        for doc in docs:
            file_name = doc.metadata.get("folder_path", doc.metadata.get("file_name", "unknown file"))
            if file_name not in citations:
                citations.append(file_name)
            context_str += f"--- {file_name} ---\n{doc.page_content}\n\n"
        
        template = """
        You are an expert codebase assistant.
        You have been provided with snippets from the codebase in the context below.
        IMPORTANT: Do NOT refuse to answer by claiming you lack access to local files or the system. The codebase snippets you need are provided to you in the Context section below.
        If the answer is in the Context, you must provide it. If the answer is NOT in the Context, do not guess or claim you can access it elsewhere; simply state that the provided context does not contain the answer.
        Based on the following context, please answer the user's question.
        When you answer, you MUST cite the file names (e.g. "Based on main.py...").

        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        prompt = PromptTemplate.from_template(template)
        
        chain = (
            {"context": lambda x: context_str, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        try:
            answer = chain.invoke(query)
            
            # Aggressively remove openrouter/free moderation prefixes
            answer_clean = answer.replace("User safety: safe", "").strip()
            if answer_clean.startswith("User safety: safe"):
                answer_clean = answer_clean[len("User safety: safe"):].strip()
            
            answer = answer_clean
                
            # Filter citations: include them if the LLM mentioned the full path or just the file name
            import os as os_lib
            used_citations = []
            for c in citations:
                basename = os_lib.path.basename(c)
                if c in answer or basename in answer:
                    used_citations.append(c)
            
            # If the answer is practically empty after stripping, replace it
            if not answer or "i don't know" in answer.lower():
                used_citations = []
                
        except Exception as e:
            answer = f"Error generating answer: {e}"
            used_citations = []
            
        # Log the question and answer
        import datetime
        try:
            with open("chat_log.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}]\n")
                f.write(f"Q: {query}\n")
                f.write(f"A: {answer.strip()}\n")
                f.write("-" * 40 + "\n")
        except Exception as log_e:
            print(f"Failed to log chat: {log_e}")
            
        return {
            "answer": answer.strip(),
            "citations": used_citations
        }
