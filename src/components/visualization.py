import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import logging
from decimal import Decimal
import numpy as np

def format_large_number(num):
    """Format large numbers for display"""
    if isinstance(num, (int, float, Decimal)):
        if abs(num) >= 1_000_000:
            return f'{num/1_000_000:.1f}M'
        elif abs(num) >= 1_000:
            return f'{num/1_000:.1f}K'
    return str(num)

def create_visualization(df: pd.DataFrame):
    """
    Creates a visualization using matplotlib and seaborn
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the data to visualize
    """
    try:
        # Configurar el estilo
        plt.style.use('seaborn')
        sns.set_palette("husl")
        
        # Crear la figura
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convertir valores a numérico si es necesario
        if 'Cantidad' in df.columns:
            df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
        
        # Crear el gráfico de barras
        bars = sns.barplot(data=df, x='Categoría', y='Cantidad', ax=ax)
        
        # Rotar etiquetas si son muchas categorías
        if len(df) > 4:
            plt.xticks(rotation=45, ha='right')
        
        # Ajustar etiquetas de valores
        for i, bar in enumerate(bars.patches):
            value = df['Cantidad'].iloc[i]
            formatted_value = format_large_number(value)
            ax.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height(),
                formatted_value,
                ha='center',
                va='bottom'
            )
        
        # Ajustar título y etiquetas
        ax.set_title('Análisis de Datos', pad=20, fontsize=14)
        ax.set_xlabel('Categoría', fontsize=12)
        ax.set_ylabel('Cantidad', fontsize=12)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Mostrar en Streamlit
        st.pyplot(fig)
        plt.close(fig)
        
    except Exception as e:
        logging.error(f"Error creating visualization: {str(e)}")
        st.error("Error al crear la visualización. Verifica el formato de los datos.")

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
        plt.style.use('seaborn')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convertir valores a numérico
        if 'Cantidad' in df.columns:
            df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
        
        if chart_type == 'bar':
            bars = sns.barplot(data=df, x='Categoría', y='Cantidad', ax=ax)
            for i, bar in enumerate(bars.patches):
                value = df['Cantidad'].iloc[i]
                formatted_value = format_large_number(value)
                ax.text(
                    bar.get_x() + bar.get_width()/2,
                    bar.get_height(),
                    formatted_value,
                    ha='center',
                    va='bottom'
                )
        elif chart_type == 'line':
            sns.lineplot(data=df, x='Categoría', y='Cantidad', ax=ax, marker='o')
        elif chart_type == 'pie':
            plt.pie(df['Cantidad'], labels=df['Categoría'],
                   autopct=lambda pct: format_large_number(pct * sum(df['Cantidad']) / 100))
        elif chart_type == 'scatter':
            sns.scatterplot(data=df, x='Categoría', y='Cantidad', ax=ax)
        
        plt.title('Análisis de Datos', pad=20, fontsize=14)
        if chart_type != 'pie' and len(df) > 4:
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        
    except Exception as e:
        logging.error(f"Error creating dynamic visualization: {str(e)}")
        st.error("Error al crear la visualización. Verifica el formato de los datos.")