# init_db.py
import os
import sys
import mysql.connector
from dotenv import load_dotenv

def load_environment():
    """Cargar variables de entorno y validar que existan las necesarias"""
    load_dotenv()
    required_vars = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_HOST', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")
        sys.exit(1)
    
    return {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST')
    }

def create_database():
    """Crear la base de datos si no existe"""
    config = load_environment()
    database_name = os.getenv('MYSQL_DATABASE')
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Crear base de datos si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Base de datos '{database_name}' creada o verificada exitosamente")
        
    except mysql.connector.Error as err:
        print(f"Error al crear la base de datos: {err}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()
        print("Conexión cerrada")

if __name__ == "__main__":
    print("Iniciando creación de la base de datos...")
    create_database()
    print("Proceso finalizado")