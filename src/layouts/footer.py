# src/layouts/footer.py
import streamlit as st

def display_footer():
    """Display the application footer"""
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='text-align: center; color: #666666; padding: 10px;'>
                <p>Created by <a href='https://ronaldmego.github.io/' target='_blank' style='text-decoration: none;'>Ronald Mego</a> 🚀</p>
                <p style='font-size: 0.8em;'>Open Source Project | 
                    <a href='https://github.com/ronaldmego/data_assistant_ai' target='_blank' style='text-decoration: none;'>More Info</a>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )