import pymysql
from bd.conexion_bd import get_db_connection, close_db_connection
from typing import Dict, Any, Optional

class FisioterapeutaModel:
    @staticmethod
    def validar_credenciales(correo: str, codigo_trabajador: str) -> Optional[Dict[str, Any]]:
        """Valida las credenciales del fisioterapeuta en la base de datos"""
        conn = get_db_connection()
        if conn is None:
            return None
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    Codigo_trabajador,
                    nombre_completo,
                    fisio_correo,
                    telefono,
                    especializacion,
                    franja_horaria_dias,
                    franja_horaria_horas,
                    estado
                FROM terapeuta 
                WHERE fisio_correo = %s AND Codigo_trabajador = %s AND estado = 'activo'
                """
                cursor.execute(sql, (correo, codigo_trabajador))
                terapeuta = cursor.fetchone()
                
                return terapeuta
                
        except Exception as e:
            print(f"Error al validar credenciales del fisioterapeuta: {e}")
            return None
        finally:
            close_db_connection(conn)