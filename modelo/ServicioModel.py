from bd.conexion_bd import get_db_connection, close_db_connection
from datetime import timedelta, time
import json

class ServicioModel:
    @staticmethod
    def obtener_servicio_por_codigo(codigo):
        """
        Obtiene un servicio por su código desde la base de datos con información de terapeutas
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                # Obtener el servicio principal
                query = "SELECT * FROM servicio_terapia WHERE codigo = %s"
                cursor.execute(query, (codigo,))
                servicio = cursor.fetchone()

                if not servicio:
                    return None, "Servicio no encontrado"
                
                servicio_dict = dict(servicio)
                
                # Convertir timedelta a string para los horarios
                if isinstance(servicio_dict.get('inicio_jornada'), timedelta):
                    servicio_dict['inicio_jornada_str'] = str(servicio_dict['inicio_jornada'])[:5]
                elif servicio_dict.get('inicio_jornada'):
                    servicio_dict['inicio_jornada_str'] = str(servicio_dict['inicio_jornada'])[:5]
                
                if isinstance(servicio_dict.get('final_jornada'), timedelta):
                    servicio_dict['final_jornada_str'] = str(servicio_dict['final_jornada'])[:5]
                elif servicio_dict.get('final_jornada'):
                    servicio_dict['final_jornada_str'] = str(servicio_dict['final_jornada'])[:5]
                
                # Obtener información de los terapeutas si existen
                if servicio_dict.get('terapeuta_disponible'):
                    terapeutas_nombres = servicio_dict['terapeuta_disponible'].split('|')
                    terapeutas_info = []
                    
                    for nombre_terapeuta in terapeutas_nombres:
                        nombre_limpio = nombre_terapeuta.strip()
                        
                        # Buscar el terapeuta por nombre
                        query_terapeuta = """
                        SELECT 
                            nombre_completo,
                            especializacion,
                            franja_horaria_dias,
                            franja_horaria_horas,
                            telefono,
                            fisio_correo
                        FROM terapeuta 
                        WHERE nombre_completo LIKE %s 
                        AND estado = 'Activo'
                        """
                        cursor.execute(query_terapeuta, (f"%{nombre_limpio}%",))
                        terapeuta_data = cursor.fetchone()
                        
                        if terapeuta_data:
                            terapeuta_dict = dict(terapeuta_data)
                            terapeuta_dict['horario_completo'] = f"{terapeuta_dict['franja_horaria_dias']} {terapeuta_dict['franja_horaria_horas']}"
                            terapeutas_info.append(terapeuta_dict)
                    
                    servicio_dict['terapeutas'] = terapeutas_info
                    
                    # Crear un texto de horarios combinados
                    if terapeutas_info:
                        horarios_unicos = set()
                        for terapeuta in terapeutas_info:
                            horarios_unicos.add(terapeuta['horario_completo'])
                        
                        servicio_dict['horarios_disponibles'] = list(horarios_unicos)
                
                return servicio_dict, None

        except Exception as e:
            print(f"Error en modelo obtener_servicio_por_codigo: {e}")
            return None, "Error interno al obtener el servicio"
        finally:
            close_db_connection(conn)

    @staticmethod
    def obtener_todos_servicios():
        """
        Obtiene todos los servicios terapéuticos con información básica de terapeutas
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM servicio_terapia"
                cursor.execute(query)
                servicios = cursor.fetchall()
                
                servicios_list = []
                for servicio in servicios:
                    servicio_dict = dict(servicio)
                    
                    # Convertir timedelta a string para los horarios
                    if isinstance(servicio_dict.get('inicio_jornada'), timedelta):
                        servicio_dict['inicio_jornada_str'] = str(servicio_dict['inicio_jornada'])[:5]
                    elif servicio_dict.get('inicio_jornada'):
                        servicio_dict['inicio_jornada_str'] = str(servicio_dict['inicio_jornada'])[:5]
                    
                    if isinstance(servicio_dict.get('final_jornada'), timedelta):
                        servicio_dict['final_jornada_str'] = str(servicio_dict['final_jornada'])[:5]
                    elif servicio_dict.get('final_jornada'):
                        servicio_dict['final_jornada_str'] = str(servicio_dict['final_jornada'])[:5]
                    
                    # Contar terapeutas disponibles
                    if servicio_dict.get('terapeuta_disponible'):
                        terapeutas_count = len(servicio_dict['terapeuta_disponible'].split('|'))
                        servicio_dict['terapeutas_count'] = terapeutas_count
                    
                    servicios_list.append(servicio_dict)
                
                return servicios_list, None

        except Exception as e:
            print(f"Error en modelo obtener_todos_servicios: {e}")
            return None, "Error interno al obtener servicios"
        finally:
            close_db_connection(conn)

    @staticmethod
    def obtener_servicios_por_categoria(categoria):
        """
        Obtiene servicios filtrados por categoría
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM servicio_terapia WHERE categoria = %s"
                cursor.execute(query, (categoria,))
                servicios = cursor.fetchall()
                
                servicios_list = []
                for servicio in servicios:
                    servicio_dict = dict(servicio)
                    
                    # Convertir timedelta a string para los horarios
                    if isinstance(servicio_dict.get('inicio_jornada'), timedelta):
                        servicio_dict['inicio_jornada_str'] = str(servicio_dict['inicio_jornada'])[:5]
                    elif servicio_dict.get('inicio_jornada'):
                        servicio_dict['inicio_jornada_str'] = str(servicio_dict['inicio_jornada'])[:5]
                    
                    if isinstance(servicio_dict.get('final_jornada'), timedelta):
                        servicio_dict['final_jornada_str'] = str(servicio_dict['final_jornada'])[:5]
                    elif servicio_dict.get('final_jornada'):
                        servicio_dict['final_jornada_str'] = str(servicio_dict['final_jornada'])[:5]
                    
                    servicios_list.append(servicio_dict)
                
                return servicios_list, None

        except Exception as e:
            print(f"Error en modelo obtener_servicios_por_categoria: {e}")
            return None, "Error interno al filtrar servicios"
        finally:
            close_db_connection(conn)

    @staticmethod
    def obtener_servicios_por_terapeuta(terapeuta_busqueda):
        """
        Obtiene servicios filtrados por terapeuta (nombre o correo)
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                # Buscar servicios que contengan el terapeuta en el campo terapeuta_disponible
                query = """
                SELECT DISTINCT st.* 
                FROM servicio_terapia st
                WHERE st.terapeuta_disponible LIKE %s 
                OR EXISTS (
                    SELECT 1 
                    FROM terapeuta t 
                    WHERE (t.nombre_completo LIKE %s OR t.fisio_correo LIKE %s)
                    AND st.terapeuta_disponible LIKE CONCAT('%%', t.nombre_completo, '%%')
                )
                ORDER BY st.nombre
                """
                
                busqueda_pattern = f"%{terapeuta_busqueda}%"
                cursor.execute(query, (busqueda_pattern, busqueda_pattern, busqueda_pattern))
                servicios = cursor.fetchall()
                
                servicios_list = []
                for servicio in servicios:
                    servicio_dict = dict(servicio)
                    
                    # Convertir timedelta a string para los horarios
                    if isinstance(servicio_dict.get('inicio_jornada'), timedelta):
                        servicio_dict['inicio_jornada_str'] = str(servicio_dict['inicio_jornada'])[:5]
                    elif servicio_dict.get('inicio_jornada'):
                        servicio_dict['inicio_jornada_str'] = str(servicio_dict['inicio_jornada'])[:5]
                    
                    if isinstance(servicio_dict.get('final_jornada'), timedelta):
                        servicio_dict['final_jornada_str'] = str(servicio_dict['final_jornada'])[:5]
                    elif servicio_dict.get('final_jornada'):
                        servicio_dict['final_jornada_str'] = str(servicio_dict['final_jornada'])[:5]
                    
                    # Obtener información específica del terapeuta buscado
                    if servicio_dict.get('terapeuta_disponible'):
                        terapeutas_nombres = servicio_dict['terapeuta_disponible'].split('|')
                        terapeutas_info = []
                        
                        for nombre_terapeuta in terapeutas_nombres:
                            nombre_limpio = nombre_terapeuta.strip()
                            
                            # Verificar si este terapeuta coincide con la búsqueda
                            if (terapeuta_busqueda.lower() in nombre_limpio.lower() or 
                                terapeuta_busqueda.lower() in servicio_dict.get('terapeuta_disponible', '').lower()):
                                
                                # Buscar info del terapeuta
                                query_terapeuta = """
                                SELECT 
                                    nombre_completo,
                                    especializacion,
                                    franja_horaria_dias,
                                    franja_horaria_horas,
                                    telefono,
                                    fisio_correo,
                                    Codigo_trabajador
                                FROM terapeuta 
                                WHERE nombre_completo LIKE %s 
                                AND estado = 'Activo'
                                """
                                cursor.execute(query_terapeuta, (f"%{nombre_limpio}%",))
                                terapeuta_data = cursor.fetchone()
                                
                                if terapeuta_data:
                                    terapeuta_dict = dict(terapeuta_data)
                                    terapeuta_dict['horario_completo'] = f"{terapeuta_dict['franja_horaria_dias']} {terapeuta_dict['franja_horaria_horas']}"
                                    terapeutas_info.append(terapeuta_dict)
                        
                        if terapeutas_info:
                            servicio_dict['terapeutas_filtrados'] = terapeutas_info
                            servicio_dict['terapeuta_coincidencia'] = True
                    
                    servicios_list.append(servicio_dict)
                
                return servicios_list, None

        except Exception as e:
            print(f"Error en modelo obtener_servicios_por_terapeuta: {e}")
            return None, "Error interno al filtrar servicios por terapeuta"
        finally:
            close_db_connection(conn)

    @staticmethod
    def obtener_lista_terapeutas():
        """
        Obtiene lista de todos los terapeutas activos para el filtro
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = """
                SELECT DISTINCT 
                    nombre_completo,
                    fisio_correo,
                    especializacion,
                    Codigo_trabajador
                FROM terapeuta 
                WHERE estado = 'Activo'
                ORDER BY nombre_completo
                """
                cursor.execute(query)
                terapeutas = cursor.fetchall()
                
                return [dict(t) for t in terapeutas], None

        except Exception as e:
            print(f"Error en modelo obtener_lista_terapeutas: {e}")
            return None, "Error interno al obtener terapeutas"
        finally:
            close_db_connection(conn)