# src/components/visualization.py
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import logging

def create_visualization(df: pd.DataFrame):
    """
    Creates a visualization using matplotlib and seaborn
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the data to visualize with 'Categoría' and 'Cantidad' columns
    """
    try:
        sns.set_style("whitegrid")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.barplot(data=df, x='Categoría', y='Cantidad', ax=ax)
        
        ax.set_title('Distribución de Datos', pad=20)
        ax.set_xlabel('Categoría')
        ax.set_ylabel('Cantidad')
        
        if len(df) > 4:
            plt.xticks(rotation=45, ha='right')
        
        for i in ax.containers:
            ax.bar_label(i, fmt='%.0f')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    except Exception as e:
        logging.error(f"Error creating visualization: {str(e)}")
        st.error("Error creating visualization")

def create_dynamic_visualization(df: pd.DataFrame, chart_type: str = 'bar'):
    """
    Creates a dynamic visualization based on the data type and chart_type
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the data to visualize
    chart_type : str
        Type of chart to create ('bar', 'line', 'pie', 'scatter')
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == 'bar':
            sns.barplot(data=df, x='Categoría', y='Cantidad', ax=ax)
        elif chart_type == 'line':
            sns.lineplot(data=df, x='Categoría', y='Cantidad', ax=ax, marker='o')
        elif chart_type == 'pie':
            ax.pie(df['Cantidad'], labels=df['Categoría'], autopct='%1.1f%%')
        elif chart_type == 'scatter':
            sns.scatterplot(data=df, x='Categoría', y='Cantidad', ax=ax)
        
        plt.title('Análisis de Datos')
        if chart_type != 'pie' and len(df) > 4:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    except Exception as e:
        logging.error(f"Error creating dynamic visualization: {str(e)}")
        st.error("Error creating visualization")