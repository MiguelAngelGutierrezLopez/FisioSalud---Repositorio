import pymysql
from bd.conexion_bd import get_db_connection, close_db_connection
from typing import List, Dict, Any, Optional
from datetime import timedelta, datetime
import random

class CitaModel:
    
    # Rangos de códigos según tipo de usuario
    RANGOS_CODIGOS = {
        'usuario': ('FS-0001', 'FS-0500'),      # Usuario autogestionado
        'admin': ('FS-0501', 'FS-1000'),        # Administrador
        'fisio': ('FS-1001', 'FS-2000')         # Fisioterapeuta
    }
    
    # Cache para códigos disponibles
    _codigos_cache = {
        'usuario': None,
        'admin': None,
        'fisio': None
    }
    
    @staticmethod
    def obtener_siguiente_codigo_usuario() -> str:
        """
        Obtiene el siguiente código disponible en el pool de usuario (FS-0001 a FS-0500)
        """
        # Primero intentar con cache
        if CitaModel._codigos_cache['usuario']:
            codigo = CitaModel._codigos_cache['usuario']
            CitaModel._codigos_cache['usuario'] = None
            return codigo
        
        conn = get_db_connection()
        if conn is None:
            return ""
        
        try:
            with conn.cursor() as cursor:
                # Obtener todos los códigos de cita existentes en el rango de usuario
                inicio_rango, fin_rango = CitaModel.RANGOS_CODIGOS['usuario']
                
                # Extraer números de los rangos
                inicio_num = int(inicio_rango.split('-')[1])
                fin_num = int(fin_rango.split('-')[1])
                
                # Buscar todos los códigos existentes
                sql = """
                SELECT cita_id 
                FROM cita 
                WHERE cita_id LIKE 'FS-%'
                """
                cursor.execute(sql)
                todos_codigos = cursor.fetchall()
                
                # Convertir a conjunto de números usados
                numeros_usados = set()
                for codigo in todos_codigos:
                    try:
                        if codigo['cita_id'].startswith('FS-'):
                            num = int(codigo['cita_id'].split('-')[1])
                            if inicio_num <= num <= fin_num:
                                numeros_usados.add(num)
                    except (ValueError, IndexError):
                        continue
                
                # Encontrar el primer número disponible
                for num in range(inicio_num, fin_num + 1):
                    if num not in numeros_usados:
                        codigo_disponible = f"FS-{num:04d}"
                        print(f"Código disponible encontrado para usuario: {codigo_disponible}")
                        return codigo_disponible
                
                # Si no hay números disponibles en el rango de usuario
                print("ADVERTENCIA: No hay códigos disponibles en el rango de usuario (0001-0500)")
                
                # Intentar con rango extendido
                return CitaModel.buscar_codigo_en_rango_extendido('usuario')
                
        except Exception as e:
            print(f"Error al obtener siguiente código de usuario: {e}")
            return f"FS-{random.randint(1, 500):04d}"  # Fallback aleatorio
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def buscar_codigo_en_rango_extendido(tipo_usuario: str) -> str:
        """
        Busca un código disponible en rangos extendidos
        """
        try:
            # Para usuarios, probar rangos alternativos
            if tipo_usuario == 'usuario':
                rangos_extendidos = [
                    ('FS-5001', 'FS-6000'),
                    ('FS-6001', 'FS-7000'),
                    ('FS-7001', 'FS-8000')
                ]
            elif tipo_usuario == 'admin':
                rangos_extendidos = [
                    ('FS-2001', 'FS-3000'),
                    ('FS-3001', 'FS-4000')
                ]
            elif tipo_usuario == 'fisio':
                rangos_extendidos = [
                    ('FS-4001', 'FS-5000'),
                    ('FS-8001', 'FS-9000')
                ]
            else:
                rangos_extendidos = [('FS-9001', 'FS-9999')]
            
            conn = get_db_connection()
            if conn is None:
                return f"FS-{random.randint(5001, 9999):04d}"
            
            try:
                with conn.cursor() as cursor:
                    # Obtener todos los códigos existentes
                    sql = "SELECT cita_id FROM cita WHERE cita_id LIKE 'FS-%'"
                    cursor.execute(sql)
                    todos_codigos = cursor.fetchall()
                    
                    # Convertir a conjunto de números usados
                    numeros_usados = set()
                    for codigo in todos_codigos:
                        try:
                            if codigo['cita_id'].startswith('FS-'):
                                num = int(codigo['cita_id'].split('-')[1])
                                numeros_usados.add(num)
                        except (ValueError, IndexError):
                            continue
                    
                    # Buscar en cada rango extendido
                    for inicio_rango, fin_rango in rangos_extendidos:
                        inicio_num = int(inicio_rango.split('-')[1])
                        fin_num = int(fin_rango.split('-')[1])
                        
                        for num in range(inicio_num, fin_num + 1):
                            if num not in numeros_usados:
                                codigo_disponible = f"FS-{num:04d}"
                                print(f"Código encontrado en rango extendido: {codigo_disponible}")
                                return codigo_disponible
                    
                    # Si no hay en rangos extendidos, generar aleatorio fuera de rangos principales
                    return f"FS-{random.randint(9001, 9999):04d}"
                    
            finally:
                close_db_connection(conn)
                
        except Exception as e:
            print(f"Error al buscar en rango extendido: {e}")
            return f"FS-{random.randint(9001, 9999):04d}"
    
    @staticmethod
    def obtener_codigo_por_tipo(tipo_usuario: str) -> str:
        """
        Obtiene código según el tipo de usuario
        """
        if tipo_usuario not in CitaModel.RANGOS_CODIGOS:
            tipo_usuario = 'usuario'  # Default
        
        if tipo_usuario == 'usuario':
            return CitaModel.obtener_siguiente_codigo_usuario()
        else:
            # Para admin y fisio, buscar en su rango específico
            return CitaModel.buscar_codigo_en_rango_especifico(tipo_usuario)
    
    @staticmethod
    def buscar_codigo_en_rango_especifico(tipo_usuario: str) -> str:
        """
        Busca código en el rango específico para admin o fisio
        """
        if tipo_usuario not in CitaModel.RANGOS_CODIGOS:
            return CitaModel.obtener_siguiente_codigo_usuario()
        
        inicio_rango, fin_rango = CitaModel.RANGOS_CODIGOS[tipo_usuario]
        inicio_num = int(inicio_rango.split('-')[1])
        fin_num = int(fin_rango.split('-')[1])
        
        conn = get_db_connection()
        if conn is None:
            return f"FS-{random.randint(inicio_num, fin_num):04d}"
        
        try:
            with conn.cursor() as cursor:
                # Buscar todos los códigos existentes en este rango
                sql = """
                SELECT cita_id 
                FROM cita 
                WHERE cita_id LIKE 'FS-%'
                """
                cursor.execute(sql)
                todos_codigos = cursor.fetchall()
                
                # Convertir a conjunto de números usados en este rango
                numeros_usados = set()
                for codigo in todos_codigos:
                    try:
                        if codigo['cita_id'].startswith('FS-'):
                            num = int(codigo['cita_id'].split('-')[1])
                            if inicio_num <= num <= fin_num:
                                numeros_usados.add(num)
                    except (ValueError, IndexError):
                        continue
                
                # Encontrar el primer número disponible
                for num in range(inicio_num, fin_num + 1):
                    if num not in numeros_usados:
                        codigo_disponible = f"FS-{num:04d}"
                        print(f"Código encontrado para {tipo_usuario}: {codigo_disponible}")
                        return codigo_disponible
                
                # Si no hay en este rango, buscar en rango extendido
                return CitaModel.buscar_codigo_en_rango_extendido(tipo_usuario)
                
        except Exception as e:
            print(f"Error al buscar código para {tipo_usuario}: {e}")
            return f"FS-{random.randint(inicio_num, fin_num):04d}"
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def generar_codigo_cita(tipo_usuario: str = 'usuario') -> str:
        """
        Genera un código único para la cita según el tipo de usuario
        """
        return CitaModel.obtener_codigo_por_tipo(tipo_usuario)
    
    @staticmethod
    def obtener_servicios_terapia() -> List[Dict[str, Any]]:
        """Obtiene todos los servicios de terapia disponibles incluyendo recomendaciones"""
        conn = get_db_connection()
        if conn is None:
            return []
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT codigo, nombre, descripcion, terapeuta_disponible, 
                    inicio_jornada, final_jornada, duracion, modalidad, 
                    precio, beneficios, recomendacion_precita,
                    condiciones_tratar, requisitos, consideraciones
                FROM servicio_terapia 
                WHERE codigo IS NOT NULL
                """
                cursor.execute(sql)
                servicios = cursor.fetchall()
                
                # Convertir a diccionarios y formatear datos
                servicios_formateados = []
                for servicio in servicios:
                    servicio_dict = dict(servicio)
                    
                    # CORRECCIÓN: Manejar duración (puede ser int, timedelta, o None)
                    duracion = servicio_dict.get('duracion')
                    if isinstance(duracion, timedelta):
                        # Convertir timedelta a minutos enteros
                        total_minutes = int(duracion.total_seconds() / 60)
                    elif isinstance(duracion, (int, float)):
                        total_minutes = int(duracion)
                    else:
                        total_minutes = 0
                    
                    # Formatear duración como string
                    horas = total_minutes // 60
                    minutos = total_minutes % 60
                    if horas > 0:
                        servicio_dict['duracion'] = f"{horas}h {minutos}min"
                    elif minutos > 0:
                        servicio_dict['duracion'] = f"{minutos} min"
                    else:
                        servicio_dict['duracion'] = "No especificada"
                    
                    # CORRECCIÓN: Convertir time objects a strings
                    for time_field in ['inicio_jornada', 'final_jornada']:
                        time_val = servicio_dict.get(time_field)
                        if time_val:
                            if hasattr(time_val, 'strftime'):
                                servicio_dict[time_field] = time_val.strftime('%H:%M')
                            elif isinstance(time_val, str):
                                # Ya es string, mantenerlo
                                pass
                            else:
                                servicio_dict[time_field] = str(time_val)
                    
                    # Asegurar que el precio sea float
                    if servicio_dict.get('precio') is not None:
                        try:
                            servicio_dict['precio'] = float(servicio_dict['precio'])
                        except (ValueError, TypeError):
                            servicio_dict['precio'] = 0.0
                    else:
                        servicio_dict['precio'] = 0.0
                    
                    # Procesar recomendaciones precita (puede ser None)
                    recomendaciones = servicio_dict.get('recomendacion_precita')
                    if recomendaciones:
                        if isinstance(recomendaciones, str):
                            # Limpiar y formatear
                            recomendaciones = recomendaciones.strip()
                            # Separar por puntos si es un texto largo
                            if len(recomendaciones) > 100 and '.' in recomendaciones:
                                recomendaciones = recomendaciones.replace('. ', '.<br>• ')
                                recomendaciones = '• ' + recomendaciones
                            servicio_dict['recomendacion_precita'] = recomendaciones
                    else:
                        servicio_dict['recomendacion_precita'] = ""
                    
                    # Asegurar que todos los campos de texto sean strings
                    campos_texto = ['descripcion', 'beneficios', 'condiciones_tratar', 
                                'requisitos', 'consideraciones', 'terapeuta_disponible']
                    for campo in campos_texto:
                        if servicio_dict.get(campo) is None:
                            servicio_dict[campo] = ""
                    
                    servicios_formateados.append(servicio_dict)
                
                return servicios_formateados
                
        except Exception as e:
            print(f"Error al obtener servicios de terapia: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            close_db_connection(conn)

    @staticmethod
    def crear_cita(datos_cita: Dict[str, Any], tipo_usuario: str = 'usuario') -> str:
        """
        Crea una nueva cita y retorna el código de la cita creada
        tipo_usuario: 'usuario', 'admin', o 'fisio'
        """
        conn = get_db_connection()
        if conn is None:
            return ""
        
        try:
            with conn.cursor() as cursor:
                # Generar código único para la cita según tipo de usuario
                codigo_cita = CitaModel.generar_codigo_cita(tipo_usuario)
                
                if not codigo_cita:
                    raise Exception("No se pudo generar el código de cita")
                
                # Validar que el código no exista ya (doble verificación)
                cursor.execute("SELECT cita_id FROM cita WHERE cita_id = %s", (codigo_cita,))
                if cursor.fetchone():
                    print(f"ADVERTENCIA: El código {codigo_cita} ya existe. Generando alternativo...")
                    # Generar código alternativo
                    codigo_cita = f"FS-{random.randint(9001, 9999):04d}"
                
                # Estado por defecto para citas de usuario
                estado_cita = 'pendiente' if tipo_usuario == 'usuario' else 'confirmada'
                
                sql = """
                INSERT INTO cita (cita_id, servicio, terapeuta_designado, nombre_paciente, 
                                telefono, correo, fecha_cita, hora_cita, 
                                notas_adicionales, tipo_pago, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql, (
                    codigo_cita,
                    datos_cita['servicio'],
                    datos_cita['terapeuta_designado'],
                    datos_cita['nombre_paciente'],
                    datos_cita['telefono'],
                    datos_cita['correo'],
                    datos_cita['fecha_cita'],
                    datos_cita['hora_cita'],
                    datos_cita.get('notas_adicionales', ''),
                    datos_cita['tipo_pago'],
                    estado_cita
                ))
                
                conn.commit()
                
                # Verificar que se insertó correctamente
                cursor.execute("SELECT cita_id FROM cita WHERE cita_id = %s", (codigo_cita,))
                cita_verificada = cursor.fetchone()
                
                if cita_verificada:
                    print(f"Cita creada exitosamente por {tipo_usuario}: {codigo_cita}")
                    return codigo_cita
                else:
                    raise Exception("No se pudo verificar la creación de la cita")
                    
        except Exception as e:
            print(f"Error al crear cita: {e}")
            if conn:
                conn.rollback()
            return ""
        finally:
            close_db_connection(conn)

    @staticmethod
    def crear_acudiente(codigo_cita: str, datos_acudiente: Dict[str, Any]) -> bool:
        """Crea un nuevo registro de acudiente vinculado a una cita"""
        conn = get_db_connection()
        if conn is None:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Verificar que la cita existe
                cursor.execute("SELECT cita_id FROM cita WHERE cita_id = %s", (codigo_cita,))
                if not cursor.fetchone():
                    print(f"Error: No existe la cita {codigo_cita} para vincular acudiente")
                    return False
                
                sql = """
                INSERT INTO acudiente (cita_id, nombre_completo, identificacion, telefono, correo)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    codigo_cita,
                    datos_acudiente['nombre_completo'],
                    datos_acudiente['identificacion'],
                    datos_acudiente.get('telefono', ''),
                    datos_acudiente.get('correo', '')
                ))
                conn.commit()
                print(f"Acudiente creado exitosamente para cita: {codigo_cita}")
                return True
                
        except Exception as e:
            print(f"Error al crear acudiente: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            close_db_connection(conn)

    @staticmethod
    def verificar_disponibilidad_cita(fecha: str, hora: str, terapeuta: str) -> bool:
        """Verifica si la hora y fecha están disponibles para el terapeuta"""
        conn = get_db_connection()
        if conn is None:
            return False
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT COUNT(*) as count 
                FROM cita 
                WHERE fecha_cita = %s AND hora_cita = %s AND terapeuta_designado = %s
                """
                cursor.execute(sql, (fecha, hora, terapeuta))
                resultado = cursor.fetchone()
                disponible = resultado['count'] == 0
                print(f"Disponibilidad para {terapeuta} el {fecha} a las {hora}: {'Sí' if disponible else 'No'}")
                return disponible
                
        except Exception as e:
            print(f"Error al verificar disponibilidad: {e}")
            return False
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def verificar_estado_pool_usuario() -> Dict[str, Any]:
        """
        Verifica el estado del pool de códigos para usuarios
        """
        conn = get_db_connection()
        if conn is None:
            return {"error": "No hay conexión"}
        
        try:
            with conn.cursor() as cursor:
                inicio_rango, fin_rango = CitaModel.RANGOS_CODIGOS['usuario']
                inicio_num = int(inicio_rango.split('-')[1])
                fin_num = int(fin_rango.split('-')[1])
                total_codigos = fin_num - inicio_num + 1
                
                # Obtener todos los códigos
                sql = "SELECT cita_id FROM cita WHERE cita_id LIKE 'FS-%'"
                cursor.execute(sql)
                todos_codigos = cursor.fetchall()
                
                # Contar códigos usados en el rango de usuario
                codigos_usados = 0
                numeros_usados = []
                
                for codigo in todos_codigos:
                    try:
                        if codigo['cita_id'].startswith('FS-'):
                            num = int(codigo['cita_id'].split('-')[1])
                            if inicio_num <= num <= fin_num:
                                codigos_usados += 1
                                numeros_usados.append(num)
                    except (ValueError, IndexError):
                        continue
                
                # Buscar el siguiente disponible
                siguiente_disponible = None
                for num in range(inicio_num, fin_num + 1):
                    if num not in numeros_usados:
                        siguiente_disponible = f"FS-{num:04d}"
                        break
                
                # Verificar si hay códigos disponibles
                if siguiente_disponible:
                    # Precachear el siguiente código
                    CitaModel._codigos_cache['usuario'] = siguiente_disponible
                    # Buscar el siguiente después de ese
                    for num in range(int(siguiente_disponible.split('-')[1]) + 1, fin_num + 1):
                        if num not in numeros_usados:
                            # Guardar como siguiente en caché
                            pass
                
                porcentaje_uso = (codigos_usados / total_codigos * 100) if total_codigos > 0 else 0
                
                return {
                    "rango": f"{inicio_rango} - {fin_rango}",
                    "total_codigos": total_codigos,
                    "codigos_usados": codigos_usados,
                    "codigos_disponibles": total_codigos - codigos_usados,
                    "siguiente_disponible": siguiente_disponible,
                    "porcentaje_uso": round(porcentaje_uso, 2),
                    "alerta": "BAJO" if codigos_usados < 400 else "MEDIO" if codigos_usados < 450 else "ALTO"
                }
                
        except Exception as e:
            print(f"Error al verificar estado del pool: {e}")
            return {"error": str(e)}
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def inicializar_cache_codigos():
        """Inicializa la caché con algunos códigos disponibles"""
        try:
            estado = CitaModel.verificar_estado_pool_usuario()
            if estado.get('siguiente_disponible'):
                CitaModel._codigos_cache['usuario'] = estado['siguiente_disponible']
                print(f"Caché inicializada con código: {estado['siguiente_disponible']}")
        except Exception as e:
            print(f"Error al inicializar caché: {e}")

    
    

    