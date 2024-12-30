from typing import Any, Dict
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import logging
from ...utils.database import get_schema, run_query
from .prompts import ChatbotPrompts
from ...utils.llm_provider import LLMProvider
import streamlit as st

logger = logging.getLogger(__name__)

class ChainBuilder:
    """Handles the creation and configuration of LangChain chains"""
    
    @staticmethod
    def _clean_sql_query(query: str) -> str:
        """Clean SQL query from markdown formatting and other artifacts"""
        # Remove markdown SQL markers
        query = query.replace('```sql', '').replace('```', '')
        
        # Remove any leading/trailing whitespace
        query = query.strip()
        
        # Ensure the query ends with a semicolon if it doesn't have one
        if not query.strip().endswith(';'):
            query += ';'
        
        return query

    @staticmethod
    def build_sql_chain():
        """Build the SQL generation chain"""
        try:
            prompt = ChatbotPrompts.get_sql_prompt()
            llm = LLMProvider.get_llm(
                provider=st.session_state.get('llm_provider', 'openai'),
                model_name=st.session_state.get('llm_model_name'),
                temperature=st.session_state.get('llm_temperature', 0.7)
            )
            
            return (
                RunnablePassthrough()
                | ChainBuilder._format_sql_input
                | prompt
                | llm.bind(stop=["\nSQLResult:"])
                | StrOutputParser()
                | ChainBuilder._clean_sql_query  # Añadimos el paso de limpieza
            )
        except Exception as e:
            logger.error(f"Error building SQL chain: {str(e)}")
            raise
    
    @staticmethod
    def build_response_chain(sql_chain):
        """Build the response generation chain"""
        try:
            prompt = ChatbotPrompts.get_response_prompt()
            llm = LLMProvider.get_llm(
                provider=st.session_state.get('llm_provider', 'openai'),
                model_name=st.session_state.get('llm_model_name'),
                temperature=st.session_state.get('llm_temperature', 0.7)
            )
            
            return (
                RunnablePassthrough.assign(query=sql_chain)
                .assign(schema=ChainBuilder._get_schema)
                .assign(response=ChainBuilder._run_query)
                | ChainBuilder._process_response
                | prompt
                | llm
                | StrOutputParser()
            )
        except Exception as e:
            logger.error(f"Error building response chain: {str(e)}")
            raise
    
    @staticmethod
    def _format_sql_input(vars: Dict[str, Any]) -> Dict[str, Any]:
        """Format input for SQL prompt template"""
        try:
            selected_tables = vars.get("selected_tables", [])
            schema = get_schema(selected_tables)
            table_list = "'" + "','".join(selected_tables) + "'" if selected_tables else "''"
            return {
                "schema": schema,
                "question": vars["question"],
                "table_list": table_list
            }
        except Exception as e:
            logger.error(f"Error formatting SQL input: {str(e)}")
            raise
    
    @staticmethod
    def _get_schema(vars: Dict[str, Any]) -> str:
        """Get schema information for selected tables"""
        try:
            return get_schema(vars.get("selected_tables", []))
        except Exception as e:
            logger.error(f"Error getting schema: {str(e)}")
            raise
    
    @staticmethod
    def _run_query(vars: Dict[str, Any]) -> Any:
        """Execute SQL query"""
        try:
            query = vars.get("query")
            if not query:
                raise ValueError("No query provided")
            return run_query(query)
        except Exception as e:
            logger.error(f"Error running query: {str(e)}")
            raise
    
    @staticmethod
    def _process_response(vars: Dict[str, Any]) -> Dict[str, Any]:
        """Process response before final prompt"""
        try:
            from .insights import InsightGenerator
            
            schema_data = InsightGenerator.get_default_insights(vars.get("selected_tables", []))
            schema_suggestions = InsightGenerator.generate_schema_suggestions(schema_data)
            
            vars["insights"] = schema_data
            vars["suggestions"] = schema_suggestions
            
            if isinstance(vars["response"], str):
                try:
                    vars["response"] = eval(vars["response"])
                except:
                    pass
            return vars
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            raise