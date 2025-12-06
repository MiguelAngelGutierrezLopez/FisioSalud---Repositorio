# modelo/CitaModel.py
from bd.conexion_bd import get_db_connection, close_db_connection
from datetime import datetime, date
import uuid

class CitaPacienteModel:
    
    @staticmethod
    def generar_id_cita():
        """Genera un ID único para la cita"""
        return f"CITA{str(uuid.uuid4())[:6].upper()}"
    
    @staticmethod
    def crear_cita(datos_cita):
        """Crea una nueva cita en la base de datos"""
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar disponibilidad del terapeuta
                check_query = """
                SELECT cita_id FROM cita 
                WHERE terapeuta_designado = %s AND fecha_cita = %s AND hora_cita = %s AND estado != 'cancelada'
                """
                cursor.execute(check_query, (
                    datos_cita['terapeuta_designado'],
                    datos_cita['fecha_cita'],
                    datos_cita['hora_cita']
                ))
                
                if cursor.fetchone():
                    return None, "El terapeuta ya tiene una cita programada en ese horario"
                
                # Insertar nueva cita
                cita_id = CitaPacienteModel.generar_id_cita()
                sql = """
                INSERT INTO cita (
                    cita_id, nombre_paciente, servicio, terapeuta_designado, 
                    telefono, correo, fecha_cita, hora_cita, notas_adicionales, 
                    tipo_pago, estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pendiente')
                """
                
                cursor.execute(sql, (
                    cita_id,
                    datos_cita['nombre_paciente'],
                    datos_cita['servicio'],
                    datos_cita['terapeuta_designado'],
                    datos_cita['telefono'],
                    datos_cita['correo'],
                    datos_cita['fecha_cita'],
                    datos_cita['hora_cita'],
                    datos_cita.get('notas_adicionales', ''),
                    datos_cita['tipo_pago']
                ))
                conn.commit()
                return cita_id, "Cita creada exitosamente"
                
        except Exception as e:
            print(f"Error en modelo crear_cita: {e}")
            return None, "Error interno al crear cita"
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_citas_por_paciente(correo_paciente):
        """Obtiene todas las citas de un paciente"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                query = """
                SELECT * FROM cita 
                WHERE correo = %s 
                ORDER BY fecha_cita DESC, hora_cita DESC
                """
                cursor.execute(query, (correo_paciente,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error en modelo obtener_citas_por_paciente: {e}")
            return []
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_citas_proximas(correo_paciente, dias=30):
        """Obtiene citas próximas del paciente"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                query = """
                SELECT * FROM cita 
                WHERE correo = %s 
                AND fecha_cita >= CURDATE() 
                AND fecha_cita <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
                AND estado IN ('pendiente', 'confirmada')
                ORDER BY fecha_cita ASC, hora_cita ASC
                """
                cursor.execute(query, (correo_paciente, dias))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error en modelo obtener_citas_proximas: {e}")
            return []
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_cita_por_id(cita_id):
        """Obtiene una cita específica por ID"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM cita WHERE cita_id = %s"
                cursor.execute(query, (cita_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error en modelo obtener_cita_por_id: {e}")
            return None
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def actualizar_estado_cita(cita_id, nuevo_estado):
        """Actualiza el estado de una cita"""
        conn = get_db_connection()
        if not conn:
            return False, "Error de conexión"
        
        try:
            with conn.cursor() as cursor:
                query = "UPDATE cita SET estado = %s WHERE cita_id = %s"
                cursor.execute(query, (nuevo_estado, cita_id))
                conn.commit()
                return True, "Estado actualizado exitosamente"
        except Exception as e:
            print(f"Error en modelo actualizar_estado_cita: {e}")
            return False, "Error interno al actualizar estado"
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_estadisticas_paciente(correo_paciente):
        """Obtiene estadísticas de citas del paciente"""
        conn = get_db_connection()
        if not conn:
            return {}
        
        try:
            with conn.cursor() as cursor:
                query = """
                SELECT 
                    COUNT(*) as total_citas,
                    SUM(CASE WHEN estado = 'completada' THEN 1 ELSE 0 END) as completadas,
                    SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as pendientes,
                    SUM(CASE WHEN estado = 'confirmada' THEN 1 ELSE 0 END) as confirmadas,
                    SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) as canceladas,
                    MIN(fecha_cita) as primera_cita,
                    MAX(fecha_cita) as ultima_cita
                FROM cita 
                WHERE correo = %s
                """
                cursor.execute(query, (correo_paciente,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error en modelo obtener_estadisticas_paciente: {e}")
            return {}
        finally:
            close_db_connection(conn)