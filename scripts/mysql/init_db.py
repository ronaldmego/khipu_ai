# init_db.py
import os
import sys
import logging
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_init.log')
    ]
)
logger = logging.getLogger(__name__)

def load_environment():
    """Cargar variables de entorno y validar que existan las necesarias"""
    # Obtener ruta raíz del proyecto
    root_path = Path(__file__).parent.parent.parent
    env_path = root_path / '.env'
    
    # Cargar .env desde la raíz del proyecto
    load_dotenv(env_path)
    
    required_vars = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_HOST', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")
        sys.exit(1)
    
    config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST')
    }
    
    logger.info(f"Variables de entorno cargadas correctamente desde {env_path}")
    return config

def create_database():
    """Crear la base de datos si no existe"""
    config = load_environment()
    database_name = os.getenv('MYSQL_DATABASE')
    
    logger.info(f"Intentando crear/verificar base de datos: {database_name}")
    logger.info(f"Host: {config['host']}")
    logger.info(f"Usuario: {config['user']}")
    
    try:
        conn = mysql.connector.connect(
            **config,
            auth_plugin='mysql_native_password'
        )
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe
        cursor.execute("SHOW DATABASES")
        existing_dbs = [db[0] for db in cursor.fetchall()]
        
        if database_name in existing_dbs:
            logger.info(f"La base de datos '{database_name}' ya existe")
        else:
            # Crear base de datos si no existe
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            logger.info(f"Base de datos '{database_name}' creada exitosamente")
        
        # Verificar caracterset y collation
        cursor.execute(f"ALTER DATABASE {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        logger.info("Charset y collation configurados a utf8mb4")
        
        # Verificar privilegios
        cursor.execute("SHOW GRANTS")
        grants = cursor.fetchall()
        logger.info("Privilegios del usuario:")
        for grant in grants:
            logger.info(f"  {grant[0]}")
        
    except mysql.connector.Error as err:
        logger.error(f"Error al crear/verificar la base de datos: {err}")
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Conexión cerrada")

if __name__ == "__main__":
    try:
        logger.info("=== Iniciando proceso de creación/verificación de base de datos ===")
        create_database()
        logger.info("=== Proceso finalizado exitosamente ===")
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        sys.exit(1)