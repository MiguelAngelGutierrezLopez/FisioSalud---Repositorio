from datetime import datetime, date, time
import pymysql
from bd.conexion_bd import get_db_connection, close_db_connection
from typing import Dict, Any, Optional, List
from decimal import Decimal

class AdminCitaModel:
    
    # ===== ESTADÍSTICAS GENERALES =====
    
    @staticmethod
    def obtener_estadisticas_citas() -> Dict[str, Any]:
        """
        Obtiene estadísticas de citas
        """
        conn = get_db_connection()
        if conn is None:
            return {
                'total_hoy': 0,
                'total_pendientes': 0,
                'total_semana': 0,
                'total_todas': 0,
                'distribucion_estados': {},
                'citas_por_terapeuta': {}
            }
        
        try:
            with conn.cursor() as cursor:
                hoy = date.today()
                
                # Obtener fecha de inicio de semana (lunes)
                inicio_semana = hoy
                while inicio_semana.weekday() != 0:  # 0 es lunes
                    inicio_semana = inicio_semana.replace(day=inicio_semana.day - 1)
                
                # 1. Citas para hoy
                sql_hoy = """
                SELECT COUNT(*) as total
                FROM cita
                WHERE fecha_cita = %s
                """
                cursor.execute(sql_hoy, (hoy,))
                stats_hoy = cursor.fetchone()
                
                # 2. Citas pendientes (estado = 'Pendiente' o 'Confirmada')
                sql_pendientes = """
                SELECT COUNT(*) as total
                FROM cita
                WHERE estado IN ('Pendiente', 'Confirmada')
                """
                cursor.execute(sql_pendientes)
                stats_pendientes = cursor.fetchone()
                
                # 3. Citas esta semana
                sql_semana = """
                SELECT COUNT(*) as total
                FROM cita
                WHERE fecha_cita BETWEEN %s AND %s
                """
                cursor.execute(sql_semana, (inicio_semana, hoy))
                stats_semana = cursor.fetchone()
                
                # 4. Total de citas
                sql_total = """
                SELECT COUNT(*) as total
                FROM cita
                """
                cursor.execute(sql_total)
                stats_total = cursor.fetchone()
                
                # 5. Distribución por estado
                sql_estados = """
                SELECT estado, COUNT(*) as cantidad
                FROM cita
                GROUP BY estado
                """
                cursor.execute(sql_estados)
                estados_data = cursor.fetchall()
                distribucion_estados = {estado['estado']: estado['cantidad'] for estado in estados_data}
                
                # 6. Citas por terapeuta
                sql_terapeutas = """
                SELECT terapeuta_designado, COUNT(*) as cantidad
                FROM cita
                GROUP BY terapeuta_designado
                ORDER BY cantidad DESC
                LIMIT 5
                """
                cursor.execute(sql_terapeutas)
                terapeutas_data = cursor.fetchall()
                citas_por_terapeuta = {terap['terapeuta_designado']: terap['cantidad'] for terap in terapeutas_data}
                
                return {
                    'total_hoy': int(stats_hoy['total'] or 0),
                    'total_pendientes': int(stats_pendientes['total'] or 0),
                    'total_semana': int(stats_semana['total'] or 0),
                    'total_todas': int(stats_total['total'] or 0),
                    'distribucion_estados': distribucion_estados,
                    'citas_por_terapeuta': citas_por_terapeuta,
                    'fecha_hoy': hoy.strftime('%Y-%m-%d'),
                    'inicio_semana': inicio_semana.strftime('%Y-%m-%d')
                }
                
        except Exception as e:
            print(f"Error en obtener_estadisticas_citas: {e}")
            return {
                'total_hoy': 0,
                'total_pendientes': 0,
                'total_semana': 0,
                'total_todas': 0,
                'distribucion_estados': {},
                'citas_por_terapeuta': {}
            }
        finally:
            close_db_connection(conn)
    
    # ===== LISTAR CITAS =====
    
    @staticmethod
    def listar_citas(filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Lista citas con filtros opcionales
        """
        if filtros is None:
            filtros = {}
        
        conn = get_db_connection()
        if conn is None:
            return []
        
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                SELECT 
                    cita_id,
                    nombre_paciente,
                    servicio,
                    terapeuta_designado,
                    telefono,
                    correo,
                    DATE_FORMAT(fecha_cita, '%%Y-%%m-%%d') as fecha_cita,
                    TIME_FORMAT(hora_cita, '%%H:%%i') as hora_cita,
                    notas_adicionales,
                    tipo_pago,
                    estado
                FROM cita
                WHERE 1=1
                """
                
                params = []
                
                if filtros.get('fecha'):
                    sql += " AND fecha_cita = %s"
                    params.append(filtros['fecha'])
                
                if filtros.get('paciente'):
                    sql += " AND nombre_paciente LIKE %s"
                    params.append(f"%{filtros['paciente']}%")
                
                if filtros.get('terapeuta'):
                    sql += " AND terapeuta_designado = %s"
                    params.append(filtros['terapeuta'])
                
                if filtros.get('estado'):
                    sql += " AND estado = %s"
                    params.append(filtros['estado'])
                
                if filtros.get('fecha_desde'):
                    sql += " AND fecha_cita >= %s"
                    params.append(filtros['fecha_desde'])
                
                if filtros.get('fecha_hasta'):
                    sql += " AND fecha_cita <= %s"
                    params.append(filtros['fecha_hasta'])
                
                sql += " ORDER BY fecha_cita DESC, hora_cita DESC"
                
                cursor.execute(sql, params)
                citas = cursor.fetchall()
                
                return citas
                
        except Exception as e:
            print(f"Error en listar_citas: {e}")
            return []
        finally:
            close_db_connection(conn)
    
    # ===== OBTENER CITA POR ID =====
    
    @staticmethod
    def obtener_cita_por_id(cita_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una cita por su ID
        """
        conn = get_db_connection()
        if conn is None:
            return None
        
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                SELECT 
                    cita_id,
                    nombre_paciente,
                    servicio,
                    terapeuta_designado,
                    telefono,
                    correo,
                    DATE_FORMAT(fecha_cita, '%%Y-%%m-%%d') as fecha_cita,
                    TIME_FORMAT(hora_cita, '%%H:%%i') as hora_cita,
                    notas_adicionales,
                    tipo_pago,
                    estado
                FROM cita
                WHERE cita_id = %s
                """
                
                cursor.execute(sql, (cita_id,))
                cita = cursor.fetchone()
                
                return cita
                
        except Exception as e:
            print(f"Error en obtener_cita_por_id: {e}")
            return None
        finally:
            close_db_connection(conn)
    
    # ===== CREAR CITA =====
    
    @staticmethod
    def crear_cita(cita_data: Dict[str, Any]) -> tuple[bool, str, str]:
        """
        Crea una nueva cita
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos", ""
        
        try:
            with conn.cursor() as cursor:
                # Generar ID único si no viene
                if 'cita_id' not in cita_data or not cita_data['cita_id']:
                    # Generar ID basado en timestamp y random
                    import random
                    import string
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    cita_id = f"CITA-{timestamp}-{random_str}"
                    cita_data['cita_id'] = cita_id
                else:
                    cita_id = cita_data['cita_id']
                
                # Verificar si el ID ya existe
                sql_check = "SELECT cita_id FROM cita WHERE cita_id = %s"
                cursor.execute(sql_check, (cita_id,))
                if cursor.fetchone():
                    return False, "El ID de cita ya existe", ""
                
                # Insertar nueva cita
                sql_insert = """
                INSERT INTO cita (
                    cita_id, nombre_paciente, servicio, terapeuta_designado,
                    telefono, correo, fecha_cita, hora_cita, notas_adicionales,
                    tipo_pago, estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql_insert, (
                    cita_id,
                    cita_data['nombre_paciente'],
                    cita_data['servicio'],
                    cita_data['terapeuta_designado'],
                    cita_data.get('telefono', ''),
                    cita_data.get('correo', ''),
                    cita_data['fecha_cita'],
                    cita_data['hora_cita'],
                    cita_data.get('notas_adicionales', ''),
                    cita_data['tipo_pago'],
                    cita_data.get('estado', 'Pendiente')
                ))
                
                conn.commit()
                return True, "Cita creada exitosamente", cita_id
                
        except Exception as e:
            conn.rollback()
            print(f"Error al crear cita: {e}")
            return False, str(e), ""
        finally:
            close_db_connection(conn)
    
    # ===== ACTUALIZAR CITA =====
    
    @staticmethod
    def actualizar_cita(cita_id: str, cita_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Actualiza una cita existente
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar que la cita existe
                sql_check = "SELECT cita_id FROM cita WHERE cita_id = %s"
                cursor.execute(sql_check, (cita_id,))
                if not cursor.fetchone():
                    return False, "Cita no encontrada"
                
                # Actualizar cita
                sql_update = """
                UPDATE cita SET
                    nombre_paciente = %s,
                    servicio = %s,
                    terapeuta_designado = %s,
                    telefono = %s,
                    correo = %s,
                    fecha_cita = %s,
                    hora_cita = %s,
                    notas_adicionales = %s,
                    tipo_pago = %s,
                    estado = %s
                WHERE cita_id = %s
                """
                
                cursor.execute(sql_update, (
                    cita_data['nombre_paciente'],
                    cita_data['servicio'],
                    cita_data['terapeuta_designado'],
                    cita_data.get('telefono', ''),
                    cita_data.get('correo', ''),
                    cita_data['fecha_cita'],
                    cita_data['hora_cita'],
                    cita_data.get('notas_adicionales', ''),
                    cita_data['tipo_pago'],
                    cita_data.get('estado', 'Pendiente'),
                    cita_id
                ))
                
                conn.commit()
                return True, "Cita actualizada exitosamente"
                
        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar cita: {e}")
            return False, str(e)
        finally:
            close_db_connection(conn)
    
    # ===== CAMBIAR ESTADO DE CITA =====
    
    @staticmethod
    def cambiar_estado_cita(cita_id: str, nuevo_estado: str) -> tuple[bool, str]:
        """
        Cambia el estado de una cita
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar que la cita existe
                sql_check = "SELECT cita_id FROM cita WHERE cita_id = %s"
                cursor.execute(sql_check, (cita_id,))
                if not cursor.fetchone():
                    return False, "Cita no encontrada"
                
                # Actualizar estado
                sql_update = "UPDATE cita SET estado = %s WHERE cita_id = %s"
                cursor.execute(sql_update, (nuevo_estado, cita_id))
                
                conn.commit()
                return True, f"Estado cambiado a '{nuevo_estado}' exitosamente"
                
        except Exception as e:
            conn.rollback()
            print(f"Error al cambiar estado de cita: {e}")
            return False, str(e)
        finally:
            close_db_connection(conn)
    
    # ===== ELIMINAR CITA =====
    
    @staticmethod
    def eliminar_cita(cita_id: str) -> tuple[bool, str]:
        """
        Elimina una cita
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar que la cita existe
                sql_check = "SELECT cita_id FROM cita WHERE cita_id = %s"
                cursor.execute(sql_check, (cita_id,))
                if not cursor.fetchone():
                    return False, "Cita no encontrada"
                
                # Eliminar cita
                sql_delete = "DELETE FROM cita WHERE cita_id = %s"
                cursor.execute(sql_delete, (cita_id,))
                
                conn.commit()
                return True, "Cita eliminada exitosamente"
                
        except Exception as e:
            conn.rollback()
            print(f"Error al eliminar cita: {e}")
            return False, str(e)
        finally:
            close_db_connection(conn)
    
    # ===== OBTENER CITAS POR SEMANA =====
    
    @staticmethod
    def obtener_citas_semana(fecha_inicio: str, fecha_fin: str) -> List[Dict[str, Any]]:
        """
        Obtiene citas para una semana específica
        """
        conn = get_db_connection()
        if conn is None:
            return []
        
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                SELECT 
                    cita_id,
                    nombre_paciente,
                    servicio,
                    terapeuta_designado,
                    DATE_FORMAT(fecha_cita, '%%Y-%%m-%%d') as fecha_cita,
                    TIME_FORMAT(hora_cita, '%%H:%%i') as hora_cita,
                    estado
                FROM cita
                WHERE fecha_cita BETWEEN %s AND %s
                ORDER BY fecha_cita ASC, hora_cita ASC
                """
                
                cursor.execute(sql, (fecha_inicio, fecha_fin))
                citas = cursor.fetchall()
                
                return citas
                
        except Exception as e:
            print(f"Error en obtener_citas_semana: {e}")
            return []
        finally:
            close_db_connection(conn)