# conexion_bd.py - VERSIÓN DEFINITIVA PARA RAILWAY
import pymysql
from pymysql import Error
import os


DB_HOST = os.environ.get('MYSQLHOST') or os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('MYSQLPORT') or os.environ.get('DB_PORT', 3306))
DB_NAME = os.environ.get('MYSQLDATABASE') or os.environ.get('DB_NAME', 'railway')
DB_USER = os.environ.get('MYSQLUSER') or os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('MYSQLPASSWORD') or os.environ.get('DB_PASSWORD', '')

def get_db_connection():
    try:
        print(f"🔍 CONEXIÓN BD - Intentando conectar...")
        print(f"   Host: {DB_HOST}")
        print(f"   Port: {DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        
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
        print(f"✅ CONEXIÓN BD - Conectado exitosamente a {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return connection
    except Error as e:
        print(f"❌ CONEXIÓN BD - Error: {e}")
        print(f"📝 Variables disponibles:")
        for key in ['MYSQLHOST', 'MYSQLPORT', 'MYSQLDATABASE', 'MYSQLUSER', 'MYSQLPASSWORD',
                    'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']:
            if key in os.environ:
                if 'PASSWORD' in key:
                    print(f"   {key}: {'*' * len(os.environ[key])}")
                else:
                    print(f"   {key}: {os.environ[key]}")
        return None

def close_db_connection(connection):
    if connection:
        try:
            connection.close()
            print("✅ CONEXIÓN BD - Conexión cerrada")
        except Error as e:
            print(f"⚠️ CONEXIÓN BD - Error cerrando: {e}")