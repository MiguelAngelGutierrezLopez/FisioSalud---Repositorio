# conexion_bd.py - VERSIÓN CORREGIDA
import pymysql
from pymysql import Error  # Importar Error correctamente
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Usar variables de entorno o valores por defecto
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_NAME = os.getenv('DB_NAME', 'fisiosalud')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

def get_db_connection():
    try:
        # CONEXIÓN CORRECTA - usa pymysql.connect directamente
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"✅ Conectado a BD: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return connection
    except Error as e:
        print(f"❌ Error conectando a MariaDB: {e}")
        return None

def close_db_connection(connection):
    if connection:
        try:
            connection.close()
            print("✅ Conexión a la base de datos cerrada.")
        except Error as e:
            print(f"⚠️ Error cerrando conexión: {e}")