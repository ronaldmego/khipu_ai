from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import logging
import streamlit as st  # Añadimos esta importación

logger = logging.getLogger(__name__)

class ResponseProcessor:
    """Handles the processing and formatting of responses"""
    
    @staticmethod
    def process_visualization_data(response: str) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
        """
        Extract and process visualization data from response
        
        Args:
            response (str): The full response string
            
        Returns:
            Tuple containing:
            - str: The main response without visualization data
            - Optional[List[Dict[str, Any]]]: Processed visualization data if available
        """
        try:
            if "DATA:" not in response:
                return response, None
                
            main_response, data_str = response.split("DATA:")
            main_response = main_response.strip()
            data_str = data_str.strip()
            
            if not data_str:
                return main_response, None
            
            try:
                data_list = eval(data_str)
                if not isinstance(data_list, (list, tuple)) or not data_list:
                    return main_response, None
                    
                visualization_data = [
                    {"Categoría": str(cat), "Cantidad": float(count)}
                    for cat, count in data_list
                ]
                return main_response, visualization_data
                
            except Exception as e:
                logger.error(f"Error parsing data list: {str(e)}")
                return main_response, None
            
        except Exception as e:
            logger.error(f"Error processing visualization data: {str(e)}")
            return response, None
    
    @staticmethod
    def format_response(question: str, query: str, response: str, 
                       selected_tables: List[str]) -> Dict[str, Any]:
        """
        Format the final response with all components
        
        Args:
            question (str): Original question
            query (str): Generated SQL query
            response (str): Raw response from LLM
            selected_tables (List[str]): List of selected tables
            
        Returns:
            Dict[str, Any]: Formatted response
        """
        try:
            # Process visualization data
            main_response, visualization_data = ResponseProcessor.process_visualization_data(response)
            
            formatted_response = {
                'question': question,
                'query': query,
                'response': main_response,
                'visualization_data': visualization_data,
                'selected_tables': selected_tables,
                'schema_overview': None  # Puedes añadir esto si lo necesitas
            }
            
            # Add RAG context if available
            if 'last_context' in st.session_state:
                formatted_response['rag_context'] = st.session_state.get('last_context', [])
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            return {
                'question': question,
                'response': f"Error formatting response: {str(e)}",
                'query': query,
                'visualization_data': None,
                'selected_tables': selected_tables
            }
            
    @staticmethod
    def handle_error_response(question: str, error: str, selected_tables: List[str]) -> Dict[str, Any]:
        """
        Create an error response
        
        Args:
            question (str): Original question
            error (str): Error message
            selected_tables (List[str]): Selected tables
            
        Returns:
            Dict[str, Any]: Error response
        """
        return {
            'question': question,
            'response': f"Lo siento, hubo un error al procesar tu consulta: {error}",
            'query': None,
            'visualization_data': None,
            'selected_tables': selected_tables,
            'rag_context': []
        }