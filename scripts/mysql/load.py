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

    def standardize_column_name(self, column_name: str) -> str:
        """
        Estandariza el nombre de una columna:
        - Remueve tildes y caracteres especiales
        - Convierte a minúsculas
        - Reemplaza espacios y guiones con underscore
        
        Args:
            column_name (str): Nombre original de la columna
            
        Returns:
            str: Nombre estandarizado de la columna
        """
        # Mapeo de caracteres especiales y tildes
        special_chars = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
            'ñ': 'n', 'Ñ': 'n', 'ü': 'u', 'Ü': 'u',
            ' ': '_', '-': '_', '.': '_'
        }
        
        # Convertir a minúsculas
        clean_name = column_name.lower()
        
        # Reemplazar caracteres especiales
        for char, replacement in special_chars.items():
            clean_name = clean_name.replace(char, replacement)
        
        # Remover cualquier carácter que no sea alfanumérico o underscore
        clean_name = ''.join(c if c.isalnum() or c == '_' else '' for c in clean_name)
        
        # Remover underscores múltiples
        while '__' in clean_name:
            clean_name = clean_name.replace('__', '_')
        
        # Remover underscore al inicio o final
        clean_name = clean_name.strip('_')
        
        # Si el nombre empieza con un número, añadir 'col_' al inicio
        if clean_name[0].isdigit():
            clean_name = f'col_{clean_name}'
        
        return clean_name

    def create_table_from_df(self, table_name: str, df: pd.DataFrame) -> bool:
        """Crea una tabla basada en la estructura del DataFrame"""
        try:
            # Mapeo por defecto para tipos de datos
            default_type_mapping = {
                'int64': 'BIGINT',
                'float64': 'DECIMAL(15,2)',
                'object': 'VARCHAR(255)',
                'datetime64[ns]': 'DATETIME',
                'bool': 'BOOLEAN'
            }
            
            # Crear la definición de columnas
            columns = []
            clean_column_names = {}  # Diccionario para mapear nombres originales a limpios
            
            for col in df.columns:
                # Estandarizar nombre de columna
                clean_col = self.standardize_column_name(col)
                clean_column_names[col] = clean_col
                
                # Obtener tipo de dato
                col_type = str(df[col].dtype)
                sql_type = default_type_mapping.get(col_type, 'TEXT')
                
                # Ajustar longitud de VARCHAR basado en los datos
                if sql_type == 'VARCHAR(255)':
                    max_length = df[col].astype(str).str.len().max()
                    sql_type = f'VARCHAR({min(max(max_length * 2, 50), 500)})'
                
                columns.append(f"`{clean_col}` {sql_type}")
            
            # Renombrar columnas en el DataFrame
            df.rename(columns=clean_column_names, inplace=True)

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
            logger.info("Mapeo de columnas realizado:")
            for original, clean in clean_column_names.items():
                logger.info(f"  {original} -> {clean}")
            
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
                
                total_registros = len(df)
                logger.info(f"""
                CSV leído exitosamente:
                - Número total de registros: {total_registros}
                - Columnas encontradas: {len(df.columns)}
                - Memoria utilizada: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB
                """)
                
            except Exception as e:
                logger.error(f"Error en la lectura inicial: {str(e)}")
                return False

            # Crear tabla si no existe
            if not self.create_table_from_df(table_name, df):
                return False

            # Preparar datos para inserción
            columns = [col.replace(" ", "_").replace("-", "_").lower() for col in df.columns]
            placeholders = ", ".join(["%s"] * len(columns))
            
            # Insertar datos en lotes usando INSERT IGNORE
            batch_size = 1000
            registros_insertados = 0
            registros_duplicados = 0
            
            for i in range(0, len(df), batch_size):
                try:
                    batch = df.iloc[i:i + batch_size]
                    # Convertir el batch a una lista de tuplas, reemplazando NaN por None
                    values = [tuple(None if pd.isna(x) else x for x in row) for row in batch.values]
                    
                    # Usar INSERT IGNORE para saltar duplicados
                    insert_sql = f"""
                    INSERT IGNORE INTO `{table_name}` 
                    (`{'`, `'.join(columns)}`) 
                    VALUES ({placeholders})
                    """
                    
                    self.cursor.executemany(insert_sql, values)
                    self.conn.commit()
                    
                    # Contar registros insertados vs duplicados
                    registros_insertados += self.cursor.rowcount
                    registros_duplicados = len(batch) - self.cursor.rowcount
                    
                    logger.info(f"Procesado lote {i//batch_size + 1} de {len(df)//batch_size + 1}")
                except Exception as e:
                    logger.error(f"Error insertando lote {i//batch_size + 1}: {str(e)}")
                    continue

            logger.info(f"""
            Archivo {csv_path} procesado:
            - Total registros en archivo: {total_registros}
            - Registros nuevos insertados: {registros_insertados}
            - Registros duplicados omitidos: {total_registros - registros_insertados}
            """)
            return True

        except Exception as e:
            logger.error(f"Error cargando archivo {csv_path}: {str(e)}")
            return False

    def process_directory(self, directory: str = 'data'):
        """Procesa todos los archivos CSV en un directorio"""
        try:
            # Obtener ruta raíz del proyecto (2 niveles arriba de scripts/mysql)
            root_path = Path(__file__).parent.parent.parent
            data_dir = root_path / directory
            
            # Verificar que el directorio existe
            if not data_dir.exists():
                raise Exception(f"El directorio {data_dir} no existe")

            # Obtener lista de archivos CSV
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            if not csv_files:
                logger.warning(f"No se encontraron archivos CSV en {data_dir}")
                return

            # Conectar a la base de datos
            if not self.connect():
                return

            # Procesar cada archivo
            successful = 0
            failed = 0
            
            for csv_file in csv_files:
                csv_path = os.path.join(data_dir, csv_file)
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