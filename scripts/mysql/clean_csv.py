# clean_csv.py
import os
import logging
from pathlib import Path
from typing import Optional, List
import csv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_headers_from_file(reference_file: str) -> Optional[List[str]]:
    """
    Extrae los encabezados de un archivo CSV de referencia
    
    Args:
        reference_file (str): Ruta al archivo CSV de referencia
        
    Returns:
        Optional[List[str]]: Lista de encabezados o None si hay error
    """
    try:
        with open(reference_file, 'r', encoding='latin1') as file:
            # Leer primera línea y dividir por punto y coma
            headers = next(csv.reader(file, delimiter=';'))
            return [h.strip() for h in headers]  # Limpiar espacios en blanco
    except Exception as e:
        logger.error(f"Error leyendo encabezados del archivo de referencia: {str(e)}")
        return None

def clean_csv(input_file: str, reference_file: str) -> None:
    """
    Limpia un archivo CSV y reemplaza sus encabezados con los de un archivo de referencia
    
    Args:
        input_file (str): Ruta al archivo CSV a limpiar
        reference_file (str): Ruta al archivo CSV de referencia para los encabezados
    """
    try:
        # Verificar que los archivos existen
        for file in [input_file, reference_file]:
            if not os.path.exists(file):
                raise FileNotFoundError(f"No se encontró el archivo: {file}")
        
        logger.info(f"Iniciando limpieza de {input_file} usando encabezados de {reference_file}")
        
        # Obtener encabezados del archivo de referencia
        headers = get_headers_from_file(reference_file)
        if not headers:
            raise ValueError("No se pudieron obtener los encabezados del archivo de referencia")
        
        # Leer el contenido del archivo a limpiar
        with open(input_file, 'r', encoding='latin1') as file:
            content = file.readlines()
        
        # Limpiar el contenido (ignorar la primera línea que contiene los encabezados)
        cleaned_content = []
        for i, line in enumerate(content):
            if i > 0:  # Ignorar la primera línea (encabezados originales)
                cleaned_line = (line
                    .replace(';\t', ';')
                    .replace(';  ', ';')
                    .replace('; ', ';')
                    .strip())
                cleaned_content.append(cleaned_line)
        
        # Generar nombre del archivo de salida
        input_path = Path(input_file)
        output_file = input_path.with_stem(f"{input_path.stem}_cleaned")
        
        # Guardar el archivo limpio con los nuevos encabezados
        with open(output_file, 'w', encoding='latin1', newline='') as file:
            # Escribir encabezados
            file.write(';'.join(headers) + '\n')
            # Escribir contenido limpio
            file.write('\n'.join(cleaned_content))
        
        logger.info(f"""
        Archivo procesado exitosamente:
        - Archivo original: {input_file}
        - Archivo de referencia: {reference_file}
        - Archivo limpio: {output_file}
        - Encabezados utilizados: {headers}
        """)
        
    except Exception as e:
        logger.error(f"Error procesando archivo: {str(e)}")
        raise

if __name__ == "__main__":
    # Especificar archivos
    input_csv = "data/ReportePCBienes202403.csv"
    reference_csv = "data/ReportePCBienes202404.csv"
    clean_csv(input_csv, reference_csv)