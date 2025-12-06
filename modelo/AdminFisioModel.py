import pymysql
from bd.conexion_bd import get_db_connection, close_db_connection
from typing import Dict, Any, Optional, List
from decimal import Decimal

class AdminFisioModel:
    
    @staticmethod
    def obtener_estadisticas_terapeutas() -> Dict[str, Any]:
        """
        Obtiene estadísticas de fisioterapeutas
        """
        conn = get_db_connection()
        if conn is None:
            return {
                'total_terapeutas': 0,
                'terapeutas_activos': 0,
                'especializaciones': 0,
                'horarios_definidos': 0
            }
        
        try:
            with conn.cursor() as cursor:
                # 1. Total de terapeutas
                sql_total = "SELECT COUNT(*) as total FROM terapeuta"
                cursor.execute(sql_total)
                total = cursor.fetchone()['total']
                
                # 2. Terapeutas activos
                sql_activos = """
                SELECT COUNT(*) as activos 
                FROM terapeuta 
                WHERE estado = 'Activo'
                """
                cursor.execute(sql_activos)
                activos = cursor.fetchone()['activos']
                
                # 3. Especializaciones únicas
                sql_especialidades = """
                SELECT COUNT(DISTINCT especializacion) as especialidades
                FROM terapeuta 
                WHERE especializacion IS NOT NULL 
                AND TRIM(especializacion) != ''
                """
                cursor.execute(sql_especialidades)
                especialidades = cursor.fetchone()['especialidades']
                
                # 4. Horarios definidos
                sql_horarios = """
                SELECT COUNT(*) as horarios
                FROM terapeuta 
                WHERE franja_horaria_dias IS NOT NULL 
                AND franja_horaria_horas IS NOT NULL
                """
                cursor.execute(sql_horarios)
                horarios = cursor.fetchone()['horarios']
                
                return {
                    'total_terapeutas': int(total),
                    'terapeutas_activos': int(activos),
                    'especializaciones': int(especialidades),
                    'horarios_definidos': int(horarios)
                }
                
        except Exception as e:
            print(f"❌ Error en obtener_estadisticas_terapeutas: {e}")
            return {
                'total_terapeutas': 0,
                'terapeutas_activos': 0,
                'especializaciones': 0,
                'horarios_definidos': 0
            }
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def listar_terapeutas(
        nombre: str = '', 
        especializacion: str = '', 
        estado: str = ''
    ) -> List[Dict[str, Any]]:
        """
        Lista terapeutas con filtros opcionales
        """
        conn = get_db_connection()
        if conn is None:
            return []
        
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
                WHERE 1=1
                """
                
                params = []
                
                if nombre:
                    sql += " AND nombre_completo LIKE %s"
                    params.append(f"%{nombre}%")
                
                if especializacion:
                    sql += " AND especializacion = %s"
                    params.append(especializacion)
                
                if estado:
                    sql += " AND estado = %s"
                    params.append(estado)
                
                sql += " ORDER BY nombre_completo ASC"
                
                cursor.execute(sql, params)
                terapeutas = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                resultado = []
                for terapeuta in terapeutas:
                    terapeuta_dict = dict(terapeuta)
                    
                    # Asegurar que no haya valores Decimal
                    for key, value in terapeuta_dict.items():
                        if isinstance(value, Decimal):
                            terapeuta_dict[key] = float(value)
                    
                    resultado.append(terapeuta_dict)
                
                return resultado
                
        except Exception as e:
            print(f"❌ Error en listar_terapeutas: {e}")
            return []
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_terapeuta_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un terapeuta por su código
        """
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
                WHERE Codigo_trabajador = %s
                """
                
                cursor.execute(sql, (codigo,))
                terapeuta = cursor.fetchone()
                
                if terapeuta:
                    terapeuta_dict = dict(terapeuta)
                    # Asegurar que no haya valores Decimal
                    for key, value in terapeuta_dict.items():
                        if isinstance(value, Decimal):
                            terapeuta_dict[key] = float(value)
                    return terapeuta_dict
                
                return None
                
        except Exception as e:
            print(f"❌ Error en obtener_terapeuta_por_codigo: {e}")
            return None
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def crear_terapeuta(terapeuta_data: Dict[str, Any]) -> tuple[bool, str, str]:
        """
        Crea un nuevo terapeuta
        Retorna: (success, message, codigo_terapeuta)
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos", ""
        
        try:
            with conn.cursor() as cursor:
                # Verificar si el código ya existe
                sql_check = """
                SELECT Codigo_trabajador 
                FROM terapeuta 
                WHERE Codigo_trabajador = %s
                """
                cursor.execute(sql_check, (terapeuta_data['Codigo_trabajador'],))
                if cursor.fetchone():
                    return False, "El código de trabajador ya existe", ""
                
                # Insertar nuevo terapeuta
                sql_insert = """
                INSERT INTO terapeuta (
                    Codigo_trabajador, nombre_completo, fisio_correo,
                    telefono, especializacion, franja_horaria_dias,
                    franja_horaria_horas, estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql_insert, (
                    terapeuta_data['Codigo_trabajador'],
                    terapeuta_data['nombre_completo'],
                    terapeuta_data['fisio_correo'],
                    terapeuta_data['telefono'],
                    terapeuta_data.get('especializacion', ''),
                    terapeuta_data.get('franja_horaria_dias', ''),
                    terapeuta_data.get('franja_horaria_horas', ''),
                    terapeuta_data.get('estado', 'Activo')
                ))
                
                conn.commit()
                return True, "Terapeuta creado exitosamente", terapeuta_data['Codigo_trabajador']
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al crear terapeuta: {e}")
            return False, str(e), ""
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def actualizar_terapeuta(codigo: str, terapeuta_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Actualiza un terapeuta existente
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar que el terapeuta existe
                sql_check = """
                SELECT Codigo_trabajador 
                FROM terapeuta 
                WHERE Codigo_trabajador = %s
                """
                cursor.execute(sql_check, (codigo,))
                if not cursor.fetchone():
                    return False, "Terapeuta no encontrado"
                
                # Actualizar terapeuta
                sql_update = """
                UPDATE terapeuta SET
                    nombre_completo = %s,
                    fisio_correo = %s,
                    telefono = %s,
                    especializacion = %s,
                    franja_horaria_dias = %s,
                    franja_horaria_horas = %s,
                    estado = %s
                WHERE Codigo_trabajador = %s
                """
                
                cursor.execute(sql_update, (
                    terapeuta_data['nombre_completo'],
                    terapeuta_data['fisio_correo'],
                    terapeuta_data['telefono'],
                    terapeuta_data.get('especializacion', ''),
                    terapeuta_data.get('franja_horaria_dias', ''),
                    terapeuta_data.get('franja_horaria_horas', ''),
                    terapeuta_data.get('estado', 'Activo'),
                    codigo
                ))
                
                conn.commit()
                return True, "Terapeuta actualizado exitosamente"
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al actualizar terapeuta: {e}")
            return False, str(e)
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def cambiar_estado_terapeuta(codigo: str, nuevo_estado: str) -> tuple[bool, str]:
        """
        Cambia el estado de un terapeuta
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar que el terapeuta existe
                sql_check = """
                SELECT Codigo_trabajador 
                FROM terapeuta 
                WHERE Codigo_trabajador = %s
                """
                cursor.execute(sql_check, (codigo,))
                if not cursor.fetchone():
                    return False, "Terapeuta no encontrado"
                
                # Actualizar estado
                sql_update = "UPDATE terapeuta SET estado = %s WHERE Codigo_trabajador = %s"
                cursor.execute(sql_update, (nuevo_estado, codigo))
                
                conn.commit()
                return True, f"Estado cambiado a '{nuevo_estado}' exitosamente"
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al cambiar estado del terapeuta: {e}")
            return False, str(e)
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_especializaciones() -> List[str]:
        """
        Obtiene lista de especializaciones únicas
        """
        conn = get_db_connection()
        if conn is None:
            return []
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT DISTINCT especializacion 
                FROM terapeuta 
                WHERE especializacion IS NOT NULL 
                AND TRIM(especializacion) != ''
                ORDER BY especializacion
                """
                
                cursor.execute(sql)
                especializaciones = cursor.fetchall()
                
                # Extraer solo los valores de especializacion
                return [esp['especializacion'] for esp in especializaciones]
                
        except Exception as e:
            print(f"❌ Error en obtener_especializaciones: {e}")
            return []
        finally:
            close_db_connection(conn)