# src/components/debug_panel.py
import streamlit as st
import logging

def display_debug_section():
    """Display debug information in a separate section"""
    try:
        st.header("Debug Information")
        
        # Asegurar que debug_logs existe
        if 'debug_logs' not in st.session_state:
            st.session_state['debug_logs'] = []
            
        if st.session_state['debug_logs']:
            for idx, log in enumerate(st.session_state['debug_logs'], 1):
                with st.expander(f"Debug Log {idx}", expanded=False):
                    st.json(log)
        else:
            st.info("No debug logs available yet. Make some queries to see the debug information.")
    except Exception as e:
        logging.error(f"Error displaying debug section: {str(e)}")
        st.error("Error loading debug information")