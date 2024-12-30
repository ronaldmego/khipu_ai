# src/components/history_view.py
import streamlit as st
import pandas as pd
from .visualization import create_visualization
import logging

def display_history():
    """Display query history"""
    try:
        st.header("Conversation History")
        
        for idx, item in enumerate(reversed(st.session_state['history']), 1):
            with st.container():
                st.markdown(f"**Q{idx}:** {item['question']}")
                st.markdown(f"**A:** {item['response']}")
                
                if item.get('query'):
                    st.markdown("**SQL Query:**")
                    st.code(item['query'], language='sql')
                
                if item.get('visualization_data'):
                    if st.button(f"📊 Ver Gráfico {idx}"):
                        df = pd.DataFrame(item['visualization_data'])
                        create_visualization(df)
                
                st.divider()
    except Exception as e:
        logging.error(f"Error displaying history: {str(e)}")
        st.error("Error loading conversation history")