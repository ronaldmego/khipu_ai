# src/layouts/header.py
import streamlit as st
from ..utils.database import test_database_connection

def display_header(show_connection_status: bool = True):
    """
    Displays the application header with optional connection status
    
    Parameters:
    -----------
    show_connection_status : bool
        Whether to show the database connection status
    """
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1>Khipu AI 📊</h1>
            <p style='font-size: 1.2em; color: #666;'>"Tu agente en exploracion de datos SQL con RAG"</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if show_connection_status:
        connection_status = test_database_connection()
        if connection_status["success"]:
            st.sidebar.success("✔️ Connected to database")
            if connection_status["tables"]:
                st.sidebar.info(f"Available tables: {len(connection_status['tables'])}")
        else:
            st.sidebar.error(f"❌ Connection error: {connection_status['error']}")

def display_subheader(title: str, description: str = ""):
    """
    Displays a subheader with optional description
    
    Parameters:
    -----------
    title : str
        The title of the section
    description : str
        Optional description text
    """
    st.markdown(f"## {title}")
    if description:
        st.markdown(f"_{description}_")