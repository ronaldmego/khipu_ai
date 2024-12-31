import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import logging
from decimal import Decimal
import numpy as np

def format_large_number(num):
    """Format large numbers for display"""
    try:
        # Convertir a float si es string
        if isinstance(num, str):
            num = float(num.replace(',', '').replace('_', ''))
        
        # Convertir Decimal a float si es necesario
        if isinstance(num, Decimal):
            num = float(num)
            
        # Formatear el número
        if isinstance(num, (int, float)):
            if abs(num) >= 1_000_000_000:
                return f'{num/1_000_000_000:.1f}B'
            elif abs(num) >= 1_000_000:
                return f'{num/1_000_000:.1f}M'
            elif abs(num) >= 1_000:
                return f'{num/1_000:.1f}K'
        return f'{num:,.0f}' if isinstance(num, (int, float)) else str(num)
    except (ValueError, TypeError):
        return str(num)

def create_visualization(df: pd.DataFrame):
    """
    Creates a visualization using matplotlib
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing the data to visualize
    """
    try:
        # Configurar el estilo básico de matplotlib
        plt.style.use('default')
        
        # Crear la figura
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convertir valores a numérico si es necesario
        if 'Cantidad' in df.columns:
            df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
        
        # Colores personalizados
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f1c40f',
                 '#1abc9c', '#e67e22', '#34495e', '#7f8c8d', '#16a085']
        
        # Crear el gráfico de barras
        bars = ax.bar(range(len(df)), df['Cantidad'], color=colors[:len(df)])
        
        # Configurar las etiquetas del eje X
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df['Categoría'], rotation=45, ha='right')
        
        # Ajustar etiquetas de valores
        for i, bar in enumerate(bars):
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
        # Usar estilo por defecto de matplotlib
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Convertir valores a numérico
        if 'Cantidad' in df.columns:
            df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
        
        # Colores personalizados
        colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f1c40f',
                 '#1abc9c', '#e67e22', '#34495e', '#7f8c8d', '#16a085']
        
        if chart_type == 'bar':
            bars = ax.bar(range(len(df)), df['Cantidad'], color=colors[:len(df)])
            ax.set_xticks(range(len(df)))
            ax.set_xticklabels(df['Categoría'], rotation=45, ha='right')
            
            for i, bar in enumerate(bars):
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
            ax.plot(range(len(df)), df['Cantidad'], marker='o', color=colors[0])
            ax.set_xticks(range(len(df)))
            ax.set_xticklabels(df['Categoría'], rotation=45, ha='right')
            
        elif chart_type == 'pie':
            plt.pie(df['Cantidad'], labels=df['Categoría'],
                   autopct=lambda pct: format_large_number(pct * sum(df['Cantidad']) / 100),
                   colors=colors[:len(df)])
            
        elif chart_type == 'scatter':
            ax.scatter(range(len(df)), df['Cantidad'], color=colors[0])
            ax.set_xticks(range(len(df)))
            ax.set_xticklabels(df['Categoría'], rotation=45, ha='right')
        
        if chart_type != 'pie':
            ax.set_title('Análisis de Datos', pad=20, fontsize=14)
            ax.set_xlabel('Categoría', fontsize=12)
            ax.set_ylabel('Cantidad', fontsize=12)
        else:
            plt.title('Análisis de Datos', pad=20, fontsize=14)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        
    except Exception as e:
        logging.error(f"Error creating dynamic visualization: {str(e)}")
        st.error("Error al crear la visualización. Verifica el formato de los datos.")