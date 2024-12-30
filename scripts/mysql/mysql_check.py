# mysql_check.py
import mysql.connector
from dotenv import load_dotenv
import os

def check_mysql_connection():
    """
    Verifica la conexión a MySQL y muestra información detallada
    """
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener credenciales
    config = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST'),
        'database': os.getenv('MYSQL_DATABASE')
    }
    
    print("\nVerificando conexión a MySQL...")
    print(f"Host: {config['host']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    
    try:
        # Intentar conexión con parámetros adicionales
        config.update({
            'raise_on_warnings': True,
            'connection_timeout': 10,
            'auth_plugin': 'mysql_native_password',
            'charset': 'utf8mb4',
            'use_unicode': True
        })
        
        # Intentar conexión
        conn = mysql.connector.connect(**config)
        
        if conn.is_connected():
            db_info = conn.get_server_info()
            cursor = conn.cursor()
            
            # Obtener versión de MySQL
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            # Obtener tablas existentes
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\n✅ Conexión exitosa!")
            print(f"MySQL versión: {version}")
            print(f"Servidor: {db_info}")
            
            if tables:
                print("\nTablas encontradas:")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"- {table[0]}: {count} registros")
            else:
                print("\nNo se encontraron tablas en la base de datos.")
                
            cursor.close()
            conn.close()
            
        else:
            print("❌ No se pudo establecer conexión.")
            
    except mysql.connector.Error as e:
        print("\n❌ Error de conexión:")
        print(f"Error: {e}")
        print("\nVerifica que:")
        print("1. El servidor MySQL esté corriendo")
        print("2. Las credenciales en .env sean correctas")
        print("3. La base de datos exista")
        print("4. El usuario tenga los permisos necesarios")

if __name__ == "__main__":
    check_mysql_connection()