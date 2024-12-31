from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import logging
import streamlit as st
from decimal import Decimal

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
                
            main_response, data_str = response.split("DATA:", 1)
            main_response = main_response.strip()
            data_str = data_str.strip()
            
            if not data_str:
                return main_response, None
            
            try:
                # Limpiar y normalizar el string de datos
                data_str = data_str.replace(' ', '')  # Remover espacios
                
                # Intentar extraer la lista usando expresiones regulares
                import re
                matches = re.findall(r'\(([^)]+)\)', data_str)
                
                if not matches:
                    return main_response, None
                    
                data_list = []
                for match in matches:
                    try:
                        # Separar la categoría y el valor
                        parts = match.split(',', 1)
                        if len(parts) != 2:
                            continue
                            
                        category = parts[0].strip('"\'')
                        # Limpiar y convertir el valor numérico
                        value_str = parts[1].strip().replace('_', '')
                        
                        # Manejar diferentes formatos numéricos
                        try:
                            value = float(value_str)
                        except ValueError:
                            # Si falla, intentar limpiar el string
                            clean_value = re.sub(r'[^\d.-]', '', value_str)
                            value = float(clean_value)
                            
                        data_list.append((category, value))
                    except Exception as e:
                        logger.warning(f"Error processing data item {match}: {str(e)}")
                        continue
                
                if not data_list:
                    return main_response, None
                    
                visualization_data = [
                    {
                        "Categoría": str(item[0] if isinstance(item, (tuple, list)) else item.get('category', '')),
                        "Cantidad": float(item[1] if isinstance(item, (tuple, list)) else item.get('value', 0))
                    }
                    for item in data_list
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
                'schema_overview': None
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