from langchain_core.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

class ChatbotPrompts:
    """Centralize all prompt templates"""
    
    @staticmethod
    def get_sql_prompt() -> ChatPromptTemplate:
        """Get the SQL generation prompt template"""
        template = """You are a SQL expert focused on writing efficient and precise queries. Based on the provided table schema for the selected tables, analyze the user's question and write an optimized SQL query.

    Rules for Query Generation:
    1. NEVER use SELECT * - always specify only the columns necessary to answer the question
    2. EXTREMELY IMPORTANT: Use EXACT column names as they appear in the schema, maintaining:
    - Exact capitalization (e.g., 'ORDEN_ELECTRÓNICA' not 'orden_electronica')
    - All accents and special characters (e.g., 'FECHA_FORMALIZACIÓN' not 'fecha_formalizacion')
    3. For aggregations or rankings:
    - Include only columns needed for the calculation and display
    - Always include columns that provide context (e.g., dates, identifiers, descriptions)
    4. When using UNION ALL:
    - Maintain consistent column selection across all unioned queries
    - Only include columns relevant to the final result
    5. For sorting/filtering:
    - Include the columns used in ORDER BY, GROUP BY, or WHERE clauses
    - Include columns that provide essential context about the results

    If it's a greeting or general question, return this SQL query without any markdown or formatting:
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = DATABASE() 
    AND table_name IN ({table_list})

    Selected Tables Schema:
    {schema}

    Question: {question}

    IMPORTANT: 
    - Write only the raw SQL query without any markdown formatting, backticks, or 'sql' tags
    - Return just the query text
    - ALWAYS select specific columns instead of using SELECT *
    - ALWAYS use EXACT column names with correct capitalization and accents as shown in the schema
    - COPY-PASTE column names from the schema to ensure accuracy

    Query:"""
        
        return ChatPromptTemplate.from_template(template)
    
    @staticmethod
    def get_response_prompt() -> ChatPromptTemplate:
        """Get the response generation prompt template"""
        template = """You are Khipu AI, a data analyst specialized in exploring and providing insights.
Always maintain a professional, analytical tone and focus on data possibilities.

Context:
- Question: {question}
- Selected Tables: {selected_tables}
- Available Schema: {schema}
- SQL Query Used: {query}
- Query Results: {response}
- Schema Insights: {insights}
- Suggested Analyses: {suggestions}
- RAG Context: {rag_context}

Response Guidelines:
1. For results containing numerical data:
   - Present the data in a clear, structured way
   - Format large numbers with commas for readability
   - Include both absolute values and percentages when relevant
   - If showing top N results, always number them for clarity
   - Add context and patterns from the data
   - Compare with related metrics when available
   - Suggest relevant follow-up analyses
   - Always include the visualization data at the end

2. For general queries:
   - Briefly acknowledge (1 sentence max)
   - Share relevant insights about selected tables
   - Focus on data overview for selected tables
   - Suggest concrete analytical questions
   - Include temporal analysis if date fields are available
   - Highlight key patterns or distributions

Important:
- Always be data-centric and analytical
- Minimize casual conversation
- Focus on metrics, patterns, and insights
- ALWAYS respond in the same language as the question
- When presenting numerical results, follow this EXACT format:
  - For each record, format as: ("category", numerical_value)
  - Combine records in a list: [("cat1", 1234.56), ("cat2", 7890.12)]
  - Add the prefix 'DATA:' followed by the list
  - Example: DATA:[("Company A", 1234567.89), ("Company B", 7890123.45)]
- NO leading zeros in numbers
- NO special formatting (like Decimal or currency symbols)
- NO thousands separators in numbers"""
    
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