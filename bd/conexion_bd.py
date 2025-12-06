import pymysql
from pymysql import Error
import os
import urllib.parse

def get_db_connection():
    try:
        print(f"\n🔍 [get_db_connection] Iniciando conexión...")
        
        # OPCIÓN A: Usar MYSQL_PUBLIC_URL (URL completa)
        DATABASE_URL = os.environ.get('MYSQL_PUBLIC_URL')
        
        if DATABASE_URL and DATABASE_URL.startswith('mysql://'):
            print(f"✅ Usando MYSQL_PUBLIC_URL de Railway")
            parsed = urllib.parse.urlparse(DATABASE_URL)
            
            DB_HOST = parsed.hostname
            DB_PORT = parsed.port or 3306
            DB_NAME = parsed.path[1:] if parsed.path else 'railway'
            DB_USER = parsed.username
            DB_PASSWORD = parsed.password
            
            print(f"   URL: mysql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        # OPCIÓN B: Usar variables individuales MYSQL_
        else:
            DB_HOST = os.environ.get('MYSQLHOST') or os.environ.get('DB_HOST')
            DB_PORT = os.environ.get('MYSQLPORT') or os.environ.get('DB_PORT')
            DB_NAME = os.environ.get('MYSQLDATABASE') or os.environ.get('DB_NAME')
            DB_USER = os.environ.get('MYSQLUSER') or os.environ.get('DB_USER')
            DB_PASSWORD = os.environ.get('MYSQLPASSWORD') or os.environ.get('DB_PASSWORD')
            
            print(f"✅ Usando variables individuales")
            print(f"   Host: {DB_HOST}")
            print(f"   Port: {DB_PORT}")
            print(f"   Database: {DB_NAME}")
            print(f"   User: {DB_USER}")
        
        # Validar que tenemos todos los datos
        if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER]):
            print("❌ Faltan variables de conexión")
            return None
        
        connection = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD or '',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=15
        )
        
        print(f"✅ Conexión exitosa a {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return connection
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print(f"   Tipo: {type(e).__name__}")
        return None
    
    
def close_db_connection(connection):
    if connection:
        try:
            connection.close()
            print("✅ CONEXIÓN BD - Conexión cerrada")
        except Error as e:
            print(f"⚠️ CONEXIÓN BD - Error cerrando: {e}")