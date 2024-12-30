# src/services/data_processing.py
import streamlit as st
import pandas as pd
import logging
from typing import Optional, Dict, List, Any
#from src.utils.chatbot import generate_sql_chain, generate_response_chain
from src.utils.chatbot.chains import ChainBuilder
from src.utils.chatbot.query import QueryProcessor
from src.utils.chatbot.response import ResponseProcessor
from src.services.state_management import store_debug_log
#from src.services.rag_service import process_query_with_rag
from src.services.rag_service import RAGService

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# src/services/data_processing.py

def handle_query_and_response(question: str, selected_tables: List[str]) -> Dict[str, Any]:
    """Process a query and generate a response"""
    try:
        if 'debug_logs' not in st.session_state:
            st.session_state['debug_logs'] = []
            
        # Usar QueryProcessor para manejar toda la lógica de procesamiento
        response_data = QueryProcessor.process_query_and_response(question, selected_tables)
        
        # Almacenar en debug_logs
        store_debug_log({
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'question': question,
            'query': response_data.get('query'),
            'full_response': response_data.get('response'),
            'has_visualization': response_data.get('visualization_data') is not None,
            'rag_enabled': st.session_state.get('rag_initialized', False),
            'selected_tables': selected_tables,
            'rag_context': response_data.get('rag_context', [])
        })
        
        return response_data
            
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        
        # Usar ResponseProcessor para manejar errores
        error_response = ResponseProcessor.handle_error_response(
            question=question,
            error=str(e),
            selected_tables=selected_tables
        )
        
        # Almacenar error en debug_logs
        store_debug_log({
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'question': question,
            'error': str(e),
            'selected_tables': selected_tables
        })
        
        return error_response