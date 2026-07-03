import os
from pathlib import Path
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List

SUPPORTED_EXTENSIONS = {
    ".py": Language.PYTHON,
    ".md": Language.MARKDOWN,
    ".dart": Language.MARKDOWN, # Dart fallback
    ".js": Language.JS,
}

class ChunkingService:
    def process_directory(self, directory_path: str, repo_url: str) -> List[Document]:
        """Walks through the directory, reads supported files, and splits them into chunks."""
        documents = []
        for root, _, files in os.walk(directory_path):
            if ".git" in root:
                continue
            for file in files:
                ext = Path(file).suffix
                if ext in SUPPORTED_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        rel_path = os.path.relpath(file_path, directory_path)
                        language = SUPPORTED_EXTENSIONS[ext]
                        
                        if language == Language.MARKDOWN:
                            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                        else:
                            splitter = RecursiveCharacterTextSplitter.from_language(
                                language=language, chunk_size=1000, chunk_overlap=200
                            )
                        
                        chunks = splitter.create_documents(
                            [content], 
                            metadatas=[{"file_name": file, "language": ext, "folder_path": rel_path, "repo_url": repo_url}]
                        )
                        documents.extend(chunks)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
        return documents
