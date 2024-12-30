from typing import List, Dict, Any
import logging
from ...utils.database import run_query
from .prompts import ChatbotPrompts
from ...utils.llm_provider import LLMProvider
import streamlit as st

logger = logging.getLogger(__name__)

class InsightGenerator:
    """Handles the generation of insights from database schema and data"""
    
    @staticmethod
    def get_default_insights(selected_tables: List[str]) -> List[Dict]:
        """
        Get basic information about selected tables and generate initial summary
        """
        try:
            columns_data = []
            for table in selected_tables:
                try:
                    query = f"""
                    SELECT 
                        COUNT(*) as count,
                        COALESCE(
                            (
                                SELECT GROUP_CONCAT(COLUMN_NAME)
                                FROM INFORMATION_SCHEMA.COLUMNS
                                WHERE TABLE_NAME = '{table}'
                                AND TABLE_SCHEMA = DATABASE()
                            ),
                            ''
                        ) as columns
                    FROM {table}
                    """
                    result = run_query(query)
                    if result and len(result) > 0:
                        row = result[0]
                        count = row[0] if len(row) > 0 else 0
                        columns = row[1] if len(row) > 1 else ''
                        
                        columns_data.append({
                            "table": table,
                            "count": count,
                            "columns": columns.split(',') if columns else []
                        })
                    else:
                        columns_data.append({
                            "table": table,
                            "count": 0,
                            "columns": []
                        })
                except Exception as e:
                    logger.error(f"Error getting info for table {table}: {str(e)}")
                    columns_data.append({
                        "table": table,
                        "count": 0,
                        "columns": []
                    })
            
            return columns_data

        except Exception as e:
            logger.error(f"Error getting default insights: {str(e)}")
            return []

    @staticmethod
    def generate_schema_suggestions(schema_data: List[Dict]) -> str:
        """Generate query suggestions based on schema"""
        try:
            prompt = ChatbotPrompts.get_schema_suggestions_prompt()
            
            llm = LLMProvider.get_llm(
                provider=st.session_state.get('llm_provider', 'openai'),
                model_name=st.session_state.get('llm_model_name'),
                temperature=st.session_state.get('llm_temperature', 0.7)
            )
            
            from langchain_core.output_parsers import StrOutputParser
            chain = prompt | llm | StrOutputParser()
            
            suggestions = chain.invoke({"schema_data": str(schema_data)})
            return suggestions
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return ""
    
    @staticmethod
    def format_schema_overview(schema_data: List[Dict]) -> str:
        """Format schema information in a readable way"""
        try:
            overview = []
            for table in schema_data:
                overview.append(f"""
Tabla: {table['table']}
- Columnas ({len(table['columns'])}): {', '.join(table['columns'])}
- Registros: {table['count']}
""")
            return '\n'.join(overview)
        except Exception as e:
            logger.error(f"Error formatting schema overview: {str(e)}")
            return ""