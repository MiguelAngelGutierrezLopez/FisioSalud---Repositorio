# conexion_bd.py - VERSIÓN QUE FUNCIONA CON AMBAS CONEXIONES
import pymysql
from pymysql import Error
import os

def get_db_connection():
    """Conexión inteligente que maneja tanto conexión interna como externa"""
    try:
        print(f"\n🔍 [get_db_connection] Iniciando...")
        
        # Obtener configuración
        host = os.environ.get('MYSQLHOST', 'localhost')
        port_str = os.environ.get('MYSQLPORT', '3306')
        database = os.environ.get('MYSQLDATABASE', 'fisiosalud-2')
        user = os.environ.get('MYSQLUSER', 'root')
        password = os.environ.get('MYSQLPASSWORD', '')
        
        # Convertir puerto a int
        try:
            port = int(port_str)
        except ValueError:
            port = 3306
        
        print(f"   Configuración:")
        print(f"   • Host: {host}")
        print(f"   • Port: {port}")
        print(f"   • Database: {database}")
        print(f"   • User: {user}")
        
        # Determinar tipo de conexión
        if 'railway.internal' in host:
            print(f"   🏠 Conexión INTERNA (servicio a servicio)")
            # Para conexión interna, SIEMPRE usar 3306
            if port != 3306:
                print(f"   ⚠️  Ajustando puerto a 3306 para conexión interna")
                port = 3306
        else:
            print(f"   🌐 Conexión EXTERNA")
        
        print(f"   Conectando a {host}:{port}/{database}...")
        
        connection = pymysql.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=15,
            autocommit=True,
        )
        
        print(f"✅ Conexión exitosa!")
        
        # Verificar la base de datos actual
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE() as db, USER() as user, @@version as version")
            info = cursor.fetchone()
            print(f"   • Base de datos: {info['db']}")
            print(f"   • Usuario: {info['user']}")
            print(f"   • MySQL: {info['version']}")
        
        return connection
        
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        
        # Diagnóstico detallado
        print(f"\n🔧 DIAGNÓSTICO:")
        print(f"   Error code: {e.args[0] if e.args else 'N/A'}")
        print(f"   Error message: {e.args[1] if len(e.args) > 1 else str(e)}")
        
        # Sugerencias basadas en el error
        if "Connection refused" in str(e):
            if port == 21670 and 'railway.internal' in host:
                print(f"\n💡 SUGERENCIA: mysql.railway.internal requiere puerto 3306, no 21670")
                print(f"   Cambia MYSQLPORT=21670 → MYSQLPORT=3306")
            elif port == 3306 and 'proxy.rlwy.net' in host:
                print(f"\n💡 SUGERENCIA: interchange.proxy.rlwy.net requiere puerto 21670, no 3306")
                print(f"   Cambia MYSQLPORT=3306 → MYSQLPORT=21670")
        
        return None

def close_db_connection(connection):
    if connection:
        try:
            connection.close()
            print("✅ Conexión cerrada")
        except Error as e:
            print(f"⚠️ Error cerrando: {e}")