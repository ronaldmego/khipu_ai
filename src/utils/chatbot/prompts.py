from langchain_core.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

class ChatbotPrompts:
    """Centralize all prompt templates"""
    
    @staticmethod
    def get_sql_prompt() -> ChatPromptTemplate:
        """Get the SQL generation prompt template"""
        template = """Based on the provided table schema for the selected tables, analyze if the user's question requires a specific SQL query.
    If it's a greeting or general question, return this SQL query without any markdown or formatting:
    SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name IN ({table_list})

    If it's a specific analytical question, write a SQL query that answers it using only the selected tables.

    Selected Tables Schema:
    {schema}

    Question: {question}

    IMPORTANT: Write only the raw SQL query without any markdown formatting, backticks, or 'sql' tags. Return just the query text.

    Query:"""
        
        return ChatPromptTemplate.from_template(template)
    
    @staticmethod
    def get_response_prompt() -> ChatPromptTemplate:
        """Get the response generation prompt template"""
        template = """You are Quipu AI, a data analyst specialized in exploring and providing insights.
Always maintain a professional, analytical tone and focus on data possibilities.

Context:
- Question: {question}
- Selected Tables: {selected_tables}
- Available Schema: {schema}
- SQL Query Used: {query}
- Query Results: {response}
- Schema Insights: {insights}
- Suggested Analyses: {suggestions}

Response Guidelines:
1. Greetings/General Questions:
   - Briefly acknowledge (1 sentence max)
   - Share insights about selected tables
   - Focus on data overview for selected tables
   - Suggest concrete analytical questions for these tables
   
2. Specific Analysis Questions:
   - Provide direct answer with numerical details
   - Add context and patterns
   - Compare with related metrics when possible
   - Suggest follow-up analyses within selected tables

Important:
- Always be data-centric and analytical
- Minimize casual conversation
- Focus on metrics, patterns, and insights
- ALWAYS respond in the same language as the question
- If sharing numerical results, add them at the end as:
DATA:[("category1",number1),("category2",number2),...]"""
        
        return ChatPromptTemplate.from_template(template)
    
    @staticmethod
    def get_schema_suggestions_prompt() -> ChatPromptTemplate:
        """Get the schema suggestions prompt template"""
        template = """Given this database structure:
{schema_data}

Generate 3 basic analytical questions that could be answered with this data. Focus on:
1. Basic counts and distributions
2. Time-based analysis if date fields are available
3. Category or group comparisons if categorical fields exist

Return just the numbered list in Spanish."""
        
        return ChatPromptTemplate.from_template(template)