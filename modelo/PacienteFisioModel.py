import pymysql
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
import json

class PacienteFisioModel:
    
    @staticmethod
    def get_db_connection():
        """Obtiene conexión a la base de datos"""
        try:
            connection = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                db="fisiosalud-2",
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except pymysql.Error as e:
            print(f"❌ Error al conectar a MySQL: {e}")
            return None

    @staticmethod
    def convertir_objeto_serializable(obj):
        """Convierte cualquier objeto no serializable a string"""
        if obj is None:
            return ''
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        elif isinstance(obj, (int, float, str, bool)):
            return obj
        else:
            return str(obj)

    @staticmethod
    def obtener_pacientes_por_terapeuta(terapeuta: str) -> List[Dict]:
        """Obtiene pacientes confirmados del terapeuta especificado"""
        connection = PacienteFisioModel.get_db_connection()
        if not connection:
            return []
            
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT 
                    p.codigo_cita,
                    p.nombre_completo,
                    p.historial_medico,
                    p.terapeuta_asignado,
                    p.estado_cita,
                    p.tipo_plan,
                    p.precio_plan,
                    c.telefono,
                    c.correo,
                    c.fecha_cita,
                    c.hora_cita,
                    c.servicio,
                    a.telefono as telefono_acudiente
                FROM paciente p
                LEFT JOIN cita c ON p.codigo_cita = c.cita_id
                LEFT JOIN acudiente a ON p.ID_acudiente = a.ID_acudiente
                WHERE p.terapeuta_asignado = %s 
                AND p.estado_cita = 'confirmed'
                ORDER BY c.fecha_cita DESC
                """
                cursor.execute(sql, (terapeuta,))
                resultados = cursor.fetchall()
                print(f"✅ Se encontraron {len(resultados)} pacientes confirmados para el terapeuta: {terapeuta}")
                
                # Convertir todos los pacientes a formato serializable
                pacientes_serializables = []
                for paciente in resultados:
                    paciente_serializable = {}
                    for key, value in paciente.items():
                        paciente_serializable[key] = PacienteFisioModel.convertir_objeto_serializable(value)
                    pacientes_serializables.append(paciente_serializable)
                
                return pacientes_serializables
                
        except Exception as e:
            print(f"❌ Error al obtener pacientes del terapeuta: {e}")
            return []
        finally:
            if connection:
                connection.close()

    @staticmethod
    def obtener_ejercicios_disponibles() -> List[Dict]:
        """Obtiene todos los ejercicios disponibles"""
        connection = PacienteFisioModel.get_db_connection()
        if not connection:
            return []
            
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT 
                    codigo_ejercicio,
                    nombre_ejercicio,
                    descripcion,
                    `duracion (minutos)` as duracion,
                    intensidad,
                    equipamento
                FROM ejercicios
                ORDER BY nombre_ejercicio
                """
                cursor.execute(sql)
                resultados = cursor.fetchall()
                print(f"✅ Se encontraron {len(resultados)} ejercicios disponibles")
                
                # Convertir a formato serializable
                ejercicios_serializables = []
                for ejercicio in resultados:
                    ejercicio_serializable = {}
                    for key, value in ejercicio.items():
                        ejercicio_serializable[key] = PacienteFisioModel.convertir_objeto_serializable(value)
                    ejercicios_serializables.append(ejercicio_serializable)
                
                return ejercicios_serializables
                
        except Exception as e:
            print(f"❌ Error al obtener ejercicios: {e}")
            return []
        finally:
            if connection:
                connection.close()

    @staticmethod
    def actualizar_ejercicios_paciente(codigo_cita: str, ejercicios: List[str]) -> bool:
        """Actualiza los ejercicios de un paciente"""
        connection = PacienteFisioModel.get_db_connection()
        if not connection:
            return False
            
        try:
            with connection.cursor() as cursor:
                # Convertir lista de ejercicios a string separado por comas
                ejercicios_str = ','.join(ejercicios) if ejercicios else ''
                
                sql = """
                UPDATE paciente 
                SET ejercicios_registrados = %s
                WHERE codigo_cita = %s
                """
                
                cursor.execute(sql, (ejercicios_str, codigo_cita))
                connection.commit()
                print(f"✅ Ejercicios actualizados para paciente {codigo_cita}: {ejercicios_str}")
                return True
                
        except Exception as e:
            print(f"❌ Error al actualizar ejercicios del paciente: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def obtener_ejercicios_paciente(codigo_cita: str) -> List[str]:
        """Obtiene los ejercicios registrados de un paciente"""
        connection = PacienteFisioModel.get_db_connection()
        if not connection:
            return []
            
        try:
            with connection.cursor() as cursor:
                sql = "SELECT ejercicios_registrados FROM paciente WHERE codigo_cita = %s"
                cursor.execute(sql, (codigo_cita,))
                resultado = cursor.fetchone()
                
                if resultado and resultado['ejercicios_registrados']:
                    ejercicios = resultado['ejercicios_registrados'].split(',')
                    return [ej.strip() for ej in ejercicios if ej.strip()]
                return []
                
        except Exception as e:
            print(f"❌ Error al obtener ejercicios del paciente: {e}")
            return []
        finally:
            if connection:
                connection.close()

    @staticmethod
    def eliminar_paciente(codigo_cita: str) -> bool:
        """Elimina un paciente de la tabla paciente"""
        connection = PacienteFisioModel.get_db_connection()
        if not connection:
            return False
            
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM paciente WHERE codigo_cita = %s"
                cursor.execute(sql, (codigo_cita,))
                connection.commit()
                print(f"✅ Paciente {codigo_cita} eliminado correctamente")
                return True
                
        except Exception as e:
            print(f"❌ Error al eliminar paciente: {e}")
            if connection:
                connection.rollback()
            return False
        finally:
            if connection:
                connection.close()

    @staticmethod
    def obtener_estadisticas_pacientes(terapeuta: str) -> Dict:
        """Obtiene estadísticas de pacientes para el terapeuta"""
        connection = PacienteFisioModel.get_db_connection()
        if not connection:
            return {}
            
        try:
            with connection.cursor() as cursor:
                # Total pacientes confirmados
                sql_total = """
                SELECT COUNT(*) as total 
                FROM paciente 
                WHERE terapeuta_asignado = %s AND estado_cita = 'confirmed'
                """
                cursor.execute(sql_total, (terapeuta,))
                total = cursor.fetchone()['total']
                
                # Pacientes con ejercicios asignados
                sql_con_ejercicios = """
                SELECT COUNT(*) as count 
                FROM paciente 
                WHERE terapeuta_asignado = %s 
                AND estado_cita = 'confirmed'
                AND ejercicios_registrados IS NOT NULL 
                AND ejercicios_registrados != ''
                """
                cursor.execute(sql_con_ejercicios, (terapeuta,))
                con_ejercicios = cursor.fetchone()['count']
                
                # Tipos de planes
                sql_planes = """
                SELECT tipo_plan, COUNT(*) as count 
                FROM paciente 
                WHERE terapeuta_asignado = %s AND estado_cita = 'confirmed'
                GROUP BY tipo_plan
                """
                cursor.execute(sql_planes, (terapeuta,))
                planes = cursor.fetchall()
                distribucion_planes = {p['tipo_plan']: p['count'] for p in planes if p['tipo_plan']}
                
                estadisticas = {
                    'total_pacientes': total,
                    'pacientes_con_ejercicios': con_ejercicios,
                    'pacientes_sin_ejercicios': total - con_ejercicios,
                    'distribucion_planes': distribucion_planes
                }
                
                print(f"📊 Estadísticas obtenidas para {terapeuta}: {estadisticas}")
                return estadisticas
                
        except Exception as e:
            print(f"❌ Error al obtener estadísticas de pacientes: {e}")
            return {}
        finally:
            if connection:
                connection.close()