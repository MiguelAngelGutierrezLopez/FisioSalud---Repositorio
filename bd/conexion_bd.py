# conexion_bd.py - VERSIÓN INTELIGENTE PARA RAILWAY
import pymysql
from pymysql import Error
import os
import socket

def get_db_connection():
    """Conexión inteligente que detecta el entorno Railway"""
    try:
        print(f"\n🔍 [get_db_connection] Detectando entorno Railway...")
        
        # Obtener variables
        host = os.environ.get('MYSQLHOST', 'localhost')
        port = int(os.environ.get('MYSQLPORT', 3306))
        database = os.environ.get('MYSQLDATABASE', 'railway')
        user = os.environ.get('MYSQLUSER', 'root')
        password = os.environ.get('MYSQLPASSWORD', '')
        
        print(f"   Host original: {host}:{port}")
        
        # DETECCIÓN AUTOMÁTICA: Si es host interno de Railway, usar puerto 3306
        if host == 'mysql.railway.internal' and port == 21670:
            print("   ⚠️  Ajustando: mysql.railway.internal debe usar puerto 3306")
            port = 3306
        
        # Si el host contiene 'railway.internal', es conexión interna
        if 'railway.internal' in host:
            print(f"   🏠 Conexión INTERNA a Railway")
            print(f"   Host ajustado: {host}:{port}")
        else:
            print(f"   🌐 Conexión EXTERNA a Railway")
        
        print(f"   Database: {database}")
        print(f"   User: {user}")
        print(f"   Password: {'*' * len(password) if password else '(vacía)'}")
        
        # Intentar conexión con timeout más largo
        print(f"   Conectando...")
        
        connection = pymysql.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=30,  # Más tiempo para Railway
            read_timeout=60,
            write_timeout=60,
            autocommit=True,
            # Parámetros específicos para MySQL 8+ en Railway
            ssl={'ssl': {}} if 'proxy.rlwy.net' in host else None,
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
        )
        
        print(f"✅ Conexión exitosa a MySQL en {host}:{port}")
        
        # Test de conexión
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test, @@version as version")
            result = cursor.fetchone()
            print(f"   Test query: OK, MySQL version: {result['version']}")
        
        return connection
        
    except Error as e:
        print(f"❌ Error de conexión MySQL: {e}")
        
        # Diagnóstico detallado
        error_code = e.args[0] if e.args else 'N/A'
        error_msg = e.args[1] if len(e.args) > 1 else str(e)
        
        print(f"\n🔧 DIAGNÓSTICO DETALLADO:")
        print(f"   Error code: {error_code}")
        print(f"   Error message: {error_msg}")
        
        # Intentar diagnóstico de red
        try:
            print(f"\n🌐 DIAGNÓSTICO DE RED:")
            print(f"   Resolviendo DNS para {host}...")
            ip = socket.gethostbyname(host)
            print(f"   DNS resuelto: {host} → {ip}")
            
            # Intentar conexión TCP básica
            print(f"   Probando conexión TCP a {ip}:{port}...")
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(10)
            result = test_sock.connect_ex((ip, port))
            test_sock.close()
            
            if result == 0:
                print(f"   ✅ Puerto {port} está ABIERTO en {host}")
            else:
                print(f"   ❌ Puerto {port} está CERRADO en {host} (código: {result})")
                
        except Exception as net_err:
            print(f"   ⚠️ Error en diagnóstico de red: {net_err}")
        
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