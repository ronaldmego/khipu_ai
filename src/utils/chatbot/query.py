from typing import Dict, Any, List, Optional
import logging
from .chains import ChainBuilder
from .response import ResponseProcessor
from ..database import get_schema, run_query
import streamlit as st

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Handles query processing and execution"""
    
    @staticmethod
    def process_query_and_response(question: str, selected_tables: List[str]) -> Dict[str, Any]:
        """
        Process a query and generate a response
        
        Args:
            question (str): User's question
            selected_tables (List[str]): List of selected tables
            
        Returns:
            Dict[str, Any]: Processed response with all components
        """
        try:
            # Check RAG availability
            if st.session_state.get('rag_initialized') and st.session_state.get('rag_enabled', True):
                return QueryProcessor._process_with_rag(question, selected_tables)
            else:
                return QueryProcessor._process_without_rag(question, selected_tables)
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return ResponseProcessor.handle_error_response(question, str(e), selected_tables)
    
    @staticmethod
    def _process_with_rag(question: str, selected_tables: List[str]) -> Dict[str, Any]:
        """Process query using RAG enhancement"""
        try:
            #from ...services.rag_service import process_query_with_rag
            from ...services.rag_service import RAGService
            
            # Get RAG enhanced query
            rag_response = RAGService.process_query(question, selected_tables)
            query = rag_response.get('query', '')
            context_used = rag_response.get('context_used', [])
            st.session_state['last_context'] = context_used
            
            # Generate response using the enhanced query
            full_chain = ChainBuilder.build_response_chain(ChainBuilder.build_sql_chain())
            full_response = full_chain.invoke({
                "question": question,
                "query": query,
                "selected_tables": selected_tables
            })
            
            # Add RAG indicator to response
            full_response = "🧠 " + str(full_response)
            
            return ResponseProcessor.format_response(
                question=question,
                query=query,
                response=full_response,
                selected_tables=selected_tables
            )
            
        except Exception as e:
            logger.error(f"Error in RAG processing: {str(e)}")
            return ResponseProcessor.handle_error_response(question, str(e), selected_tables)
    
    @staticmethod
    def _process_without_rag(question: str, selected_tables: List[str]) -> Dict[str, Any]:
        """Process query without RAG"""
        try:
            # Generate SQL query
            sql_chain = ChainBuilder.build_sql_chain()
            query = sql_chain.invoke({
                "question": question,
                "selected_tables": selected_tables
            })
            
            # Generate full response
            full_chain = ChainBuilder.build_response_chain(sql_chain)
            full_response = full_chain.invoke({
                "question": question,
                "query": query,
                "selected_tables": selected_tables
            })
            
            return ResponseProcessor.format_response(
                question=question,
                query=query,
                response=full_response,
                selected_tables=selected_tables
            )
            
        except Exception as e:
            logger.error(f"Error in standard processing: {str(e)}")
            return ResponseProcessor.handle_error_response(question, str(e), selected_tables)
    
    @staticmethod
    def get_schema_overview(selected_tables: List[str]) -> Dict[str, Any]:
        """
        Get an overview of the database schema for selected tables
        
        Args:
            selected_tables (List[str]): List of selected tables
            
        Returns:
            Dict[str, Any]: Schema overview response
        """
        try:
            from .insights import InsightGenerator
            
            schema_data = InsightGenerator.get_default_insights(selected_tables)
            suggestions = InsightGenerator.generate_schema_suggestions(schema_data)
            overview = InsightGenerator.format_schema_overview(schema_data)
            
            response = f"""
Aquí está un resumen de los datos disponibles:

{overview}

Algunas preguntas que podrías hacer:
{suggestions}
            """
            
            # Create visualization data from schema info
            visualization_data = [
                {"Categoría": table["table"], "Cantidad": len(table["columns"])}
                for table in schema_data
            ]
            
            return {
                'question': "Visión general de la base de datos",
                'response': response,
                'query': "SELECT * FROM information_schema.columns WHERE table_schema = DATABASE()",
                'visualization_data': visualization_data,
                'selected_tables': selected_tables,
                'schema_overview': overview
            }
            
        except Exception as e:
            logger.error(f"Error getting schema overview: {str(e)}")
            return ResponseProcessor.handle_error_response(
                "Visión general de la base de datos",
                str(e),
                selected_tables
            )