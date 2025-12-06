# modelo/EjercicioPacienteModel.py (VERSIÓN CORREGIDA)
from bd.conexion_bd import get_db_connection, close_db_connection
from datetime import datetime, date
import json

class EjercicioPacienteModel:
    
    @staticmethod
    def obtener_ejercicios_por_paciente(id_usuario):
        """Obtiene todos los ejercicios asignados a un paciente"""
        conn = get_db_connection()
        if not conn:
            print("❌ No se pudo conectar a la BD")
            return []
        
        try:
            with conn.cursor() as cursor:
                # Primero obtenemos los nombres de ejercicios del paciente
                query_paciente = """
                SELECT ejercicios_registrados 
                FROM paciente 
                WHERE ID_usuario = %s
                """
                cursor.execute(query_paciente, (id_usuario,))
                paciente_data = cursor.fetchone()
                
                print(f"🔍 Datos del paciente: {paciente_data}")
                
                if not paciente_data:
                    print("❌ No se encontró el paciente")
                    return []
                
                if not paciente_data['ejercicios_registrados']:
                    print("ℹ️ No hay ejercicios registrados para este paciente")
                    return []
                
                # Parsear los ejercicios registrados
                ejercicios_nombres = []
                ejercicios_str = paciente_data['ejercicios_registrados']
                print(f"🔍 Ejercicios registrados (raw): {ejercicios_str}")
                
                # Siempre tratar como lista separada por comas
                ejercicios_nombres = [nombre.strip() for nombre in ejercicios_str.split(',') if nombre.strip()]
                
                print(f"🔍 Nombres de ejercicios extraídos: {ejercicios_nombres}")
                
                if not ejercicios_nombres:
                    print("ℹ️ No se pudieron extraer nombres de ejercicios")
                    return []
                
                # Obtener detalles de los ejercicios por NOMBRE
                placeholders = ','.join(['%s'] * len(ejercicios_nombres))
                query_ejercicios = f"""
                SELECT * FROM ejercicios 
                WHERE nombre_ejercicio IN ({placeholders})
                """
                print(f"🔍 Query: {query_ejercicios}")
                print(f"🔍 Parámetros: {ejercicios_nombres}")
                
                cursor.execute(query_ejercicios, ejercicios_nombres)
                ejercicios = cursor.fetchall()
                
                print(f"✅ Ejercicios encontrados en BD: {len(ejercicios)}")
                for ej in ejercicios:
                    print(f"   - {ej['codigo_ejercicio']}: {ej['nombre_ejercicio']}")
                
                return ejercicios
                
        except Exception as e:
            print(f"❌ Error en modelo obtener_ejercicios_por_paciente: {e}")
            import traceback
            print(traceback.format_exc())
            return []
        finally:
            close_db_connection(conn)
    
    
    
    @staticmethod
    def obtener_ejercicios_completados(id_usuario):
        """Obtiene ejercicios marcados como completados por el paciente"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                query = """
                SELECT e.*, ec.fecha_completado, ec.feedback 
                FROM ejercicios e
                INNER JOIN ejercicios_completados ec ON e.codigo_ejercicio = ec.codigo_ejercicio
                WHERE ec.ID_usuario = %s
                ORDER BY ec.fecha_completado DESC
                """
                cursor.execute(query, (id_usuario,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error en modelo obtener_ejercicios_completados: {e}")
            return []
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_ejercicios_pendientes(id_usuario):
        """Obtiene ejercicios asignados pero no completados"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                # Primero obtenemos todos los ejercicios asignados
                ejercicios_asignados = EjercicioPacienteModel.obtener_ejercicios_por_paciente(id_usuario)
                if not ejercicios_asignados:
                    return []
                
                # Luego obtenemos los completados
                ejercicios_completados = EjercicioPacienteModel.obtener_ejercicios_completados(id_usuario)
                codigos_completados = [ej['codigo_ejercicio'] for ej in ejercicios_completados]
                
                # Filtramos los no completados
                ejercicios_pendientes = [ej for ej in ejercicios_asignados if ej['codigo_ejercicio'] not in codigos_completados]
                
                return ejercicios_pendientes
                
        except Exception as e:
            print(f"Error en modelo obtener_ejercicios_pendientes: {e}")
            return []
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def marcar_como_completado(id_usuario, codigo_ejercicio, feedback=None, nivel_dificultad=None):
        """Marca un ejercicio como completado por el paciente"""
        conn = get_db_connection()
        if not conn:
            return False, "Error de conexión"
        
        try:
            with conn.cursor() as cursor:
                # Verificar si ya está completado
                check_query = """
                SELECT * FROM ejercicios_completados 
                WHERE ID_usuario = %s AND codigo_ejercicio = %s
                """
                cursor.execute(check_query, (id_usuario, codigo_ejercicio))
                
                if cursor.fetchone():
                    return False, "Este ejercicio ya fue marcado como completado"
                
                # Insertar en ejercicios completados
                insert_query = """
                INSERT INTO ejercicios_completados 
                (ID_usuario, codigo_ejercicio, fecha_completado, feedback, nivel_dificultad)
                VALUES (%s, %s, NOW(), %s, %s)
                """
                cursor.execute(insert_query, (id_usuario, codigo_ejercicio, feedback, nivel_dificultad))
                conn.commit()
                
                return True, "Ejercicio marcado como completado exitosamente"
                
        except Exception as e:
            print(f"Error en modelo marcar_como_completado: {e}")
            return False, "Error interno al marcar ejercicio como completado"
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_estadisticas_ejercicios(id_usuario):
        """Obtiene estadísticas de ejercicios del paciente"""
        conn = get_db_connection()
        if not conn:
            return {}
        
        try:
            with conn.cursor() as cursor:
                # Obtener ejercicios asignados
                ejercicios_asignados = EjercicioPacienteModel.obtener_ejercicios_por_paciente(id_usuario)
                total_asignados = len(ejercicios_asignados)
                
                # Obtener ejercicios completados
                ejercicios_completados = EjercicioPacienteModel.obtener_ejercicios_completados(id_usuario)
                total_completados = len(ejercicios_completados)
                
                # Obtener ejercicios pendientes para hoy (todos los pendientes)
                ejercicios_pendientes = EjercicioPacienteModel.obtener_ejercicios_pendientes(id_usuario)
                pendientes_hoy = len(ejercicios_pendientes)
                
                # Calcular días seguidos (simplificado)
                query_dias_seguidos = """
                SELECT COUNT(DISTINCT DATE(fecha_completado)) as dias_seguidos
                FROM ejercicios_completados 
                WHERE ID_usuario = %s 
                AND fecha_completado >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                """
                cursor.execute(query_dias_seguidos, (id_usuario,))
                dias_seguidos_data = cursor.fetchone()
                dias_seguidos = dias_seguidos_data['dias_seguidos'] if dias_seguidos_data else 0
                
                return {
                    'total_asignados': total_asignados,
                    'total_completados': total_completados,
                    'pendientes_hoy': pendientes_hoy,
                    'dias_seguidos': dias_seguidos
                }
                
        except Exception as e:
            print(f"Error en modelo obtener_estadisticas_ejercicios: {e}")
            return {
                'total_asignados': 0,
                'total_completados': 0,
                'pendientes_hoy': 0,
                'dias_seguidos': 0
            }
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_ejercicio_por_codigo(codigo_ejercicio):
        """Obtiene un ejercicio específico por su código"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM ejercicios WHERE codigo_ejercicio = %s"
                cursor.execute(query, (codigo_ejercicio,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error en modelo obtener_ejercicio_por_codigo: {e}")
            return None
        finally:
            close_db_connection(conn)