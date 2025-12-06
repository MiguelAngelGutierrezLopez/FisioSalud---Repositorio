from datetime import datetime
from time import time
import pymysql
from bd.conexion_bd import get_db_connection, close_db_connection
from typing import Dict, Any, Optional, List
from decimal import Decimal

class AdminServicioModel:
    
    # ===== ESTADÍSTICAS GENERALES =====
    
    @staticmethod
    def obtener_estadisticas_generales() -> Dict[str, Any]:
        """
        Obtiene estadísticas de todos los tipos de servicios
        """
        conn = get_db_connection()
        if conn is None:
            return {
                'total_servicios': 0,
                'terapias': 0,
                'nutricion': 0,
                'implementos': 0,
                'precio_promedio_terapias': 0.0,
                'total_porciones_nutricion': 0,
                'peso_total_implementos': 0.0
            }
        
        try:
            with conn.cursor() as cursor:
                # 1. Estadísticas de terapias
                sql_terapias = """
                SELECT 
                    COUNT(*) as total,
                    AVG(precio) as precio_promedio
                FROM servicio_terapia
                """
                cursor.execute(sql_terapias)
                stats_terapias = cursor.fetchone()
                
                # 2. Estadísticas de nutrición
                sql_nutricion = """
                SELECT 
                    COUNT(*) as total,
                    SUM(porciones) as total_porciones,
                    AVG(precio) as precio_promedio
                FROM servicio_nutricion
                """
                cursor.execute(sql_nutricion)
                stats_nutricion = cursor.fetchone()
                
                # 3. Estadísticas de implementos
                sql_implementos = """
                SELECT 
                    COUNT(*) as total,
                    SUM(peso) as peso_total,
                    AVG(precio) as precio_promedio
                FROM servicio_implementos
                """
                cursor.execute(sql_implementos)
                stats_implementos = cursor.fetchone()
                
                # Calcular total general
                total_general = (
                    (stats_terapias['total'] or 0) + 
                    (stats_nutricion['total'] or 0) + 
                    (stats_implementos['total'] or 0)
                )
                
                return {
                    'total_servicios': int(total_general),
                    'terapias': int(stats_terapias['total'] or 0),
                    'nutricion': int(stats_nutricion['total'] or 0),
                    'implementos': int(stats_implementos['total'] or 0),
                    'precio_promedio_terapias': float(stats_terapias['precio_promedio'] or 0),
                    'total_porciones_nutricion': int(stats_nutricion['total_porciones'] or 0),
                    'peso_total_implementos': float(stats_implementos['peso_total'] or 0),
                    'precio_promedio_nutricion': float(stats_nutricion['precio_promedio'] or 0),
                    'precio_promedio_implementos': float(stats_implementos['precio_promedio'] or 0)
                }
                
        except Exception as e:
            return {
                'total_servicios': 0,
                'terapias': 0,
                'nutricion': 0,
                'implementos': 0,
                'precio_promedio_terapias': 0.0,
                'total_porciones_nutricion': 0,
                'peso_total_implementos': 0.0
            }
        finally:
            close_db_connection(conn)
    
    # ===== FUNCIONES PARA TERAPIAS =====
    
    @staticmethod
    def listar_terapias(filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Lista servicios de terapia con filtros opcionales
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
                    codigo, 
                    nombre, 
                    descripcion, 
                    terapeuta_disponible,
                    TIME_FORMAT(inicio_jornada, '%%H:%%i') as inicio_jornada,
                    TIME_FORMAT(final_jornada, '%%H:%%i') as final_jornada,
                    duracion, 
                    intensidad, 
                    equipamento, 
                    modalidad,
                    condiciones_tratar, 
                    requisitos, 
                    beneficios, 
                    precio,
                    consideraciones, 
                    promedio_sesiones, 
                    recomendacion_precita
                FROM servicio_terapia
                WHERE 1=1
                """
                
                params = []
                
                if filtros.get('nombre'):
                    sql += " AND nombre LIKE %s"
                    params.append(f"%{filtros['nombre']}%")
                
                if filtros.get('modalidad'):
                    sql += " AND modalidad LIKE %s"
                    params.append(f"%{filtros['modalidad']}%")
                
                if filtros.get('duracion_min') is not None:
                    sql += " AND duracion >= %s"
                    params.append(filtros['duracion_min'])
                
                if filtros.get('duracion_max') is not None:
                    sql += " AND duracion <= %s"
                    params.append(filtros['duracion_max'])
                
                sql += " ORDER BY nombre ASC"
                
                cursor.execute(sql, params)
                terapias = cursor.fetchall()
                
                # Convertir Decimal a float
                for terapia in terapias:
                    for key, value in terapia.items():
                        if isinstance(value, Decimal):
                            terapia[key] = float(value)
                        elif isinstance(value, time):  # CORREGIDO: usar 'time' directamente
                            terapia[key] = str(value)
                
                return terapias
                
        except Exception as e:
            return []
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_terapia_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una terapia por su código
        """
        conn = get_db_connection()
        if conn is None:
            return None
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    codigo, nombre, descripcion, terapeuta_disponible,
                    TIME_FORMAT(inicio_jornada, '%H:%i') as inicio_jornada,
                    TIME_FORMAT(final_jornada, '%H:%i') as final_jornada,
                    duracion, intensidad, equipamento, modalidad,
                    condiciones_tratar, requisitos, beneficios, precio,
                    consideraciones, promedio_sesiones, recomendacion_precita
                FROM servicio_terapia
                WHERE codigo = %s
                """
                
                cursor.execute(sql, (codigo,))
                terapia = cursor.fetchone()
                
                if terapia:
                    terapia_dict = dict(terapia)
                    # Convertir Decimal a float
                    for key, value in terapia_dict.items():
                        if isinstance(value, Decimal):
                            terapia_dict[key] = float(value)
                    return terapia_dict
                
                return None
                
        except Exception as e:
            return None
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def crear_terapia(terapia_data: Dict[str, Any]) -> tuple[bool, str, str]:
        """
        Crea un nuevo servicio de terapia
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos", ""
        
        try:
            with conn.cursor() as cursor:
                # Verificar si el código ya existe
                sql_check = "SELECT codigo FROM servicio_terapia WHERE codigo = %s"
                cursor.execute(sql_check, (terapia_data['codigo'],))
                if cursor.fetchone():
                    return False, "El código de terapia ya existe", ""
                
                # Insertar nueva terapia
                sql_insert = """
                INSERT INTO servicio_terapia (
                    codigo, nombre, descripcion, terapeuta_disponible,
                    inicio_jornada, final_jornada, duracion, intensidad,
                    equipamento, modalidad, condiciones_tratar, requisitos,
                    beneficios, precio, consideraciones, promedio_sesiones,
                    recomendacion_precita
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql_insert, (
                    terapia_data['codigo'],
                    terapia_data['nombre'],
                    terapia_data.get('descripcion', ''),
                    terapia_data.get('terapeuta_disponible', ''),
                    terapia_data.get('inicio_jornada'),
                    terapia_data.get('final_jornada'),
                    terapia_data.get('duracion'),
                    terapia_data.get('intensidad', ''),
                    terapia_data.get('equipamento', ''),
                    terapia_data.get('modalidad', ''),
                    terapia_data.get('condiciones_tratar', ''),
                    terapia_data.get('requisitos', ''),
                    terapia_data.get('beneficios', ''),
                    terapia_data.get('precio', 0.0),
                    terapia_data.get('consideraciones', ''),
                    terapia_data.get('promedio_sesiones'),
                    terapia_data.get('recomendacion_precita', '')
                ))
                
                conn.commit()
                return True, "Terapia creada exitosamente", terapia_data['codigo']
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al crear terapia: {e}")
            return False, str(e), ""
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def actualizar_terapia(codigo: str, terapia_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Actualiza un servicio de terapia existente
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar que la terapia existe
                sql_check = "SELECT codigo FROM servicio_terapia WHERE codigo = %s"
                cursor.execute(sql_check, (codigo,))
                if not cursor.fetchone():
                    return False, "Terapia no encontrada"
                
                # Actualizar terapia
                sql_update = """
                UPDATE servicio_terapia SET
                    nombre = %s,
                    descripcion = %s,
                    terapeuta_disponible = %s,
                    inicio_jornada = %s,
                    final_jornada = %s,
                    duracion = %s,
                    intensidad = %s,
                    equipamento = %s,
                    modalidad = %s,
                    condiciones_tratar = %s,
                    requisitos = %s,
                    beneficios = %s,
                    precio = %s,
                    consideraciones = %s,
                    promedio_sesiones = %s,
                    recomendacion_precita = %s
                WHERE codigo = %s
                """
                
                cursor.execute(sql_update, (
                    terapia_data['nombre'],
                    terapia_data.get('descripcion', ''),
                    terapia_data.get('terapeuta_disponible', ''),
                    terapia_data.get('inicio_jornada'),
                    terapia_data.get('final_jornada'),
                    terapia_data.get('duracion'),
                    terapia_data.get('intensidad', ''),
                    terapia_data.get('equipamento', ''),
                    terapia_data.get('modalidad', ''),
                    terapia_data.get('condiciones_tratar', ''),
                    terapia_data.get('requisitos', ''),
                    terapia_data.get('beneficios', ''),
                    terapia_data.get('precio', 0.0),
                    terapia_data.get('consideraciones', ''),
                    terapia_data.get('promedio_sesiones'),
                    terapia_data.get('recomendacion_precita', ''),
                    codigo
                ))
                
                conn.commit()
                return True, "Terapia actualizada exitosamente"
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al actualizar terapia: {e}")
            return False, str(e)
        finally:
            close_db_connection(conn)
    
    # ===== FUNCIONES PARA NUTRICIÓN =====
    
    @staticmethod
    def listar_nutricion(filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Lista productos de nutrición con filtros opcionales
        """
        if filtros is None:
            filtros = {}
        
        conn = get_db_connection()
        if conn is None:
            return []
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    codigo, nombre, descripcion, `tiempo/resultado`,
                    `proteina/porcion`, valor_energetico, proteinas,
                    carbohidratos, grasas, beneficios, dosis_recomendada,
                    preparacion, momento_ideal_post_tratamiento,
                    contraindicaciones, forma_almacenar, sabores, precio,
                    porciones
                FROM servicio_nutricion
                WHERE 1=1
                """
                
                params = []
                
                if filtros.get('nombre'):
                    sql += " AND nombre LIKE %s"
                    params.append(f"%{filtros['nombre']}%")
                
                if filtros.get('sabor'):
                    sql += " AND sabores LIKE %s"
                    params.append(f"%{filtros['sabor']}%")
                
                if filtros.get('porciones_min') is not None:
                    sql += " AND porciones >= %s"
                    params.append(filtros['porciones_min'])
                
                if filtros.get('porciones_max') is not None:
                    sql += " AND porciones <= %s"
                    params.append(filtros['porciones_max'])
                
                sql += " ORDER BY nombre ASC"
                
                cursor.execute(sql, params)
                productos = cursor.fetchall()
                
                # Procesar datos para JSON
                resultado = []
                for producto in productos:
                    producto_dict = dict(producto)
                    # Convertir Decimal a float
                    for key, value in producto_dict.items():
                        if isinstance(value, Decimal):
                            producto_dict[key] = float(value)
                    resultado.append(producto_dict)
                
                return resultado
                
        except Exception as e:
            print(f"❌ Error en listar_nutricion: {e}")
            return []
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_nutricion_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un producto de nutrición por su código
        """
        conn = get_db_connection()
        if conn is None:
            return None
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    codigo, nombre, descripcion, `tiempo/resultado`,
                    `proteina/porcion`, valor_energetico, proteinas,
                    carbohidratos, grasas, beneficios, dosis_recomendada,
                    preparacion, momento_ideal_post_tratamiento,
                    contraindicaciones, forma_almacenar, sabores, precio,
                    porciones
                FROM servicio_nutricion
                WHERE codigo = %s
                """
                
                cursor.execute(sql, (codigo,))
                producto = cursor.fetchone()
                
                if producto:
                    producto_dict = dict(producto)
                    # Convertir Decimal a float
                    for key, value in producto_dict.items():
                        if isinstance(value, Decimal):
                            producto_dict[key] = float(value)
                    return producto_dict
                
                return None
                
        except Exception as e:
            print(f"❌ Error en obtener_nutricion_por_codigo: {e}")
            return None
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def crear_nutricion(nutricion_data: Dict[str, Any]) -> tuple[bool, str, str]:
        """
        Crea un nuevo producto de nutrición
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos", ""
        
        try:
            with conn.cursor() as cursor:
                # Verificar si el código ya existe
                sql_check = "SELECT codigo FROM servicio_nutricion WHERE codigo = %s"
                cursor.execute(sql_check, (nutricion_data['codigo'],))
                if cursor.fetchone():
                    return False, "El código de nutrición ya existe", ""
                
                # Insertar nuevo producto
                sql_insert = """
                INSERT INTO servicio_nutricion (
                    codigo, nombre, descripcion, `tiempo/resultado`,
                    `proteina/porcion`, valor_energetico, proteinas,
                    carbohidratos, grasas, beneficios, dosis_recomendada,
                    preparacion, momento_ideal_post_tratamiento,
                    contraindicaciones, forma_almacenar, sabores, precio,
                    porciones
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql_insert, (
                    nutricion_data['codigo'],
                    nutricion_data['nombre'],
                    nutricion_data.get('descripcion', ''),
                    nutricion_data.get('tiempo_resultado', ''),
                    nutricion_data.get('proteina_porcion', 0.0),
                    nutricion_data.get('valor_energetico', 0.0),
                    nutricion_data.get('proteinas', 0.0),
                    nutricion_data.get('carbohidratos', 0.0),
                    nutricion_data.get('grasas', 0.0),
                    nutricion_data.get('beneficios', ''),
                    nutricion_data.get('dosis_recomendada', ''),
                    nutricion_data.get('preparacion', ''),
                    nutricion_data.get('momento_ideal_post_tratamiento', ''),
                    nutricion_data.get('contraindicaciones', ''),
                    nutricion_data.get('forma_almacenar', ''),
                    nutricion_data.get('sabores', ''),
                    nutricion_data.get('precio', 0.0),
                    nutricion_data.get('porciones', 1)
                ))
                
                conn.commit()
                return True, "Producto de nutrición creado exitosamente", nutricion_data['codigo']
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al crear producto de nutrición: {e}")
            return False, str(e), ""
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def actualizar_nutricion(codigo: str, nutricion_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Actualiza un producto de nutrición existente
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar que el producto existe
                sql_check = "SELECT codigo FROM servicio_nutricion WHERE codigo = %s"
                cursor.execute(sql_check, (codigo,))
                if not cursor.fetchone():
                    return False, "Producto de nutrición no encontrado"
                
                # Actualizar producto
                sql_update = """
                UPDATE servicio_nutricion SET
                    nombre = %s,
                    descripcion = %s,
                    `tiempo/resultado` = %s,
                    `proteina/porcion` = %s,
                    valor_energetico = %s,
                    proteinas = %s,
                    carbohidratos = %s,
                    grasas = %s,
                    beneficios = %s,
                    dosis_recomendada = %s,
                    preparacion = %s,
                    momento_ideal_post_tratamiento = %s,
                    contraindicaciones = %s,
                    forma_almacenar = %s,
                    sabores = %s,
                    precio = %s,
                    porciones = %s
                WHERE codigo = %s
                """
                
                cursor.execute(sql_update, (
                    nutricion_data['nombre'],
                    nutricion_data.get('descripcion', ''),
                    nutricion_data.get('tiempo_resultado', ''),
                    nutricion_data.get('proteina_porcion', 0.0),
                    nutricion_data.get('valor_energetico', 0.0),
                    nutricion_data.get('proteinas', 0.0),
                    nutricion_data.get('carbohidratos', 0.0),
                    nutricion_data.get('grasas', 0.0),
                    nutricion_data.get('beneficios', ''),
                    nutricion_data.get('dosis_recomendada', ''),
                    nutricion_data.get('preparacion', ''),
                    nutricion_data.get('momento_ideal_post_tratamiento', ''),
                    nutricion_data.get('contraindicaciones', ''),
                    nutricion_data.get('forma_almacenar', ''),
                    nutricion_data.get('sabores', ''),
                    nutricion_data.get('precio', 0.0),
                    nutricion_data.get('porciones', 1),
                    codigo
                ))
                
                conn.commit()
                return True, "Producto de nutrición actualizado exitosamente"
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al actualizar producto de nutrición: {e}")
            return False, str(e)
        finally:
            close_db_connection(conn)
    
    # ===== FUNCIONES PARA IMPLEMENTOS =====
    
    @staticmethod
    def listar_implementos(filtros: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Lista implementos con filtros opcionales
        """
        if filtros is None:
            filtros = {}
        
        conn = get_db_connection()
        if conn is None:
            return []
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    codigo, nombre, descripcion, `rango/peso`,
                    ejercicios_posibles, dimensiones, material,
                    peso_total_set, beneficios, dificultad,
                    grupo_muscular, frecuencia, duracion,
                    contenido_set, uso_recomendado, contras,
                    mantenimiento, precio, peso
                FROM servicio_implementos
                WHERE 1=1
                """
                
                params = []
                
                if filtros.get('nombre'):
                    sql += " AND nombre LIKE %s"
                    params.append(f"%{filtros['nombre']}%")
                
                if filtros.get('material'):
                    sql += " AND material LIKE %s"
                    params.append(f"%{filtros['material']}%")
                
                if filtros.get('grupo_muscular'):
                    sql += " AND grupo_muscular LIKE %s"
                    params.append(f"%{filtros['grupo_muscular']}%")
                
                if filtros.get('dificultad_min') is not None:
                    sql += " AND dificultad >= %s"
                    params.append(filtros['dificultad_min'])
                
                if filtros.get('dificultad_max') is not None:
                    sql += " AND dificultad <= %s"
                    params.append(filtros['dificultad_max'])
                
                sql += " ORDER BY nombre ASC"
                
                cursor.execute(sql, params)
                implementos = cursor.fetchall()
                
                # Procesar datos para JSON
                resultado = []
                for implemento in implementos:
                    implemento_dict = dict(implemento)
                    # Convertir Decimal a float
                    for key, value in implemento_dict.items():
                        if isinstance(value, Decimal):
                            implemento_dict[key] = float(value)
                    resultado.append(implemento_dict)
                
                return resultado
                
        except Exception as e:
            print(f"❌ Error en listar_implementos: {e}")
            return []
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def obtener_implemento_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un implemento por su código
        """
        conn = get_db_connection()
        if conn is None:
            return None
        
        try:
            with conn.cursor() as cursor:
                sql = """
                SELECT 
                    codigo, nombre, descripcion, `rango/peso`,
                    ejercicios_posibles, dimensiones, material,
                    peso_total_set, beneficios, dificultad,
                    grupo_muscular, frecuencia, duracion,
                    contenido_set, uso_recomendado, contras,
                    mantenimiento, precio, peso
                FROM servicio_implementos
                WHERE codigo = %s
                """
                
                cursor.execute(sql, (codigo,))
                implemento = cursor.fetchone()
                
                if implemento:
                    implemento_dict = dict(implemento)
                    # Convertir Decimal a float
                    for key, value in implemento_dict.items():
                        if isinstance(value, Decimal):
                            implemento_dict[key] = float(value)
                    return implemento_dict
                
                return None
                
        except Exception as e:
            print(f"❌ Error en obtener_implemento_por_codigo: {e}")
            return None
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def crear_implemento(implemento_data: Dict[str, Any]) -> tuple[bool, str, str]:
        """
        Crea un nuevo implemento
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos", ""
        
        try:
            with conn.cursor() as cursor:
                # Verificar si el código ya existe
                sql_check = "SELECT codigo FROM servicio_implementos WHERE codigo = %s"
                cursor.execute(sql_check, (implemento_data['codigo'],))
                if cursor.fetchone():
                    return False, "El código de implemento ya existe", ""
                
                # Insertar nuevo implemento
                sql_insert = """
                INSERT INTO servicio_implementos (
                    codigo, nombre, descripcion, `rango/peso`,
                    ejercicios_posibles, dimensiones, material,
                    peso_total_set, beneficios, dificultad,
                    grupo_muscular, frecuencia, duracion,
                    contenido_set, uso_recomendado, contras,
                    mantenimiento, precio, peso
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(sql_insert, (
                    implemento_data['codigo'],
                    implemento_data['nombre'],
                    implemento_data.get('descripcion', ''),
                    implemento_data.get('rango_peso', ''),
                    implemento_data.get('ejercicios_posibles', ''),
                    implemento_data.get('dimensiones', ''),
                    implemento_data.get('material', ''),
                    implemento_data.get('peso_total_set', 0.0),
                    implemento_data.get('beneficios', ''),
                    implemento_data.get('dificultad', 1),
                    implemento_data.get('grupo_muscular', ''),
                    implemento_data.get('frecuencia', ''),
                    implemento_data.get('duracion', ''),
                    implemento_data.get('contenido_set', ''),
                    implemento_data.get('uso_recomendado', ''),
                    implemento_data.get('contras', ''),
                    implemento_data.get('mantenimiento', ''),
                    implemento_data.get('precio', 0.0),
                    implemento_data.get('peso', 0.0)
                ))
                
                conn.commit()
                return True, "Implemento creado exitosamente", implemento_data['codigo']
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al crear implemento: {e}")
            return False, str(e), ""
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def actualizar_implemento(codigo: str, implemento_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Actualiza un implemento existente
        """
        conn = get_db_connection()
        if conn is None:
            return False, "Error de conexión a la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar que el implemento existe
                sql_check = "SELECT codigo FROM servicio_implementos WHERE codigo = %s"
                cursor.execute(sql_check, (codigo,))
                if not cursor.fetchone():
                    return False, "Implemento no encontrado"
                
                # Actualizar implemento
                sql_update = """
                UPDATE servicio_implementos SET
                    nombre = %s,
                    descripcion = %s,
                    `rango/peso` = %s,
                    ejercicios_posibles = %s,
                    dimensiones = %s,
                    material = %s,
                    peso_total_set = %s,
                    beneficios = %s,
                    dificultad = %s,
                    grupo_muscular = %s,
                    frecuencia = %s,
                    duracion = %s,
                    contenido_set = %s,
                    uso_recomendado = %s,
                    contras = %s,
                    mantenimiento = %s,
                    precio = %s,
                    peso = %s
                WHERE codigo = %s
                """
                
                cursor.execute(sql_update, (
                    implemento_data['nombre'],
                    implemento_data.get('descripcion', ''),
                    implemento_data.get('rango_peso', ''),
                    implemento_data.get('ejercicios_posibles', ''),
                    implemento_data.get('dimensiones', ''),
                    implemento_data.get('material', ''),
                    implemento_data.get('peso_total_set', 0.0),
                    implemento_data.get('beneficios', ''),
                    implemento_data.get('dificultad', 1),
                    implemento_data.get('grupo_muscular', ''),
                    implemento_data.get('frecuencia', ''),
                    implemento_data.get('duracion', ''),
                    implemento_data.get('contenido_set', ''),
                    implemento_data.get('uso_recomendado', ''),
                    implemento_data.get('contras', ''),
                    implemento_data.get('mantenimiento', ''),
                    implemento_data.get('precio', 0.0),
                    implemento_data.get('peso', 0.0),
                    codigo
                ))
                
                conn.commit()
                return True, "Implemento actualizado exitosamente"
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Error al actualizar implemento: {e}")
            return False, str(e)
        finally:
            close_db_connection(conn)