# conexion_bd.py - VERSIÓN PARA RAILWAY
import pymysql
from pymysql import Error
import os

# Railway NO usa .env en producción, usa variables de entorno directas
# Estas líneas SON CRÍTICAS:
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_NAME = os.environ.get('DB_NAME', 'railway')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')

def get_db_connection():
    try:
        print(f"🔍 Intentando conectar a: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10
        )
        print(f"✅ Conectado a BD: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return connection
    except Error as e:
        print(f"❌ Error conectando a MariaDB: {e}")
        print(f"📝 Configuración usada:")
        print(f"   Host: {DB_HOST}")
        print(f"   Port: {DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        print(f"   Password: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'VACÍA'}")
        return None

def close_db_connection(connection):
    if connection:
        try:
            connection.close()
            print("✅ Conexión a la base de datos cerrada.")
        except Error as e:
            print(f"⚠️ Error cerrando conexión: {e}")