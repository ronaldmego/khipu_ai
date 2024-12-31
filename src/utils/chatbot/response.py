from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import logging
import streamlit as st
from decimal import Decimal
import re
from datetime import datetime, date

logger = logging.getLogger(__name__)

class ResponseProcessor:
    """Handles the processing and formatting of responses"""
    
    @staticmethod
    def process_visualization_data(response: str, query_result: Optional[List[Tuple]] = None) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
        """
        Extract and process visualization data with enhanced capabilities
        
        Args:
            response (str): The full response string
            query_result (Optional[List[Tuple]]): Raw query results
            
        Returns:
            Tuple containing:
            - str: The main response without visualization data
            - Optional[List[Dict[str, Any]]]: Processed visualization data if available
        """
        try:
            # Si ya hay datos de visualización en el formato esperado
            if "DATA:" in response:
                main_response, data_str = response.split("DATA:", 1)
                # Procesar datos existentes
                visualization_data = ResponseProcessor._process_existing_data(data_str)
                if visualization_data:
                    return main_response, visualization_data
            
            # Si no hay datos de visualización, intentar generarlos del query_result
            if query_result and len(query_result) > 0:
                # Detectar tipo de datos y crear visualización apropiada
                if ResponseProcessor._is_ranking_data(query_result):
                    visualization_data = ResponseProcessor.create_ranking_visualization(query_result)
                elif ResponseProcessor._is_temporal_data(query_result):
                    visualization_data = ResponseProcessor.create_temporal_visualization(query_result)
                else:
                    visualization_data = ResponseProcessor.create_default_visualization(query_result)
                
                return response, visualization_data
            
            return response, None
            
        except Exception as e:
            logger.error(f"Error processing visualization data: {str(e)}")
            return response, None

    @staticmethod
    def _process_existing_data(data_str: str) -> Optional[List[Dict[str, Any]]]:
        """Procesa datos existentes en formato DATA:[...]"""
        try:
            data_str = data_str.strip()
            if not data_str:
                return None
            
            # Limpiar y normalizar el string de datos
            data_str = data_str.replace(' ', '')  # Remover espacios
            
            # Extraer tuplas usando regex
            matches = re.findall(r'\(([^)]+)\)', data_str)
            if not matches:
                return None
            
            visualization_data = []
            for match in matches:
                try:
                    # Separar categoría y valor
                    parts = match.split(',', 1)
                    if len(parts) != 2:
                        continue
                    
                    category = parts[0].strip('"\'')
                    value_str = parts[1].strip().replace('_', '')
                    
                    # Convertir valor a número
                    try:
                        value = float(value_str)
                    except ValueError:
                        clean_value = re.sub(r'[^\d.-]', '', value_str)
                        value = float(clean_value)
                    
                    visualization_data.append({
                        "Categoría": category,
                        "Cantidad": value
                    })
                except Exception as e:
                    logger.warning(f"Error processing data item {match}: {str(e)}")
                    continue
            
            return visualization_data if visualization_data else None
            
        except Exception as e:
            logger.error(f"Error processing existing data: {str(e)}")
            return None

    @staticmethod
    def _is_ranking_data(query_result: List[Tuple]) -> bool:
        """Determina si los datos son tipo ranking"""
        try:
            if not query_result or len(query_result) == 0:
                return False
                
            # Verificar si hay una columna numérica al final o cerca del final
            row = query_result[0]
            for i in range(len(row)-1, max(len(row)-4, -1), -1):
                if isinstance(row[i], (int, float, Decimal)):
                    return True
            
            return False
        except Exception:
            return False

    @staticmethod
    def _is_temporal_data(query_result: List[Tuple]) -> bool:
        """Determina si los datos contienen series temporales"""
        try:
            if not query_result or len(query_result) == 0:
                return False
            
            # Buscar columnas de fecha
            row = query_result[0]
            for value in row:
                if isinstance(value, (datetime, date)):
                    return True
            
            # Buscar nombres de columna que sugieran fechas
            date_keywords = ['fecha', 'date', 'year', 'month', 'año', 'mes']
            for i, value in enumerate(row):
                if isinstance(value, str) and any(keyword in value.lower() for keyword in date_keywords):
                    return True
            
            return False
        except Exception:
            return False
        
    @staticmethod
    def create_ranking_visualization(query_result: List[Tuple]) -> List[Dict[str, Any]]:
        """Crear visualización para rankings"""
        try:
            visualization_data = []
            
            # Identificar columnas numéricas
            numeric_cols = [i for i, value in enumerate(query_result[0]) 
                          if isinstance(value, (int, float, Decimal))]
            
            # Usar la última columna numérica como valor por defecto
            value_col = numeric_cols[-1] if numeric_cols else -1
            
            # Buscar una columna de texto para las etiquetas
            text_cols = [i for i, value in enumerate(query_result[0]) 
                        if isinstance(value, str) and len(value) < 100]
            label_col = text_cols[0] if text_cols else 0
            
            for row in query_result:
                try:
                    category = str(row[label_col])
                    value = float(row[value_col]) if isinstance(row[value_col], (int, float, Decimal)) else 0
                    visualization_data.append({
                        "Categoría": category,
                        "Cantidad": value
                    })
                except Exception as e:
                    logger.warning(f"Error processing row for visualization: {str(e)}")
                    continue
            
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error creating ranking visualization: {str(e)}")
            return []
        
    @staticmethod
    def create_temporal_visualization(query_result: List[Tuple]) -> List[Dict[str, Any]]:
        """Crear visualización para datos temporales"""
        try:
            visualization_data = []
            
            # Identificar columna de fecha
            date_col = next((i for i, value in enumerate(query_result[0]) 
                           if isinstance(value, (datetime, date))), 0)
            
            # Identificar columna numérica
            numeric_col = next((i for i, value in enumerate(query_result[0]) 
                              if isinstance(value, (int, float, Decimal))), -1)
            
            for row in query_result:
                try:
                    date_value = row[date_col]
                    if isinstance(date_value, (datetime, date)):
                        date_str = date_value.strftime("%Y-%m")
                    else:
                        date_str = str(date_value)
                    
                    value = float(row[numeric_col]) if isinstance(row[numeric_col], (int, float, Decimal)) else 0
                    
                    visualization_data.append({
                        "Categoría": date_str,
                        "Cantidad": value
                    })
                except Exception as e:
                    logger.warning(f"Error processing temporal row: {str(e)}")
                    continue
            
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error creating temporal visualization: {str(e)}")
            return []
        
    @staticmethod
    def create_default_visualization(query_result: List[Tuple]) -> List[Dict[str, Any]]:
        """Crear visualización por defecto para otros tipos de datos"""
        try:
            visualization_data = []
            
            for row in query_result:
                try:
                    # Buscar el mejor par de valores para categoría y cantidad
                    category = None
                    value = None
                    
                    # Buscar el primer valor string para categoría
                    for item in row:
                        if isinstance(item, str) and len(item) < 100:
                            category = item
                            break
                    
                    # Buscar el primer valor numérico para cantidad
                    for item in row:
                        if isinstance(item, (int, float, Decimal)):
                            value = float(item)
                            break
                    
                    if category is None:
                        category = str(row[0] if len(row) > 0 else "N/A")
                    if value is None:
                        value = float(row[1]) if len(row) > 1 and isinstance(row[1], (int, float, Decimal)) else 0
                    
                    visualization_data.append({
                        "Categoría": category,
                        "Cantidad": value
                    })
                except Exception as e:
                    logger.warning(f"Error processing default row: {str(e)}")
                    continue
            
            return visualization_data
            
        except Exception as e:
            logger.error(f"Error creating default visualization: {str(e)}")
            return []

    @staticmethod
    def format_response(question: str, query: str, response: str, 
                       selected_tables: List[str], 
                       query_result: Optional[List[Tuple]] = None) -> Dict[str, Any]:
        """Format the final response with all components"""
        try:
            # Process visualization data with query results
            main_response, visualization_data = ResponseProcessor.process_visualization_data(
                response, query_result)
            
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
        """Create an error response"""
        return {
            'question': question,
            'response': f"Lo siento, hubo un error al procesar tu consulta: {error}",
            'query': None,
            'visualization_data': None,
            'selected_tables': selected_tables,
            'rag_context': []
        }