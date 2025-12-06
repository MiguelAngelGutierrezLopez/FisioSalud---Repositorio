# conexion_bd.py - VERSIÓN INTELIGENTE PARA RAILWAY
import pymysql
from pymysql import Error
import os
import socket

def get_db_connection():
    """Conexión inteligente que prueba diferentes bases de datos"""
    try:
        print(f"\n🔍 [get_db_connection] Detectando entorno Railway...")
        
        # Obtener variables
        host = os.environ.get('MYSQLHOST', 'localhost')
        port = int(os.environ.get('MYSQLPORT', 3306))
        
        # Lista de bases de datos a intentar (en orden de prioridad)
        possible_databases = [
            os.environ.get('MYSQLDATABASE', 'railway'),
            'fisiosalud-2',
            'railway_db_fisiosalud',
            'railway'
        ]
        
        user = os.environ.get('MYSQLUSER', 'root')
        password = os.environ.get('MYSQLPASSWORD', '')
        
        print(f"   Host: {host}:{port}")
        print(f"   User: {user}")
        
        # Intentar con cada base de datos
        for db_name in possible_databases:
            if not db_name:
                continue
                
            print(f"\n   Probando base de datos: '{db_name}'...")
            
            try:
                connection = pymysql.connect(
                    host=host,
                    port=port,
                    database=db_name,
                    user=user,
                    password=password,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=10,
                    autocommit=True,
                )
                
                # Verificar que tenga la tabla 'usuario'
                with connection.cursor() as cursor:
                    cursor.execute("SHOW TABLES LIKE 'usuario'")
                    has_usuario_table = cursor.fetchone() is not None
                    
                    if has_usuario_table:
                        print(f"   ✅ Base de datos '{db_name}' tiene tabla 'usuario'")
                        print(f"   ✅ Usando base de datos: {db_name}")
                        return connection
                    else:
                        print(f"   ❌ Base de datos '{db_name}' NO tiene tabla 'usuario'")
                        connection.close()
                        
            except Exception as e:
                print(f"   ⚠️  Error con base de datos '{db_name}': {e}")
                continue
        
        print(f"\n❌ No se encontró ninguna base de datos con la tabla 'usuario'")
        return None
        
    except Error as e:
        print(f"❌ Error de conexión MySQL: {e}")
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