# test_load.py
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import pandas as pd
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_load.log')
    ]
)
logger = logging.getLogger(__name__)

def verify_database_permissions(cursor):
    """Verificar permisos de base de datos"""
    try:
        logger.info("Verificando permisos...")
        
        # Verificar privilegios del usuario
        cursor.execute("SHOW GRANTS")
        grants = cursor.fetchall()
        for grant in grants:
            logger.info(f"Grant: {grant[0]}")

        # Verificar base de datos actual
        cursor.execute("SELECT DATABASE()")
        db = cursor.fetchone()
        logger.info(f"Base de datos actual: {db[0]}")

        return True
    except Error as e:
        logger.error(f"Error verificando permisos: {str(e)}")
        return False

def test_connection():
    """Prueba básica de conexión y operaciones"""
    conn = None
    cursor = None
    
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        # Configuración de la base de datos
        config = {
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'host': os.getenv('MYSQL_HOST'),
            'database': os.getenv('MYSQL_DATABASE'),
            'raise_on_warnings': True,
            'auth_plugin': 'mysql_native_password'
        }
        
        logger.info("Intentando conectar a MySQL...")
        logger.info(f"Host: {config['host']}")
        logger.info(f"Database: {config['database']}")
        logger.info(f"User: {config['user']}")
        
        # Conectar a MySQL
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(buffered=True)
        
        logger.info("Conexión exitosa!")
        
        # Verificar permisos
        if not verify_database_permissions(cursor):
            raise Exception("Error verificando permisos")
        
        # 1. Crear tabla de prueba
        logger.info("Creando tabla de prueba...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS test_carga (
            id INT AUTO_INCREMENT PRIMARY KEY,
            FECHA_PROCESO DATETIME,
            RUC_PROVEEDOR VARCHAR(11),
            MONTO DECIMAL(15,2),
            DESCRIPCION VARCHAR(500)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Intentar crear la tabla sin DROP primero
        cursor.execute(create_table_sql)
        conn.commit()
        logger.info("Tabla creada exitosamente")
        
        # 2. Insertar datos de prueba
        logger.info("Insertando datos de prueba...")
        insert_sql = """
        INSERT INTO test_carga (FECHA_PROCESO, RUC_PROVEEDOR, MONTO, DESCRIPCION)
        VALUES (NOW(), %s, %s, %s)
        """
        test_data = [
            ('20123456789', 1000.50, 'Prueba 1'),
            ('20987654321', 2500.75, 'Prueba 2')
        ]
        cursor.executemany(insert_sql, test_data)
        conn.commit()
        logger.info("Datos insertados exitosamente")
        
        # 3. Verificar los datos
        logger.info("Verificando datos insertados...")
        cursor.execute("SELECT * FROM test_carga")
        rows = cursor.fetchall()
        for row in rows:
            logger.info(f"Row: {row}")
        
        # 4. Leer un archivo CSV real
        logger.info("Intentando leer el primer archivo CSV...")
        data_dir = os.path.join(os.getcwd(), 'data')
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        if csv_files:
            test_file = os.path.join(data_dir, csv_files[0])
            logger.info(f"Leyendo archivo: {test_file}")
            
            df = pd.read_csv(
                test_file,
                encoding='latin1',
                sep=';',
                nrows=5  # Solo leer 5 filas para prueba
            )
            logger.info(f"CSV leído exitosamente. Columnas encontradas: {list(df.columns)}")
            logger.info(f"Primeras 5 filas:\n{df.head()}")
        
        # 5. Limpiar - ahora con más cuidado
        logger.info("Intentando eliminar tabla de prueba...")
        try:
            cursor.execute("SELECT COUNT(*) FROM test_carga")
            count = cursor.fetchone()[0]
            logger.info(f"Registros en la tabla antes de eliminar: {count}")
            
            cursor.execute("DROP TABLE test_carga")
            conn.commit()
            logger.info("Tabla eliminada exitosamente")
        except Error as e:
            logger.error(f"Error eliminando tabla: {str(e)}")
        
        logger.info("¡Prueba completada exitosamente!")
        
    except Exception as e:
        logger.error(f"Error durante la prueba: {str(e)}", exc_info=True)
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            logger.info("Conexión cerrada")

if __name__ == "__main__":
    test_connection()