from pathlib import Path
from typing import Dict, List, Optional
import logging
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from ..utils.rag_utils import initialize_embeddings, load_documents, create_vector_store
from ..utils.database import get_all_tables
from ..utils.chatbot.chains import ChainBuilder

logger = logging.getLogger(__name__)

class RAGService:
    """Service class for handling RAG (Retrieval Augmented Generation) functionality"""
    
    @staticmethod
    def initialize_components():
        """Initialize RAG components in session state"""
        if 'rag_initialized' not in st.session_state:
            try:
                api_key = RAGService._get_api_key()
                if not api_key:
                    return
                    
                embeddings = initialize_embeddings(api_key)
                documents = RAGService._load_documents()
                if not documents:
                    return
                    
                vector_store = create_vector_store(documents, embeddings)
                if not vector_store:
                    return
                    
                RAGService._initialize_memory_and_state(vector_store, documents)
                logger.info("RAG components initialized successfully")
                    
            except Exception as e:
                logger.error(f"Error initializing RAG components: {e}")
                st.session_state['rag_initialized'] = False
    
    @staticmethod
    def process_query(question: str, selected_tables: Optional[List[str]] = None) -> Dict:
        """
        Process query using RAG enhancement
        
        Args:
            question (str): The user's question
            selected_tables (Optional[List[str]]): List of selected tables to query
        
        Returns:
            Dict: Processed query result with context
        """
        try:
            if not st.session_state.get('rag_initialized'):
                return {'question': question, 'error': 'RAG not initialized'}
            
            context = RAGService._get_relevant_context(question)
            chat_history = RAGService._get_chat_history()
            
            query = RAGService._generate_enhanced_query(
                question, 
                context, 
                chat_history, 
                selected_tables
            )
            
            RAGService._update_memory(question, query)
            
            return {
                'question': question,
                'query': query,
                'context_used': [doc.page_content for doc in context],
                'chat_history': chat_history
            }
            
        except Exception as e:
            logger.error(f"Error processing RAG query: {e}")
            return {
                'question': question,
                'error': str(e)
            }
    
    @staticmethod
    def _get_api_key() -> Optional[str]:
        """Get OpenAI API key from session state"""
        api_key = st.session_state.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API key not found in session state")
            st.session_state['rag_initialized'] = False
        return api_key
    
    @staticmethod
    def _load_documents():
        """Load documents from the docs directory"""
        try:
            cwd = Path.cwd()
            docs_path = Path("docs")
            if not docs_path.exists():
                docs_path = cwd / "docs"
            
            logger.info(f"Looking for documents in: {docs_path}")
            documents = load_documents(docs_path)
            
            if not documents:
                logger.warning("No documents found, RAG will be disabled")
                st.session_state['rag_initialized'] = False
                return None
                
            return documents
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            st.session_state['rag_initialized'] = False
            return None
    
    @staticmethod
    def _initialize_memory_and_state(vector_store, documents):
        """Initialize memory and session state variables"""
        msgs = StreamlitChatMessageHistory(key="langchain_messages")
        memory = ConversationBufferMemory(
            chat_memory=msgs,
            memory_key="chat_history",
            return_messages=True
        )
        
        st.session_state['vector_store'] = vector_store
        st.session_state['conversation_memory'] = memory
        st.session_state['rag_initialized'] = True
        st.session_state['docs_loaded'] = [
            str(doc.metadata.get('source', 'Unknown')) 
            for doc in documents
        ]
    
    @staticmethod
    def _get_relevant_context(question: str):
        """Get relevant context from vector store"""
        vector_store = st.session_state.get('vector_store')
        return vector_store.similarity_search(question, k=3) if vector_store else []
    
    @staticmethod
    def _get_chat_history():
        """Get chat history from memory"""
        memory = st.session_state.get('conversation_memory')
        return memory.load_memory_variables({}).get('chat_history', '') if memory else ""
    
    @staticmethod
    def _generate_enhanced_query(question: str, context: List, 
                               chat_history: str, selected_tables: Optional[List[str]]) -> str:
        """Generate enhanced SQL query using context"""
        enhanced_prompt = f"""
        Based on:
        - Previous conversation: {chat_history}
        - Context: {[doc.page_content for doc in context]}
        - Selected tables: {selected_tables if selected_tables else 'all tables'}
        - Question: {question}
        
        Generate an appropriate SQL query using only the selected tables.
        """
        
        sql_chain = ChainBuilder.build_sql_chain()
        return sql_chain.invoke({
            "question": enhanced_prompt,
            "selected_tables": selected_tables
        })
    
    @staticmethod
    def _update_memory(question: str, query: str):
        """Update conversation memory"""
        memory = st.session_state.get('conversation_memory')
        if memory:
            memory.save_context(
                {"question": question},
                {"answer": str(query)}
            )