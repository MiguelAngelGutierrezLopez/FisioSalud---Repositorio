# conexion_bd.py - VERSIÓN DEFINITIVA PARA RAILWAY
import pymysql
from pymysql import Error
import os

def get_db_connection():
    """Obtiene conexión a MySQL en Railway"""
    try:
        print(f"\n🔍 [get_db_connection] Buscando configuración...")
        
        # DEBUG: Mostrar qué variables tenemos
        env_vars = dict(os.environ)
        print(f"   Variables disponibles: {len(env_vars)}")
        
        # Buscar TODAS las posibles fuentes de configuración
        # 1. Variables MYSQL_ (Railway automático)
        # 2. Variables DB_ (tus variables manuales)
        # 3. MYSQL_PUBLIC_URL (URL completa)
        
        sources = []
        
        # Fuente 1: MYSQL_
        if 'MYSQLHOST' in env_vars:
            DB_HOST = env_vars['MYSQLHOST']
            DB_PORT = int(env_vars.get('MYSQLPORT', 3306))
            DB_NAME = env_vars.get('MYSQLDATABASE', 'railway')
            DB_USER = env_vars.get('MYSQLUSER', 'root')
            DB_PASSWORD = env_vars.get('MYSQLPASSWORD', '')
            sources.append("MYSQL_ variables")
            
        # Fuente 2: DB_
        elif 'DB_HOST' in env_vars:
            DB_HOST = env_vars['DB_HOST']
            DB_PORT = int(env_vars.get('DB_PORT', 3306))
            DB_NAME = env_vars.get('DB_NAME', 'railway')
            DB_USER = env_vars.get('DB_USER', 'root')
            DB_PASSWORD = env_vars.get('DB_PASSWORD', '')
            sources.append("DB_ variables")
            
        # Fuente 3: Ninguna - usar localhost (solo desarrollo)
        else:
            print("⚠️ No se encontraron variables MYSQL_ ni DB_, usando localhost")
            DB_HOST = 'localhost'
            DB_PORT = 3306
            DB_NAME = 'railway'
            DB_USER = 'root'
            DB_PASSWORD = ''
            sources.append("localhost (fallback)")
        
        print(f"✅ Usando: {', '.join(sources)}")
        print(f"   Host: {DB_HOST}")
        print(f"   Port: {DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        print(f"   Password: {'*' * len(DB_PASSWORD) if DB_PASSWORD else '(vacía)'}")
        
        # Intentar conexión
        print(f"   Conectando...")
        
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
        
        print(f"✅ Conexión exitosa a MySQL en {DB_HOST}:{DB_PORT}")
        
        # Verificar que podemos hacer una consulta básica
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE() as db, USER() as user")
            result = cursor.fetchone()
            print(f"   Base de datos: {result['db']}")
            print(f"   Usuario: {result['user']}")
        
        return connection
        
    except Error as e:
        print(f"❌ Error de conexión MySQL: {e}")
        
        # Diagnóstico detallado
        print(f"\n🔧 DIAGNÓSTICO DE CONEXIÓN:")
        print(f"   Error code: {e.args[0] if e.args else 'N/A'}")
        print(f"   Error message: {e.args[1] if len(e.args) > 1 else str(e)}")
        
        # Verificar qué variables tenemos realmente
        print(f"\n📋 VARIABLES DE CONEXIÓN DISPONIBLES:")
        mysql_keys = [k for k in env_vars.keys() if 'MYSQL' in k.upper() or 'DB' in k.upper()]
        
        if mysql_keys:
            for key in sorted(mysql_keys):
                value = env_vars[key]
                if 'PASS' in key.upper():
                    print(f"   {key}: {'*' * len(value)}")
                else:
                    print(f"   {key}: {value}")
        else:
            print(f"   ❌ No hay variables MYSQL_ o DB_")
            print(f"   Todas las variables disponibles ({len(env_vars)}):")
            for key in sorted(env_vars.keys())[:10]:  # Mostrar primeras 10
                print(f"     {key}: {env_vars[key]}")
        
        return None

def close_db_connection(connection):
    """Cierra la conexión de manera segura"""
    if connection:
        try:
            connection.close()
            print("✅ Conexión MySQL cerrada correctamente")
        except Error as e:
            print(f"⚠️ Error al cerrar conexión: {e}")
    else:
        print("⚠️ Intento de cerrar conexión nula")