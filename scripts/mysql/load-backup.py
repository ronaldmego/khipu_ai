# Load files ReportePCBienesYYYYMM
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import pandas as pd
import logging
from typing import List, Dict, Optional
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('csv_loader.log')
    ]
)
logger = logging.getLogger(__name__)

class CSVLoader:
    def __init__(self):
        # Cargar variables de entorno
        load_dotenv()
        
        self.config = {
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'host': os.getenv('MYSQL_HOST'),
            'database': os.getenv('MYSQL_DATABASE'),
            'raise_on_warnings': True,
            'auth_plugin': 'mysql_native_password'
        }
        
        self.conn = None
        self.cursor = None

    def connect(self) -> bool:
        """Establece conexión con la base de datos"""
        try:
            logger.info("Intentando conectar a MySQL...")
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(buffered=True)
            logger.info("Conexión exitosa!")
            return True
        except Error as e:
            logger.error(f"Error de conexión: {str(e)}")
            return False

    def verify_table_exists(self, table_name: str) -> bool:
        """Verifica si una tabla existe"""
        try:
            self.cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            return self.cursor.fetchone() is not None
        except Error as e:
            logger.error(f"Error verificando tabla {table_name}: {str(e)}")
            return False

    def create_table_from_df(self, table_name: str, df: pd.DataFrame) -> bool:
        """Crea una tabla basada en la estructura del DataFrame"""
        try:
            # Mapeo específico para las columnas de Perú Compras
            column_mapping = {
                'FECHA_PROCESO': 'DATETIME',
                'RUC_PROVEEDOR': 'VARCHAR(11)',
                'PROVEEDOR': 'VARCHAR(255)',
                'RUC_ENTIDAD': 'VARCHAR(11)',
                'ENTIDAD': 'VARCHAR(255)',
                'TIPO_PROCEDIMIENTO': 'VARCHAR(50)',
                'ORDEN_ELECTRÓNICA': 'VARCHAR(100)',
                'ORDEN_ELECTRÓNICA_GENERADA': 'VARCHAR(500)',
                'ESTADO_ORDEN_ELECTRÓNICA': 'VARCHAR(50)',
                'DOCUMENTO_ESTADO_OCAM': 'VARCHAR(500)',
                'FECHA_FORMALIZACIÓN': 'DATETIME',
                'FECHA_ÚLTIMO_ESTADO': 'DATETIME',
                'SUB_TOTAL': 'DECIMAL(15,2)',
                'IGV': 'DECIMAL(15,2)',
                'TOTAL': 'DECIMAL(15,2)',
                'ORDEN_DIGITALIZADA': 'VARCHAR(500)',
                'DESCRIPCIÓN_ESTADO': 'VARCHAR(255)',
                'DESCRIPCIÓN_CESIÓN_DERECHOS': 'VARCHAR(255)',
                'ACUERDO_MARCO': 'VARCHAR(255)'
            }
            
            # Mapeo por defecto para columnas no especificadas
            default_type_mapping = {
                'int64': 'BIGINT',
                'float64': 'DECIMAL(15,2)',
                'object': 'VARCHAR(255)',
                'datetime64[ns]': 'DATETIME',
                'bool': 'BOOLEAN'
            }
            
            # Crear la definición de columnas
            columns = []
            for col in df.columns:
                # Limpiar nombre de columna
                clean_col = col.replace(" ", "_").replace("-", "_").lower()
                # Obtener tipo de dato (usar mapeo específico si existe)
                sql_type = column_mapping.get(col, None)
                if sql_type is None:
                    col_type = str(df[col].dtype)
                    sql_type = default_type_mapping.get(col_type, 'TEXT')
                
                columns.append(f"`{clean_col}` {sql_type}")

            # Crear la tabla si no existe
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                {', '.join(columns)}
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            self.cursor.execute(create_table_sql)
            self.conn.commit()
            logger.info(f"Tabla {table_name} creada o verificada exitosamente")
            return True
            
        except Error as e:
            logger.error(f"Error creando tabla {table_name}: {str(e)}")
            return False

    def load_csv_to_table(self, csv_path: str) -> bool:
        """Carga un archivo CSV a una tabla en MySQL"""
        try:
            # Obtener nombre de tabla del nombre del archivo
            table_name = Path(csv_path).stem.lower()
            
            # Configuración específica para los CSVs de Perú Compras
            df = None
            try:
                # Primero leer el CSV
                df = pd.read_csv(
                    csv_path,
                    encoding='latin1',
                    sep=';',
                    decimal=',',
                    thousands='.'
                )
                
                # Luego convertir las columnas de fecha usando to_datetime
                date_columns = ['FECHA_PROCESO', 'FECHA_FORMALIZACIÓN', 'FECHA_ÚLTIMO_ESTADO']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                
                # Reemplazar valores NaN/None por NULL para MySQL
                df = df.replace({pd.NA: None, pd.NaT: None})
                df = df.where(pd.notnull(df), None)
                
                # Logging de estadísticas
                logger.info(f"""
                CSV leído exitosamente:
                - Número total de registros: {len(df)}
                - Columnas encontradas: {len(df.columns)}
                - Memoria utilizada: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB
                """)
                
            except Exception as e:
                logger.error(f"Error en la lectura inicial: {str(e)}")
                # Intento de recuperación con configuración más flexible
                try:
                    df = pd.read_csv(
                        csv_path,
                        encoding='latin1',
                        sep=';',
                        on_bad_lines='skip'
                    )
                    # Reemplazar valores NaN/None por NULL para MySQL
                    df = df.replace({pd.NA: None, pd.NaT: None})
                    df = df.where(pd.notnull(df), None)
                    logger.info("CSV leído en modo de recuperación")
                except Exception as e:
                    logger.error(f"Error en la lectura de recuperación: {str(e)}")
            
            if df is None:
                raise Exception("No se pudo leer el archivo CSV con ninguna codificación")

            # Crear tabla si no existe
            if not self.create_table_from_df(table_name, df):
                return False

            # Preparar datos para inserción
            columns = [col.replace(" ", "_").replace("-", "_").lower() for col in df.columns]
            placeholders = ", ".join(["%s"] * len(columns))
            
            # Insertar datos en lotes
            batch_size = 1000
            for i in range(0, len(df), batch_size):
                try:
                    batch = df.iloc[i:i + batch_size]
                    # Convertir el batch a una lista de tuplas, reemplazando NaN por None
                    values = [tuple(None if pd.isna(x) else x for x in row) for row in batch.values]
                    
                    insert_sql = f"""
                    INSERT INTO `{table_name}` 
                    (`{'`, `'.join(columns)}`) 
                    VALUES ({placeholders})
                    """
                    
                    self.cursor.executemany(insert_sql, values)
                    self.conn.commit()
                    logger.info(f"Insertado lote {i//batch_size + 1} de {len(df)//batch_size + 1}")
                except Exception as e:
                    logger.error(f"Error insertando lote {i//batch_size + 1}: {str(e)}")
                    continue

            logger.info(f"Archivo {csv_path} cargado exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error cargando archivo {csv_path}: {str(e)}")
            return False

    def process_directory(self, directory: str = 'data'):
        """Procesa todos los archivos CSV en un directorio"""
        try:
            # Verificar que el directorio existe
            if not os.path.exists(directory):
                raise Exception(f"El directorio {directory} no existe")

            # Obtener lista de archivos CSV
            csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
            if not csv_files:
                logger.warning(f"No se encontraron archivos CSV en {directory}")
                return

            # Conectar a la base de datos
            if not self.connect():
                return

            # Procesar cada archivo
            successful = 0
            failed = 0
            
            for csv_file in csv_files:
                csv_path = os.path.join(directory, csv_file)
                if self.load_csv_to_table(csv_path):
                    successful += 1
                else:
                    failed += 1

            logger.info(f"""
            Resumen del proceso:
            - Archivos procesados exitosamente: {successful}
            - Archivos con errores: {failed}
            - Total de archivos: {len(csv_files)}
            """)

        except Exception as e:
            logger.error(f"Error en el proceso: {str(e)}")
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn and self.conn.is_connected():
                self.conn.close()
                logger.info("Conexión cerrada")

def main():
    loader = CSVLoader()
    loader.process_directory()

if __name__ == "__main__":
    main()