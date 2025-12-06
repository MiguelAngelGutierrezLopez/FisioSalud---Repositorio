# conexion_bd.py - VERSIÓN MEJORADA
import pymysql
from pymysql import Error
import os
import urllib.parse

def get_db_connection():
    try:
        print(f"\n🔍 [get_db_connection] Iniciando conexión...")
        
        # 1. Primero intentar con DATABASE_URL (formato Railway)
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL and DATABASE_URL.startswith('mysql://'):
            print("   Usando DATABASE_URL de Railway")
            parsed = urllib.parse.urlparse(DATABASE_URL)
            DB_HOST = parsed.hostname
            DB_PORT = parsed.port or 3306
            DB_NAME = parsed.path[1:] if parsed.path else 'railway'
            DB_USER = parsed.username
            DB_PASSWORD = parsed.password
        else:
            # 2. Usar variables MYSQL_ (Railway MySQL plugin)
            print("   Usando variables MYSQL_")
            DB_HOST = os.environ.get('MYSQLHOST', 'localhost')
            DB_PORT = int(os.environ.get('MYSQLPORT', 3306))
            DB_NAME = os.environ.get('MYSQLDATABASE', 'railway')
            DB_USER = os.environ.get('MYSQLUSER', 'root')
            DB_PASSWORD = os.environ.get('MYSQLPASSWORD', '')
        
        # Debug info
        print(f"   Host: {DB_HOST}")
        print(f"   Port: {DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        print(f"   Password: {'*' * len(DB_PASSWORD) if DB_PASSWORD else '(vacía)'}")
        
        # Intento de conexión
        print(f"   Conectando a mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=15,
            read_timeout=30,
            write_timeout=30,
            autocommit=True
        )
        
        print(f"✅ [get_db_connection] Conexión exitosa a {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return connection
        
    except Error as e:
        print(f"❌ [get_db_connection] Error: {e}")
        
        # Debug detallado
        print(f"   Tipo de error: {type(e).__name__}")
        print(f"   Código de error: {e.args[0] if e.args else 'N/A'}")
        
        # Mostrar todas las variables disponibles
        print(f"\n   📋 Todas las variables con 'MYSQL' o 'DB':")
        for key in os.environ:
            key_upper = key.upper()
            if 'MYSQL' in key_upper or 'DB' in key_upper:
                value = os.environ[key]
                if 'PASS' in key_upper:
                    print(f"      {key}: {'*' * len(value)}")
                else:
                    print(f"      {key}: {value}")
        
        return None