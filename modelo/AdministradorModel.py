import pymysql
from bd.conexion_bd import get_db_connection, close_db_connection
from typing import Dict, Any, Optional
import hashlib

class AdministradorModel:
    
    @staticmethod
    def validar_credenciales_admin(correo: str, contraseña: str) -> Optional[Dict[str, Any]]:
        """
        Valida credenciales del administrador en la base de datos
        """
        print(f"📊 [MODELO] Validando credenciales para: {correo}")
        
        conn = get_db_connection()
        if conn is None:
            print("❌ [MODELO] No se pudo conectar a la BD")
            return None
        
        try:
            with conn.cursor() as cursor:
                # Hashear la contraseña para comparar
                contraseña_hash = hashlib.sha256(contraseña.encode()).hexdigest()
                print(f"🔑 [MODELO] Contraseña ingresada: {contraseña}")
                print(f"🔑 [MODELO] Hash SHA256 calculado: {contraseña_hash}")
                
                # 1. Primero, veamos EXACTAMENTE qué hay en la BD para este admin
                sql_check = """
                SELECT `Codigo/ID`, nombre, `Correo_electronico`, `Contraseña` 
                FROM administrador 
                WHERE `Correo_electronico` = %s
                """
                cursor.execute(sql_check, (correo,))
                admin_bd = cursor.fetchone()
                
                if admin_bd:
                    print(f"✅ [MODELO] Admin encontrado en BD:")
                    print(f"   - ID: {admin_bd['Codigo/ID']}")
                    print(f"   - Nombre: {admin_bd['nombre']}")
                    print(f"   - Email: {admin_bd['Correo_electronico']}")
                    print(f"   - Contraseña en BD: {admin_bd['Contraseña']}")
                    print(f"   - Longitud contraseña BD: {len(admin_bd['Contraseña'])} caracteres")
                    
                    # Mostrar primeros y últimos caracteres del hash en BD
                    hash_bd = admin_bd['Contraseña']
                    if hash_bd:
                        print(f"   - Hash BD (primeros 20): {hash_bd[:20]}...")
                        print(f"   - Hash BD (últimos 20): ...{hash_bd[-20:]}")
                    
                    # Verificar si es texto plano
                    if len(admin_bd['Contraseña']) < 64:  # SHA256 tiene 64 caracteres hex
                        print(f"⚠️  [MODELO] La contraseña en BD parece NO ser SHA256 (solo {len(admin_bd['Contraseña'])} chars)")
                        print(f"⚠️  [MODELO] Posible texto plano o hash diferente")
                else:
                    print(f"❌ [MODELO] No se encontró admin con correo: {correo}")
                    return None
                
                # 2. Intentar login con SHA256
                sql = """
                SELECT 
                    `Codigo/ID` as id,
                    nombre,
                    `Correo_electronico` as correo
                FROM administrador 
                WHERE `Correo_electronico` = %s AND `Contraseña` = %s
                """
                cursor.execute(sql, (correo, contraseña_hash))
                admin = cursor.fetchone()
                
                if admin:
                    print(f"🎉 [MODELO] Login con SHA256 EXITOSO")
                    return admin
                else:
                    print(f"❌ [MODELO] SHA256 no coincide")
                    
                    # 3. Intentar con texto plano (por si está sin hash)
                    sql_plain = """
                    SELECT 
                        `Codigo/ID` as id,
                        nombre,
                        `Correo_electronico` as correo
                    FROM administrador 
                    WHERE `Correo_electronico` = %s AND `Contraseña` = %s
                    """
                    cursor.execute(sql_plain, (correo, contraseña))
                    admin_plain = cursor.fetchone()
                    
                    if admin_plain:
                        print(f"🎉 [MODELO] Login con texto plano EXITOSO")
                        return admin_plain
                    else:
                        print(f"❌ [MODELO] Texto plano tampoco coincide")
                
                return None
                
        except Exception as e:
            print(f"❌ [MODELO] Error al validar credenciales: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            close_db_connection(conn)
            print("🔌 [MODELO] Conexión a BD cerrada")