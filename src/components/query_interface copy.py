# src/components/query_interface.py
import streamlit as st
import pandas as pd
from src.services.data_processing import handle_query_and_response
from src.components.visualization import create_visualization
from src.utils.database import get_all_tables
from typing import List
from src.utils.llm_provider import LLMProvider
from config.config import get_default_model

def display_model_settings():
    """Display model settings in sidebar"""
    st.sidebar.markdown("## Model Settings")
    ollama_available = LLMProvider.check_ollama_availability()
    
    if not ollama_available:
        st.sidebar.warning("⚠️ Ollama service not detected")
    
    provider = st.sidebar.selectbox(
        "Select Provider",
        options=['openai', 'ollama'],
        index=0 if st.session_state.get('llm_provider') == 'openai' else 1,
        key='provider_select'
    )
    st.session_state['llm_provider'] = provider
    
    available_models = LLMProvider.list_available_models(provider)
    model_name = st.sidebar.selectbox(
        "Select Model",
        options=available_models,
        index=available_models.index(get_default_model(provider)) if get_default_model(provider) in available_models else 0,
        key='model_select'
    )
    st.session_state['llm_model_name'] = model_name
    
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.get('llm_temperature', 0.7),
        step=0.1,
        key='temperature_slider'
    )
    st.session_state['llm_temperature'] = temperature

def display_table_selection() -> List[str]:
    """Display table selection interface and return selected tables"""
    try:
        tables = get_all_tables()
        if not tables:
            st.sidebar.error("No tables found in database.")
            return []
        
        st.sidebar.markdown("---")
        st.sidebar.write("📊 Select tables to query:")
        
        # Crear dos columnas para los botones de selección
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.sidebar.button("Select All"):  # Cambiar a st.sidebar.button
                st.session_state['selected_tables'] = tables
        with col2:
            if st.sidebar.button("Clear All"):   # Cambiar a st.sidebar.button
                st.session_state['selected_tables'] = []

        # Inicializar selected_tables en session_state si no existe
        if 'selected_tables' not in st.session_state:
            st.session_state['selected_tables'] = []

        # Multiselect con los nombres originales de las tablas
        selected_tables = st.sidebar.multiselect(
            "Available Tables:",
            options=sorted(tables, reverse=True),
            default=st.session_state['selected_tables'],
            key='table_selector'
        )
        
        # Guardar la selección en session_state
        st.session_state['selected_tables'] = selected_tables
        
        # Mostrar las tablas seleccionadas en el sidebar
        if selected_tables:
            with st.sidebar.expander("Selected Tables", expanded=False):
                st.write(", ".join(selected_tables))
            st.sidebar.success(f"✅ Selected {len(selected_tables)} tables")
        else:
            st.sidebar.warning("⚠️ No tables selected")
            
        # Mostrar estado de conexión al final
        st.sidebar.markdown("---")
        st.sidebar.success("✔️ Connected to database")
        if tables:
            st.sidebar.info(f"Available tables: {len(tables)}")
            
        return selected_tables
        
    except Exception as e:
        st.sidebar.error(f"Error in table selection: {str(e)}")
        return []

def process_query(question: str, selected_tables: List[str]):
    """Process a query and display results"""
    with st.spinner('Processing your question...'):
        try:
            response = handle_query_and_response(question, selected_tables)
            
            if response:
                # Main response container
                response_container = st.container()
                with response_container:
                    # Answer section
                    st.markdown("### Answer")
                    st.write(response.get('response', ''))
                    
                    # Results section
                    results_container = st.container()
                    with results_container:
                        # Visualization section
                        if response.get('visualization_data'):
                            viz_expander = st.expander("📊 Data Visualization", expanded=True)
                            with viz_expander:
                                df = pd.DataFrame(response['visualization_data'])
                                create_visualization(df)
                        
                        # SQL Query section
                        if response.get('query'):
                            sql_expander = st.expander("🔍 SQL Query", expanded=False)
                            with sql_expander:
                                st.code(response.get('query', ''), language='sql')

                        # RAG Context section
                        if response.get('rag_context'):
                            rag_expander = st.expander("📚 Documents Used for Analysis", expanded=False)
                            with rag_expander:
                                st.markdown("The following document excerpts were used to enhance the analysis:")
                                for idx, ctx in enumerate(response['rag_context'], 1):
                                    st.markdown(f"**Document {idx}:**")
                                    st.markdown(f"```\n{ctx[:300]}...\n```")
                                    st.markdown("---")
                
                # Add to history
                if 'history' not in st.session_state:
                    st.session_state['history'] = []
                st.session_state['history'].append(response)
                
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
            st.info("Please check your database connection and API keys.")

def display_query_interface():
    """Display the main query interface"""
    # Initialize session states
    if 'current_question' not in st.session_state:
        st.session_state['current_question'] = ""
    
    # Obtener las tablas seleccionadas
    selected_tables = st.session_state.get('selected_tables', [])
    
    if not selected_tables:
        st.warning("Please select at least one table from the sidebar to start querying.")
        return
    
    # Contenedor principal para el input y botón
    col1, col2 = st.columns([6,1])
    
    with col1:
        question = st.text_input(
            "Question",
            value=st.session_state['current_question'],
            placeholder="Ask a question about your data...",
            label_visibility="collapsed"
        )
    
    with col2:
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    
    # Process query if button is clicked or if we have a new quick question
    if ask_button or question != st.session_state['current_question']:
        if question and selected_tables:
            st.session_state['current_question'] = question
            process_query(question, selected_tables)