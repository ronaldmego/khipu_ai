# src/utils/rag_utils.py
from langchain_openai import OpenAIEmbeddings  # Actualizado
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from typing import List, Dict, Optional
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

def initialize_embeddings(api_key: str):
    """Initialize OpenAI embeddings"""
    try:
        return OpenAIEmbeddings(openai_api_key=api_key)
    except Exception as e:
        logger.error(f"Error initializing embeddings: {e}")
        raise

def load_documents(docs_path: Path) -> List:
    """Load documents from various sources"""
    documents = []
    
    # Log the absolute path being checked
    abs_path = docs_path.absolute()
    logger.info(f"Checking for documents in: {abs_path}")
    
    if not docs_path.exists():
        logger.warning(f"Documents directory {abs_path} does not exist")
        # Create the directory if it doesn't exist
        docs_path.mkdir(parents=True, exist_ok=True)
        return documents
        
    # Log existing files in directory
    files = list(docs_path.glob('**/*'))
    logger.info(f"Files found in docs directory: {[str(f) for f in files]}")

    # Load PDFs
    pdf_loader = DirectoryLoader(str(docs_path), glob="**/*.pdf", loader_cls=PyPDFLoader)
    # Load text files
    text_loader = DirectoryLoader(str(docs_path), glob="**/*.txt", loader_cls=TextLoader)
    # Load markdown files
    md_loader = DirectoryLoader(str(docs_path), glob="**/*.md", loader_cls=TextLoader)
    
    try:
        # Load each type separately with error handling
        try:
            pdf_docs = pdf_loader.load()
            logger.info(f"Loaded {len(pdf_docs)} PDF documents")
            documents.extend(pdf_docs)
        except Exception as e:
            logger.error(f"Error loading PDFs: {e}")
            
        try:
            txt_docs = text_loader.load()
            logger.info(f"Loaded {len(txt_docs)} text documents")
            documents.extend(txt_docs)
        except Exception as e:
            logger.error(f"Error loading text files: {e}")
            
        try:
            md_docs = md_loader.load()
            logger.info(f"Loaded {len(md_docs)} markdown documents")
            documents.extend(md_docs)
        except Exception as e:
            logger.error(f"Error loading markdown files: {e}")
        
        if not documents:
            logger.warning("No documents were successfully loaded")
        else:
            logger.info(f"Successfully loaded total of {len(documents)} documents")
            for doc in documents:
                logger.info(f"Loaded: {doc.metadata.get('source', 'Unknown source')}")
            
        return documents
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        return documents

def create_vector_store(documents: List, embeddings) -> Optional[FAISS]:
    """Create FAISS vector store from documents"""
    try:
        if not documents:
            logger.warning("No documents provided for vector store creation")
            return None
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False
        )
        chunks = text_splitter.split_documents(documents)
        
        if not chunks:
            logger.warning("No chunks created from documents")
            return None
            
        vector_store = FAISS.from_documents(chunks, embeddings)
        logger.info("Vector store created successfully")
        return vector_store
        
    except Exception as e:
        logger.error(f"Error creating vector store: {e}")
        return None