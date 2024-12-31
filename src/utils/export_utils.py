import os
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class ExportManager:
    """Manages the export of analysis results to markdown files"""
    
    @staticmethod
    def ensure_export_directory() -> Path:
        """Ensure the exports directory exists"""
        export_dir = Path("assets/outputs")
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir

    @staticmethod
    def save_visualization(fig: plt.Figure, timestamp: str) -> str:
        """Save the current visualization to a file"""
        try:
            export_dir = ExportManager.ensure_export_directory()
            viz_path = export_dir / f"visualization_{timestamp}.png"
            
            # Save the figure with high DPI for better quality
            fig.savefig(viz_path, bbox_inches='tight', dpi=300)
            return str(viz_path)
        except Exception as e:
            logger.error(f"Error saving visualization: {e}")
            return ""

    @staticmethod
    def create_markdown_content(analysis_data: Dict[str, Any], timestamp: str, viz_filename: Optional[str] = None) -> str:
        """Create markdown content from analysis data"""
        try:
            content = f"""# Análisis de Datos - {timestamp}

## Pregunta Original
{analysis_data.get('question', 'N/A')}

## Respuesta
{analysis_data.get('response', 'N/A')}

## Query SQL Utilizada
```sql
{analysis_data.get('query', 'N/A')}
```"""
            
            # Add RAG context if available
            if rag_context := analysis_data.get('rag_context'):
                content += "\n## Contexto RAG Utilizado\n"
                for i, ctx in enumerate(rag_context, 1):
                    content += f"\n### Documento {i}\n{ctx}\n"

            # Add tables information
            content += "\n## Tablas Analizadas\n"
            content += ", ".join(analysis_data.get('selected_tables', ['N/A']))

            # Add visualization reference if available
            if viz_filename:
                content += f"\n\n## Visualización\n![Análisis](./{viz_filename})\n"

            # Add footer
            content += f"\n---\nGenerado por Khipu AI - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            return content
            
        except Exception as e:
            logger.error(f"Error creating markdown content: {e}")
            return ""

    @staticmethod
    def export_analysis(analysis_data: Dict[str, Any], fig: Optional[plt.Figure] = None) -> Tuple[Optional[str], Optional[str]]:
        """Export analysis to markdown and save visualization"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = ExportManager.ensure_export_directory()
            
            # Save visualization if available
            viz_filename = None
            if fig:
                viz_path = ExportManager.save_visualization(fig, timestamp)
                viz_filename = os.path.basename(viz_path)
            
            # Create and save markdown content
            content = ExportManager.create_markdown_content(analysis_data, timestamp, viz_filename)
            md_path = export_dir / f"analysis_{timestamp}.md"
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return str(md_path), viz_filename and str(export_dir / viz_filename)
            
        except Exception as e:
            logger.error(f"Error exporting analysis: {e}")
            return None, None

    @staticmethod
    def get_file_download_button(file_path: str, button_text: str) -> None:
        """Create a download button for a file using Streamlit"""
        try:
            with open(file_path, 'rb') as f:
                file_contents = f.read()
            file_name = os.path.basename(file_path)
            
            st.download_button(
                label=button_text,
                data=file_contents,
                file_name=file_name,
                mime='text/markdown' if file_path.endswith('.md') else 'image/png'
            )
        except Exception as e:
            logger.error(f"Error creating download button: {e}")
            st.error("Error creating download button")