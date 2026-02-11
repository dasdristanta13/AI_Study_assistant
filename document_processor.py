"""
Document Processing Utilities
Handles loading and processing of various document types
"""
import os
from typing import List, Optional
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
from langchain_core.documents import Document

from config import Config


class DocumentProcessor:
    """Process various document types and extract text"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load document based on file extension"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            loader = PyPDFLoader(file_path)
        elif extension == '.docx':
            loader = Docx2txtLoader(file_path)
        elif extension == '.txt':
            loader = TextLoader(file_path)
        elif extension == '.md':
            loader = UnstructuredMarkdownLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
        
        return loader.load()
    
    def process_document(self, file_path: str) -> tuple[str, List[Document]]:
        """Load and split document into chunks"""
        # Load document
        documents = self.load_document(file_path)
        
        # Get raw content
        raw_content = "\n\n".join([doc.page_content for doc in documents])
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        return raw_content, chunks
    
    def process_text(self, text: str, source: str = "direct_input") -> tuple[str, List[Document]]:
        """Process raw text input"""
        # Create a document from text
        document = Document(page_content=text, metadata={"source": source})
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([document])
        
        return text, chunks
    
    def extract_key_info(self, documents: List[Document]) -> dict:
        """Extract metadata and key information from documents"""
        total_chars = sum(len(doc.page_content) for doc in documents)
        
        return {
            "num_chunks": len(documents),
            "total_characters": total_chars,
            "avg_chunk_size": total_chars // len(documents) if documents else 0,
            "sources": list(set(doc.metadata.get("source", "unknown") for doc in documents))
        }


def validate_file_path(file_path: str) -> bool:
    """Validate if file exists and is supported"""
    path = Path(file_path)
    
    if not path.exists():
        return False
    
    if path.suffix.lower() not in Config.SUPPORTED_FILE_TYPES:
        return False
    
    return True