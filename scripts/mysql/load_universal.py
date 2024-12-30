# enhanced_loader.py
import os
import sys
import pandas as pd
import numpy as np
import mysql.connector
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging
from dotenv import load_dotenv

class DataValidator:
    """Clase para validación y limpieza de datos"""
    
    @staticmethod
    def detect_date_format(series: pd.Series) -> str:
        """Detecta el formato de fecha más común en una serie"""
        common_formats = [
            '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y',
            '%Y%m%d'
        ]
        
        for date_format in common_formats:
            try:
                pd.to_datetime(series.dropna().iloc[0], format=date_format)
                return date_format
            except (ValueError, IndexError):
                continue
        return None

    @staticmethod
    def infer_column_type(series: pd.Series) -> Tuple[str, float]:
        """
        Infiere el tipo de datos de una columna y retorna el tipo SQL correspondiente
        junto con el porcentaje de valores válidos
        """
        # Eliminar valores nulos para el análisis
        non_null = series.dropna()
        if len(non_null) == 0:
            return 'TEXT', 100.0

        # Intentar convertir a numérico
        numeric_conversion = pd.to_numeric(non_null, errors='coerce')
        if numeric_conversion.notna().all():
            # Verificar si son enteros
            if (numeric_conversion % 1 == 0).all():
                if numeric_conversion.max() > 2147483647 or numeric_conversion.min() < -2147483648:
                    return 'BIGINT', 100.0
                return 'INT', 100.0
            return 'DOUBLE', 100.0

        # Intentar convertir a fecha
        date_format = DataValidator.detect_date_format(non_null)
        if date_format:
            try:
                pd.to_datetime(non_null, format=date_format)
                return 'DATETIME', 100.0
            except ValueError:
                pass

        # Si no es número ni fecha, usar TEXT
        # Calcular el porcentaje de valores que son strings válidos
        valid_strings = non_null.astype(str).str.len() <= 255
        valid_percentage = (valid_strings.sum() / len(non_null)) * 100
        
        if valid_percentage < 100:
            return 'TEXT', valid_percentage
        return 'TEXT', 100.0

class CSVLoader:
    """Clase principal para cargar CSVs a MySQL"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.setup_logging()
        self.validator = DataValidator()
        self.connection = None
        self.cursor = None

    def setup_logging(self):
        """Configura el sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('csv_loader.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def connect_to_database(self):
        """Establece conexión con la base de datos"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            self.logger.info("Conexión a MySQL establecida exitosamente")
        except mysql.connector.Error as err:
            self.logger.error(f"Error al conectar a MySQL: {err}")
            raise

    def clean_column_name(self, column: str) -> str:
        """Limpia y valida nombres de columnas"""
        clean_name = ''.join(c if c.isalnum() else '_' for c in str(column))
        if clean_name[0].isdigit():
            clean_name = 'col_' + clean_name
        return clean_name.lower()

    def analyze_csv(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analiza el DataFrame y retorna información sobre los tipos de datos"""
        column_info = {}
        
        for column in df.columns:
            sql_type, valid_percentage = self.validator.infer_column_type(df[column])
            missing_percentage = (df[column].isna().sum() / len(df)) * 100
            
            column_info[column] = {
                'sql_type': sql_type,
                'valid_percentage': valid_percentage,
                'missing_percentage': missing_percentage,
                'clean_name': self.clean_column_name(column)
            }
            
        return column_info

    def create_table(self, table_name: str, column_info: Dict[str, Dict[str, Any]]):
        """Crea la tabla en MySQL con los tipos de datos inferidos"""
        columns = []
        for col, info in column_info.items():
            clean_name = info['clean_name']
            sql_type = info['sql_type']
            columns.append(f"`{clean_name}` {sql_type}")

        # Agregar id como primary key
        columns.insert(0, "id INT AUTO_INCREMENT PRIMARY KEY")
        
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            {', '.join(columns)}
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        self.cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        self.cursor.execute(create_table_query)
        self.logger.info(f"Tabla '{table_name}' creada exitosamente")

    def attempt_csv_read(self, file_path: str) -> Tuple[pd.DataFrame, dict]:
        """
        Intenta leer un CSV usando diferentes estrategias, retorna el DataFrame y la estrategia usada
        """
        strategies = [
            # Estrategia 1: Lectura estándar
            {'encoding': 'utf-8'},
            {'encoding': 'ISO-8859-1'},
            {'encoding': 'cp1252'},
            
            # Estrategia 2: Probar diferentes separadores
            {'encoding': 'utf-8', 'sep': ','},
            {'encoding': 'utf-8', 'sep': ';'},
            {'encoding': 'ISO-8859-1', 'sep': ';'},
            
            # Estrategia 3: Manejo de líneas problemáticas
            {'encoding': 'utf-8', 'on_bad_lines': 'skip'},
            {'encoding': 'ISO-8859-1', 'on_bad_lines': 'skip'},
            {'encoding': 'utf-8', 'sep': ';', 'on_bad_lines': 'skip'},
            {'encoding': 'ISO-8859-1', 'sep': ';', 'on_bad_lines': 'skip'},
            
            # Estrategia 4: Modo de emergencia con más opciones
            {
                'encoding': 'ISO-8859-1',
                'sep': ';',
                'on_bad_lines': 'skip',
                'low_memory': False,
                'quoting': 3  # QUOTE_NONE
            }
        ]

        errors = []
        for i, strategy in enumerate(strategies, 1):
            try:
                self.logger.info(f"Intentando estrategia {i} con parámetros: {strategy}")
                df = pd.read_csv(file_path, **strategy)
                
                # Verificar que el DataFrame no esté vacío y tenga columnas
                if len(df) > 0 and len(df.columns) > 1:
                    self.logger.info(f"Lectura exitosa con estrategia {i}")
                    return df, strategy
                else:
                    errors.append(f"Estrategia {i}: DataFrame vacío o sin columnas suficientes")
            except Exception as e:
                errors.append(f"Estrategia {i}: {str(e)}")
                continue

        # Si llegamos aquí, intentamos una última estrategia más agresiva
        try:
            self.logger.warning("Intentando estrategia de último recurso con engine='python'")
            df = pd.read_csv(
                file_path,
                encoding='ISO-8859-1',
                sep=None,  # intentar detectar el separador
                engine='python',
                on_bad_lines='skip',
                low_memory=False,
                quoting=3
            )
            if len(df) > 0:
                return df, {"engine": "python", "sep": "auto-detected"}
        except Exception as e:
            errors.append(f"Estrategia final: {str(e)}")

        # Si todas las estrategias fallan, registrar los errores y lanzar excepción
        error_log = "\n".join(errors)
        self.logger.error(f"Todas las estrategias de lectura fallaron:\n{error_log}")
        raise ValueError("No se pudo leer el archivo CSV con ninguna estrategia")

    def load_csv(self, file_path: str) -> bool:
        """Carga un archivo CSV a MySQL"""
        try:
            self.logger.info(f"Iniciando carga de {file_path}")
            
            # Intentar leer el CSV con diferentes estrategias
            df, strategy_used = self.attempt_csv_read(file_path)
            
            # Registrar información sobre la estrategia exitosa
            self.logger.info(f"Archivo leído exitosamente usando: {strategy_used}")
            self.logger.info(f"Dimensiones iniciales: {df.shape}")
            
            # Continuar con el proceso de limpieza y carga...
            initial_rows = len(df)
            
            # Limpiar datos
            df = df.replace({np.nan: None, 'nan': None, 'NULL': None, '': None})
            df = df.dropna(how='all')
            df = df.drop_duplicates()
            
            # Registrar estadísticas de limpieza
            rows_after_cleaning = len(df)
            self.logger.info(f"""
            Estadísticas de limpieza:
            - Filas iniciales: {initial_rows}
            - Filas después de limpieza: {rows_after_cleaning}
            - Filas eliminadas: {initial_rows - rows_after_cleaning}
            """)

            # Obtener nombre de la tabla del nombre del archivo
            table_name = os.path.splitext(os.path.basename(file_path))[0].lower()
            
            # Analizar tipos de columnas y crear tabla
            column_info = self.analyze_csv(df)
            self.create_table(table_name, column_info)
            
            # Preparar los datos para inserción
            clean_columns = [info['clean_name'] for info in column_info.values()]
            df.columns = clean_columns
            
            # Insertar datos por lotes
            batch_size = 1000
            total_inserted = 0
            
            # Preparar la consulta de inserción
            placeholders = ', '.join(['%s'] * len(clean_columns))
            insert_query = f"INSERT INTO `{table_name}` ({', '.join(f'`{col}`' for col in clean_columns)}) VALUES ({placeholders})"
            
            for i in range(0, len(df), batch_size):
                try:
                    batch = df.iloc[i:i + batch_size]
                    values = [tuple(row) for _, row in batch.iterrows()]
                    self.cursor.executemany(insert_query, values)
                    self.connection.commit()
                    total_inserted += len(batch)
                    self.logger.info(f"Insertados {total_inserted} de {len(df)} registros...")
                except Exception as e:
                    self.logger.error(f"Error en el lote {i}-{i+batch_size}: {e}")
                    self.connection.rollback()
                    continue

            self.logger.info(f"Importación completada. Total de registros insertados: {total_inserted}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al cargar {file_path}: {str(e)}")
            return False

    def process_directory(self, directory: str):
        """Procesa todos los CSVs en un directorio"""
        if not os.path.isdir(directory):
            self.logger.error(f"El directorio {directory} no existe")
            return
        
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        if not csv_files:
            self.logger.warning("No se encontraron archivos CSV")
            return
        
        successful_loads = 0
        failed_loads = 0
        
        for csv_file in csv_files:
            full_path = os.path.join(directory, csv_file)
            if self.load_csv(full_path):
                successful_loads += 1
            else:
                failed_loads += 1
        
        self.logger.info(f"""
        Resumen de procesamiento:
        - CSVs procesados exitosamente: {successful_loads}
        - CSVs con errores: {failed_loads}
        - Total de archivos: {len(csv_files)}
        """)

def main():
    # Cargar variables de entorno
    load_dotenv()
    
    config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST'),
        'database': os.getenv('MYSQL_DATABASE')
    }
    
    loader = CSVLoader(config)
    try:
        loader.connect_to_database()
        loader.process_directory('data')
    finally:
        if loader.cursor:
            loader.cursor.close()
        if loader.connection:
            loader.connection.close()

if __name__ == "__main__":
    main()