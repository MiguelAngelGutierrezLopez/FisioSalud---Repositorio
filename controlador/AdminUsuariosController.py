from fastapi import Request, UploadFile, File
from fastapi.responses import JSONResponse, Response
from typing import Optional, Dict, List, Any
import traceback
import csv
import io
from datetime import datetime
import hashlib 
from decimal import Decimal
from controlador.AuthAdminController import AuthAdminController

class AdminUsuariosController:
    
    @staticmethod
    async def obtener_estadisticas_admin(request: Request):
        """
        Obtiene estadísticas para el dashboard
        """
        try:
            print("📊 INICIANDO obtener_estadisticas_admin")
            
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                print("❌ No hay sesión admin")
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado. Inicie sesión."}
                )
            
            print("✅ Sesión admin verificada")
            
            from bd.conexion_bd import get_db_connection
            
            print("🔌 Intentando conexión a BD...")
            conn = get_db_connection()
            if not conn:
                print("❌ Error de conexión a BD")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error de conexión a BD"}
                )
            print("✅ Conexión a BD establecida")
            
            try:
                with conn.cursor() as cursor:
                    # 1. Total de usuarios
                    sql_usuarios = """
                    SELECT COUNT(*) as total_usuarios,
                        SUM(CASE WHEN estado = 'Activo' THEN 1 ELSE 0 END) as usuarios_activos
                    FROM usuario
                    """
                    print("📋 Ejecutando consulta de usuarios...")
                    cursor.execute(sql_usuarios)
                    stats_usuarios = cursor.fetchone()
                    print(f"📊 Resultado usuarios: {stats_usuarios}")
                    
                    # 2. Total de pacientes (registrados en tabla paciente)
                    sql_pacientes = """
                    SELECT COUNT(DISTINCT ID_usuario) as total_pacientes
                    FROM paciente
                    """
                    print("📋 Ejecutando consulta de pacientes...")
                    cursor.execute(sql_pacientes)
                    stats_pacientes = cursor.fetchone()
                    print(f"📊 Resultado pacientes: {stats_pacientes}")
                    
                    # 3. Usuarios con historial médico (en tabla usuario)
                    sql_con_historial = """
                    SELECT COUNT(*) as con_historial
                    FROM usuario
                    WHERE historial_medico IS NOT NULL 
                    AND TRIM(historial_medico) != ''
                    """
                    print("📋 Ejecutando consulta de historial...")
                    cursor.execute(sql_con_historial)
                    stats_historial = cursor.fetchone()
                    print(f"📊 Resultado historial: {stats_historial}")
                    
                    # 4. Citas confirmadas recientemente
                    sql_citas_confirmadas = """
                    SELECT COUNT(*) as citas_confirmadas
                    FROM cita
                    WHERE estado = 'confirmada'
                    AND fecha_cita >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    """
                    print("📋 Ejecutando consulta de citas...")
                    cursor.execute(sql_citas_confirmadas)
                    stats_citas = cursor.fetchone()
                    print(f"📊 Resultado citas: {stats_citas}")
                    
                    # Convertir valores numéricos a int
                    resultado = {
                        "total_usuarios": int(stats_usuarios['total_usuarios']) if stats_usuarios else 0,
                        "usuarios_activos": int(stats_usuarios['usuarios_activos']) if stats_usuarios else 0,
                        "total_pacientes": int(stats_pacientes['total_pacientes']) if stats_pacientes else 0,
                        "con_historial": int(stats_historial['con_historial']) if stats_historial else 0,
                        "citas_confirmadas": int(stats_citas['citas_confirmadas']) if stats_citas else 0
                    }
                    
                    print(f"📊 Resultado final: {resultado}")
                    
                    return JSONResponse(content={
                        "success": True,
                        "data": resultado
                    })
                    
            except Exception as e:
                print(f"❌ Error en consultas de estadísticas: {e}")
                import traceback
                traceback.print_exc()
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    print("🔌 Conexión a BD cerrada")
                    
        except Exception as e:
            print(f"❌ Error en obtener_estadisticas_admin: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def listar_usuarios(request: Request):
        """
        Lista usuarios de la tabla usuario con filtros
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener parámetros de query
            nombre = request.query_params.get('nombre', '')
            estado = request.query_params.get('estado', '')
            correo = request.query_params.get('correo', '')
            
            from bd.conexion_bd import get_db_connection
            
            conn = get_db_connection()
            if not conn:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error de conexión a BD"}
                )
            
            try:
                with conn.cursor() as cursor:
                    # Construir query dinámica
                    sql = """
                    SELECT 
                        ID,
                        nombre,
                        apellido,
                        CONCAT(nombre, ' ', apellido) as nombre_completo,
                        genero,
                        correo,
                        telefono,
                        estado,
                        historial_medico
                    FROM usuario
                    WHERE 1=1
                    """
                    
                    params = []
                    
                    if nombre:
                        sql += " AND (nombre LIKE %s OR apellido LIKE %s OR CONCAT(nombre, ' ', apellido) LIKE %s)"
                        params.extend([f"%{nombre}%", f"%{nombre}%", f"%{nombre}%"])
                    
                    if estado and estado != "Todos los estados":
                        sql += " AND estado = %s"
                        params.append(estado)
                    
                    if correo:
                        sql += " AND correo LIKE %s"
                        params.append(f"%{correo}%")
                    
                    sql += " ORDER BY ID DESC"
                    
                    cursor.execute(sql, params)
                    usuarios = cursor.fetchall()
                    
                    # Para cada usuario, verificar si es paciente
                    usuarios_con_info = []
                    for usuario in usuarios:
                        usuario_dict = dict(usuario)
                        
                        # Verificar si tiene registro en paciente
                        sql_paciente = """
                        SELECT COUNT(*) as es_paciente 
                        FROM paciente 
                        WHERE ID_usuario = %s
                        """
                        cursor.execute(sql_paciente, (usuario['ID'],))
                        resultado = cursor.fetchone()
                        
                        usuario_dict['es_paciente'] = resultado['es_paciente'] > 0 if resultado else False
                        
                        # Asegurar que todos los valores sean serializables
                        for key, value in usuario_dict.items():
                            if isinstance(value, Decimal):
                                usuario_dict[key] = float(value)
                            elif hasattr(value, 'strftime'):  # Para fechas
                                usuario_dict[key] = value.strftime('%Y-%m-%d')
                        
                        usuarios_con_info.append(usuario_dict)
                    
                    return JSONResponse(content={
                        "success": True,
                        "data": usuarios_con_info,
                        "total": len(usuarios_con_info)
                    })
                    
            except Exception as e:
                print(f"❌ Error en listar_usuarios: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en listar_usuarios: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def crear_usuario(request: Request):
        """
        Crea nuevo usuario en tabla usuario
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener datos del body
            body = await request.json()
            
            # Validar campos requeridos
            required_fields = ['nombre', 'apellido', 'correo', 'telefono']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            from bd.conexion_bd import get_db_connection
            
            conn = get_db_connection()
            if not conn:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error de conexión a BD"}
                )
            
            try:
                with conn.cursor() as cursor:
                    # Verificar correo duplicado
                    check_sql = "SELECT ID FROM usuario WHERE correo = %s"
                    cursor.execute(check_sql, (body['correo'],))
                    if cursor.fetchone():
                        return JSONResponse(
                            status_code=400,
                            content={"success": False, "error": "El correo ya está registrado"}
                        )
                    
                    # ===== MODIFICACIÓN: Manejo de contraseña =====
                    if 'password' in body and body['password']:
                        # Usar la contraseña proporcionada por el admin
                        contrasena_hash = hashlib.sha256(body['password'].encode()).hexdigest()
                        temp_password = body['password']  # Guardar para mostrar si es necesario
                    else:
                        # Generar contraseña temporal solo si no se proporcionó
                        import random
                        temp_password = str(random.randint(100000, 999999))
                        contrasena_hash = hashlib.sha256(temp_password.encode()).hexdigest()
                    # ===== FIN DE MODIFICACIÓN =====
                    
                    # Crear nuevo usuario
                    insert_sql = """
                    INSERT INTO usuario (
                        nombre, apellido, genero, correo, telefono,
                        contraseña, contraseña_confirmada, estado, historial_medico
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_sql, (
                        body['nombre'],
                        body['apellido'],
                        body.get('genero', ''),
                        body['correo'],
                        body['telefono'],
                        contrasena_hash,
                        contrasena_hash,
                        body.get('estado', 'Activo'),
                        body.get('historial_medico', '')
                    ))
                    
                    user_id = cursor.lastrowid
                    
                    # Si se marcó como paciente, crear también en tabla paciente
                    if body.get('registrar_como_paciente', False):
                        # ===== MODIFICACIÓN: Crear cita primero =====
                        from datetime import datetime
                        codigo_cita = f"CITA-{user_id}-{datetime.now().strftime('%Y%m%d')}"
                        
                        # Crear registro en tabla cita
                        sql_cita = """
                        INSERT INTO cita (cita_id, correo, estado, fecha_cita)
                        VALUES (%s, %s, 'pendiente', CURDATE())
                        """
                        cursor.execute(sql_cita, (codigo_cita, body['correo']))
                        
                        # Ahora crear paciente
                        paciente_sql = """
                        INSERT INTO paciente (codigo_cita, ID_usuario, nombre_completo, estado_cita, fecha_creacion_reporte)
                        VALUES (%s, %s, %s, 'pendiente', CURDATE())
                        """
                        nombre_completo = f"{body['nombre']} {body['apellido']}"
                        cursor.execute(paciente_sql, (codigo_cita, user_id, nombre_completo))
                        # ===== FIN DE MODIFICACIÓN =====
                    
                    conn.commit()
                    
                    return JSONResponse(content={
                        "success": True,
                        "message": "Usuario creado exitosamente",
                        "data": {
                            "user_id": user_id,
                            "temp_password": temp_password if body.get('mostrar_password', False) else None
                        }
                    })
                    
            except Exception as e:
                conn.rollback()
                print(f"❌ Error al crear usuario: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en crear_usuario: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def listar_pacientes(request: Request):
        """
        Lista pacientes registrados (unión de usuario + paciente)
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener parámetros de query
            nombre = request.query_params.get('nombre', '')
            terapeuta = request.query_params.get('terapeuta', '')
            plan = request.query_params.get('plan', '')
            
            from bd.conexion_bd import get_db_connection
            
            conn = get_db_connection()
            if not conn:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error de conexión a BD"}
                )
            
            try:
                with conn.cursor() as cursor:
                    # Unir usuario con paciente
                    sql = """
                    SELECT 
                        p.codigo_cita,
                        p.ID_usuario,
                        u.nombre,
                        u.apellido,
                        CONCAT(u.nombre, ' ', u.apellido) as nombre_completo,
                        u.correo,
                        u.telefono,
                        u.genero,
                        p.terapeuta_asignado,
                        p.estado_cita,
                        p.tipo_plan,
                        p.precio_plan,
                        p.fecha_creacion_reporte,
                        p.historial_medico as historial_paciente,
                        u.historial_medico as historial_usuario
                    FROM paciente p
                    INNER JOIN usuario u ON p.ID_usuario = u.ID
                    WHERE 1=1
                    """
                    
                    params = []
                    
                    if nombre:
                        sql += " AND (u.nombre LIKE %s OR u.apellido LIKE %s)"
                        params.extend([f"%{nombre}%", f"%{nombre}%"])
                    
                    if terapeuta:
                        sql += " AND p.terapeuta_asignado LIKE %s"
                        params.append(f"%{terapeuta}%")
                    
                    if plan and plan != 'Todos los planes':
                        sql += " AND p.tipo_plan = %s"
                        params.append(plan)
                    
                    sql += " ORDER BY p.fecha_creacion_reporte DESC"
                    
                    cursor.execute(sql, params)
                    pacientes = cursor.fetchall()
                    
                    # Convertir Decimal y otros tipos no serializables
                    pacientes_procesados = []
                    for paciente in pacientes:
                        paciente_dict = dict(paciente)
                        
                        # Convertir Decimal a float
                        if isinstance(paciente_dict.get('precio_plan'), Decimal):
                            paciente_dict['precio_plan'] = float(paciente_dict['precio_plan'])
                        elif paciente_dict.get('precio_plan') is not None:
                            # Si ya es otro tipo, asegurarse que sea float
                            try:
                                paciente_dict['precio_plan'] = float(paciente_dict['precio_plan'])
                            except (ValueError, TypeError):
                                paciente_dict['precio_plan'] = 0.0
                        else:
                            paciente_dict['precio_plan'] = 0.0
                        
                        # Asegurar que fecha_creacion_reporte sea string
                        if paciente_dict.get('fecha_creacion_reporte'):
                            if hasattr(paciente_dict['fecha_creacion_reporte'], 'strftime'):
                                paciente_dict['fecha_creacion_reporte'] = paciente_dict['fecha_creacion_reporte'].strftime('%Y-%m-%d')
                        
                        # Asegurar que otros campos sean serializables
                        for key, value in paciente_dict.items():
                            if isinstance(value, Decimal):
                                paciente_dict[key] = float(value)
                            elif hasattr(value, 'strftime'):
                                paciente_dict[key] = value.strftime('%Y-%m-%d')
                        
                        pacientes_procesados.append(paciente_dict)
                    
                    return JSONResponse(content={
                        "success": True,
                        "data": pacientes_procesados,
                        "total": len(pacientes_procesados)
                    })
                    
            except Exception as e:
                print(f"❌ Error en listar_pacientes: {e}")
                import traceback
                traceback.print_exc()
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en listar_pacientes: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def crear_paciente(request: Request):
        """
        Crea nuevo paciente vinculado a usuario existente
        PRIMERO crea cita, LUEGO paciente
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener datos del body
            body = await request.json()
            print(f"📥 Datos recibidos para crear paciente: {body}")
            
            # Validar campos requeridos
            required_fields = ['ID_usuario', 'nombre_completo']
            for field in required_fields:
                if field not in body or not body[field]:
                    print(f"❌ Campo requerido faltante: {field}")
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            from bd.conexion_bd import get_db_connection
            
            print("🔌 Intentando conectar a BD...")
            conn = get_db_connection()
            if not conn:
                print("❌ No se pudo obtener conexión a BD")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error de conexión a BD"}
                )
            print("✅ Conexión a BD establecida")
            
            try:
                with conn.cursor() as cursor:
                    # Verificar que el usuario existe
                    sql_usuario = """
                    SELECT ID, nombre, apellido, correo, telefono 
                    FROM usuario WHERE ID = %s
                    """
                    print(f"🔍 Buscando usuario ID: {body['ID_usuario']}")
                    cursor.execute(sql_usuario, (body['ID_usuario'],))
                    usuario = cursor.fetchone()
                    
                    if not usuario:
                        print(f"❌ Usuario no encontrado: {body['ID_usuario']}")
                        return JSONResponse(
                            status_code=404,
                            content={"success": False, "error": "Usuario no encontrado"}
                        )
                    print(f"✅ Usuario encontrado: {usuario['nombre']} {usuario['apellido']}")
                    
                    # Verificar que no sea paciente ya
                    sql_paciente_check = "SELECT codigo_cita FROM paciente WHERE ID_usuario = %s"
                    cursor.execute(sql_paciente_check, (body['ID_usuario'],))
                    if cursor.fetchone():
                        print(f"❌ Usuario ya es paciente: {body['ID_usuario']}")
                        return JSONResponse(
                            status_code=400,
                            content={"success": False, "error": "Este usuario ya es paciente"}
                        )
                    
                    # ===== 1. GENERAR CÓDIGO DE CITA CONSECUTIVO =====
                    codigo_cita = AdminUsuariosController.generar_codigo_cita_para_admin()
                    
                    if not codigo_cita:
                        print("❌ No se pudo generar código de cita")
                        return JSONResponse(
                            status_code=500,
                            content={"success": False, "error": "No hay códigos de cita disponibles"}
                        )
                    
                    print(f"🔢 Código de cita generado: {codigo_cita}")
                    
                    # ===== 2. CREAR CITA =====
                    from datetime import datetime
                    
                    # Preparar valores para la cita
                    fecha_cita = body.get('fecha_cita', datetime.now().strftime('%Y-%m-%d'))
                    hora_cita = body.get('hora_cita', '09:00:00')
                    servicio = body.get('servicio', 'Consulta General')
                    terapeuta = body.get('terapeuta_asignado', '')
                    telefono = usuario['telefono']
                    correo = usuario['correo']
                    notas = body.get('notas_adicionales', '')
                    tipo_pago = body.get('tipo_pago', 'Por definir')
                    estado = body.get('estado_cita', 'pendiente')
                    
                    print(f"📝 Creando cita con datos:")
                    print(f"  - Código: {codigo_cita}")
                    print(f"  - Paciente: {body['nombre_completo']}")
                    print(f"  - Servicio: {servicio}")
                    print(f"  - Fecha: {fecha_cita}")
                    print(f"  - Hora: {hora_cita}")
                    
                    sql_cita = """
                    INSERT INTO cita (
                        cita_id, nombre_paciente, servicio, terapeuta_designado,
                        telefono, correo, fecha_cita, hora_cita, notas_adicionales,
                        tipo_pago, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(sql_cita, (
                        codigo_cita,
                        body['nombre_completo'],
                        servicio,
                        terapeuta,
                        telefono,
                        correo,
                        fecha_cita,
                        hora_cita,
                        notas,
                        tipo_pago,
                        estado
                    ))
                    print("✅ Cita creada exitosamente")
                    
                    # ===== 3. CREAR PACIENTE =====
                    print("📝 Creando paciente...")
                    sql_paciente = """
                    INSERT INTO paciente (
                        codigo_cita, ID_usuario, nombre_completo, ID_acudiente,
                        historial_medico, terapeuta_asignado, ejercicios_registrados,
                        estado_cita, tipo_plan, precio_plan, fecha_creacion_reporte
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
                    """
                    
                    cursor.execute(sql_paciente, (
                        codigo_cita,
                        body['ID_usuario'],
                        body['nombre_completo'],
                        body.get('ID_acudiente'),
                        body.get('historial_medico', ''),
                        body.get('terapeuta_asignado', ''),
                        body.get('ejercicios_registrados', ''),
                        body.get('estado_cita', 'pendiente'),
                        body.get('tipo_plan', ''),
                        float(body.get('precio_plan', 0.00))
                    ))
                    print("✅ Paciente creado exitosamente")
                    
                    conn.commit()
                    print("✅ Transacción confirmada")
                    
                    return JSONResponse(content={
                        "success": True,
                        "message": "Paciente y cita creados exitosamente",
                        "data": {
                            "codigo_cita": codigo_cita,
                            "usuario_id": body['ID_usuario'],
                            "nombre_paciente": body['nombre_completo'],
                            "tipo_codigo": "admin"  # Indica que es del rango admin
                        }
                    })
                    
            except Exception as e:
                conn.rollback()
                print(f"❌ ERROR en transacción: {str(e)}")
                import traceback
                traceback.print_exc()
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": f"Error en base de datos: {str(e)}"}
                )
            finally:
                if conn:
                    conn.close()
                    print("🔌 Conexión a BD cerrada")
                    
        except Exception as e:
            print(f"❌ ERROR GENERAL en crear_paciente: {str(e)}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": f"Error interno del servidor: {str(e)}"}
            )
    
    @staticmethod
    async def obtener_historial_completo(request: Request, usuario_id: int):
        """
        Obtiene historial completo (usuario + paciente si existe)
        """
        try:
            # Verificar sesión
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            from bd.conexion_bd import get_db_connection
            
            conn = get_db_connection()
            if not conn:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error de conexión a BD"}
                )
            
            try:
                with conn.cursor() as cursor:
                    # Obtener datos del usuario
                    sql_usuario = """
                    SELECT 
                        ID, nombre, apellido, genero, correo, telefono,
                        estado, historial_medico
                    FROM usuario 
                    WHERE ID = %s
                    """
                    cursor.execute(sql_usuario, (usuario_id,))
                    usuario = cursor.fetchone()
                    
                    if not usuario:
                        return JSONResponse(
                            status_code=404,
                            content={"success": False, "error": "Usuario no encontrado"}
                        )
                    
                    # Obtener datos del paciente si existe
                    sql_paciente = """
                    SELECT 
                        codigo_cita, terapeuta_asignado, estado_cita,
                        tipo_plan, precio_plan, fecha_creacion_reporte,
                        historial_medico, ejercicios_registrados
                    FROM paciente
                    WHERE ID_usuario = %s
                    ORDER BY fecha_creacion_reporte DESC
                    LIMIT 1
                    """
                    cursor.execute(sql_paciente, (usuario_id,))
                    paciente = cursor.fetchone()
                    
                    # Procesar datos para JSON
                    usuario_dict = dict(usuario) if usuario else {}
                    
                    # Asegurar serialización del usuario
                    for key, value in usuario_dict.items():
                        if isinstance(value, Decimal):
                            usuario_dict[key] = float(value)
                        elif hasattr(value, 'strftime'):
                            usuario_dict[key] = value.strftime('%Y-%m-%d')
                    
                    paciente_dict = None
                    if paciente:
                        paciente_dict = dict(paciente)
                        # Convertir Decimal a float
                        for key, value in paciente_dict.items():
                            if isinstance(value, Decimal):
                                paciente_dict[key] = float(value)
                            elif hasattr(value, 'strftime'):
                                paciente_dict[key] = value.strftime('%Y-%m-%d')
                    
                    historial_completo = {
                        "usuario": usuario_dict,
                        "paciente": paciente_dict
                    }
                    
                    return JSONResponse(content={
                        "success": True,
                        "data": historial_completo
                    })
                    
            except Exception as e:
                print(f"❌ Error en obtener_historial_completo: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en obtener_historial_completo: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def exportar_csv(request: Request):
        """
        Exporta datos a CSV
        """
        try:
            # Verificar sesión
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            tipo = request.query_params.get('tipo', 'usuarios')
            
            from bd.conexion_bd import get_db_connection
            
            conn = get_db_connection()
            if not conn:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error de conexión a BD"}
                )
            
            try:
                with conn.cursor() as cursor:
                    if tipo == 'usuarios':
                        sql = """
                        SELECT 
                            ID, nombre, apellido, genero, correo, telefono,
                            estado
                        FROM usuario
                        ORDER BY ID DESC
                        """
                        cursor.execute(sql)
                        data = cursor.fetchall()
                        filename = f"usuarios_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        
                    elif tipo == 'pacientes':
                        sql = """
                        SELECT 
                            p.codigo_cita,
                            u.ID as usuario_id,
                            u.nombre,
                            u.apellido,
                            u.correo,
                            u.telefono,
                            u.genero,
                            p.terapeuta_asignado,
                            p.estado_cita,
                            p.tipo_plan,
                            p.precio_plan,
                            p.fecha_creacion_reporte
                        FROM paciente p
                        INNER JOIN usuario u ON p.ID_usuario = u.ID
                        ORDER BY p.fecha_creacion_reporte DESC
                        """
                        cursor.execute(sql)
                        data = cursor.fetchall()
                        filename = f"pacientes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    
                    else:
                        return JSONResponse(
                            status_code=400,
                            content={"success": False, "error": "Tipo de exportación no válido"}
                        )
                    
                    # Procesar datos: convertir tipos no serializables
                    processed_data = []
                    for row in data:
                        row_dict = dict(row)
                        # Convertir todos los tipos no serializables
                        for key, value in row_dict.items():
                            if isinstance(value, Decimal):
                                row_dict[key] = float(value)
                            elif hasattr(value, 'strftime'):  # Para fechas
                                row_dict[key] = value.strftime('%Y-%m-%d')
                            elif isinstance(value, (bytes, bytearray)):
                                row_dict[key] = value.decode('utf-8', errors='ignore')
                        processed_data.append(row_dict)
                    
                    # Crear CSV en memoria
                    output = io.StringIO()
                    if processed_data:
                        writer = csv.DictWriter(output, fieldnames=processed_data[0].keys())
                        writer.writeheader()
                        for row in processed_data:
                            writer.writerow(row)
                    
                    csv_content = output.getvalue()
                    
                    # Devolver como respuesta descargable
                    return Response(
                        content=csv_content,
                        media_type="text/csv",
                        headers={
                            "Content-Disposition": f"attachment; filename={filename}",
                            "Content-Type": "text/csv; charset=utf-8"
                        }
                    )
                    
            except Exception as e:
                print(f"❌ Error en exportar_csv: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en exportar_csv: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def debug_archivo(request: Request, file: UploadFile = File(...)):
        """
        Endpoint para debuguear archivos
        """
        content = await file.read()
        
        return JSONResponse({
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(content),
            "first_20_bytes": str(content[:20]),
            "is_pdf": content.startswith(b'%PDF'),
            "hex_first_10": content[:10].hex()
        })
    
    @staticmethod
    async def eliminar_usuario(request: Request, usuario_id: int):
        """
        Elimina un usuario y todos sus registros relacionados
        Si es paciente, también elimina citas y otros registros
        """
        try:
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(status_code=401, content={
                    "success": False, 
                    "error": "Acceso no autorizado"
                })
            
            from bd.conexion_bd import get_db_connection
            conn = get_db_connection()
            
            try:
                with conn.cursor() as cursor:
                    # 1. Verificar si el usuario existe y si es paciente
                    sql_check = """
                    SELECT u.ID, u.nombre, u.apellido, 
                        (SELECT COUNT(*) FROM paciente p WHERE p.ID_usuario = u.ID) as es_paciente
                    FROM usuario u
                    WHERE u.ID = %s
                    """
                    cursor.execute(sql_check, (usuario_id,))
                    usuario = cursor.fetchone()
                    
                    if not usuario:
                        return JSONResponse(status_code=404, content={
                            "success": False, 
                            "error": "Usuario no encontrado"
                        })
                    
                    print(f"🗑️ Eliminando usuario: {usuario['nombre']} {usuario['apellido']}")
                    print(f"ℹ️ Es paciente: {usuario['es_paciente'] > 0}")
                    
                    # 2. Si es paciente, obtener sus códigos de cita
                    codigos_cita = []
                    if usuario['es_paciente'] > 0:
                        sql_codigos = "SELECT codigo_cita FROM paciente WHERE ID_usuario = %s"
                        cursor.execute(sql_codigos, (usuario_id,))
                        resultados = cursor.fetchall()
                        codigos_cita = [r['codigo_cita'] for r in resultados]
                        print(f"📋 Códigos de cita a eliminar: {codigos_cita}")
                    
                    # 3. Eliminar acudientes relacionados (si existen)
                    if codigos_cita:
                        for codigo in codigos_cita:
                            try:
                                sql_delete_acudiente = "DELETE FROM acudiente WHERE cita_id = %s"
                                cursor.execute(sql_delete_acudiente, (codigo,))
                                print(f"✅ Acudiente eliminado para cita {codigo}")
                            except Exception as e:
                                print(f"ℹ️ No se pudo eliminar acudiente para cita {codigo}: {e}")
                    
                    # 4. Eliminar registros en paciente
                    sql_delete_paciente = "DELETE FROM paciente WHERE ID_usuario = %s"
                    cursor.execute(sql_delete_paciente, (usuario_id,))
                    print("✅ Registros de paciente eliminados")
                    
                    # 5. Eliminar citas asociadas (si existen)
                    if codigos_cita:
                        for codigo in codigos_cita:
                            sql_delete_cita = "DELETE FROM cita WHERE cita_id = %s"
                            cursor.execute(sql_delete_cita, (codigo,))
                            print(f"✅ Cita {codigo} eliminada")
                    
                    # 6. Eliminar usuario
                    sql_delete_usuario = "DELETE FROM usuario WHERE ID = %s"
                    cursor.execute(sql_delete_usuario, (usuario_id,))
                    print("✅ Usuario eliminado")
                    
                    conn.commit()
                    
                    return JSONResponse(content={
                        "success": True,
                        "message": "Usuario y todos sus registros relacionados eliminados exitosamente",
                        "data": {
                            "usuario_id": usuario_id,
                            "nombre_completo": f"{usuario['nombre']} {usuario['apellido']}",
                            "es_paciente": usuario['es_paciente'] > 0,
                            "citas_eliminadas": len(codigos_cita)
                        }
                    })
                    
            except Exception as e:
                conn.rollback()
                print(f"❌ Error al eliminar usuario: {e}")
                import traceback
                traceback.print_exc()
                return JSONResponse(status_code=500, content={
                    "success": False, 
                    "error": str(e)
                })
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en eliminar_usuario: {e}")
            return JSONResponse(status_code=500, content={
                "success": False, 
                "error": "Error interno del servidor"
            })
        

    @staticmethod    
    async def convertir_a_paciente(request: Request, usuario_id: int):
        """
        Convierte un usuario existente en paciente, creando registros completos en ambas tablas
        """
        try:
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(status_code=401, content={
                    "success": False, 
                    "error": "Acceso no autorizado"
                })
            
            # Obtener datos del body
            body = await request.json()
            
            from bd.conexion_bd import get_db_connection
            from datetime import datetime
            import random
            
            conn = get_db_connection()
            if not conn:
                return JSONResponse(status_code=500, content={
                    "success": False, 
                    "error": "Error de conexión a BD"
                })
            
            try:
                with conn.cursor() as cursor:   
                    # 1. Verificar si ya es paciente
                    sql_check = "SELECT codigo_cita FROM paciente WHERE ID_usuario = %s"
                    cursor.execute(sql_check, (usuario_id,))
                    if cursor.fetchone():
                        return JSONResponse(status_code=400, content={
                            "success": False, 
                            "error": "Este usuario ya es paciente"
                        })
                    
                    # 2. Obtener datos COMPLETOS del usuario
                    sql_usuario = """
                    SELECT ID, nombre, apellido, correo, telefono, genero, estado, historial_medico
                    FROM usuario WHERE ID = %s
                    """
                    cursor.execute(sql_usuario, (usuario_id,))
                    usuario = cursor.fetchone()
                    
                    if not usuario:
                        return JSONResponse(status_code=404, content={
                            "success": False, 
                            "error": "Usuario no encontrado"
                        })
                    
                    # 3. Generar código de cita consecutivo para admin
                    codigo_cita = AdminUsuariosController.generar_codigo_cita_para_admin()
                    if not codigo_cita:
                        return JSONResponse(status_code=500, content={
                            "success": False, 
                            "error": "No hay códigos de cita disponibles en el rango admin"
                        })
                    
                    # 4. Obtener valores del formulario o usar valores por defecto
                    # Si vienen del body, usar esos; si no, usar valores por defecto
                    nombre_completo = f"{usuario['nombre']} {usuario['apellido']}"
                    telefono = usuario['telefono'] or body.get('telefono', '000-000-0000')
                    correo = usuario['correo']
                    servicio = body.get('servicio', 'Consulta General')
                    terapeuta = body.get('terapeuta_designado', body.get('terapeuta_asignado', 'Por asignar'))
                    fecha_cita = body.get('fecha_cita', datetime.now().strftime('%Y-%m-%d'))
                    hora_cita = body.get('hora_cita', '09:00:00')
                    notas = body.get('notas_adicionales', 'Usuario convertido automáticamente por administrador')
                    tipo_pago = body.get('tipo_pago', 'Por definir')
                    estado_cita = body.get('estado_cita', 'pendiente')
                    tipo_plan = body.get('tipo_plan', 'Básico')
                    precio_plan = float(body.get('precio_plan', 0.0))
                    historial_medico = body.get('historial_medico', usuario.get('historial_medico', ''))
                    
                    # 5. CREAR CITA COMPLETA (con todos los campos obligatorios)
                    print(f"📝 Creando cita completa: {codigo_cita}")
                    
                    sql_cita = """
                    INSERT INTO cita (
                        cita_id, nombre_paciente, servicio, terapeuta_designado,
                        telefono, correo, fecha_cita, hora_cita, notas_adicionales,
                        tipo_pago, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(sql_cita, (
                        codigo_cita,
                        nombre_completo,
                        servicio,
                        terapeuta,
                        telefono,
                        correo,
                        fecha_cita,
                        hora_cita,
                        notas,
                        tipo_pago,
                        estado_cita
                    ))
                    print("✅ Cita creada exitosamente con todos los campos")
                    
                    # 6. CREAR PACIENTE COMPLETO
                    print(f"📝 Creando paciente: {usuario_id}")
                    
                    sql_paciente = """
                    INSERT INTO paciente (
                        codigo_cita, ID_usuario, nombre_completo, ID_acudiente,
                        historial_medico, terapeuta_asignado, ejercicios_registrados,
                        estado_cita, tipo_plan, precio_plan, fecha_creacion_reporte
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
                    """
                    
                    cursor.execute(sql_paciente, (
                        codigo_cita,
                        usuario_id,
                        nombre_completo,
                        body.get('ID_acudiente'),  # Puede ser None
                        historial_medico,
                        terapeuta,
                        body.get('ejercicios_registrados', ''),
                        estado_cita,
                        tipo_plan,
                        precio_plan
                    ))
                    print("✅ Paciente creado exitosamente")
                    
                    conn.commit()
                    
                    return JSONResponse(content={
                        "success": True,
                        "message": "Usuario convertido a paciente exitosamente",
                        "data": {
                            "codigo_cita": codigo_cita,
                            "tipo_codigo": "admin",
                            "nombre_paciente": nombre_completo,
                            "servicio": servicio,
                            "terapeuta": terapeuta,
                            "fecha_cita": fecha_cita,
                            "hora_cita": hora_cita,
                            "estado": estado_cita,
                            "tipo_plan": tipo_plan,
                            "precio_plan": precio_plan
                        }
                    })
                    
            except Exception as e:
                conn.rollback()
                print(f"❌ Error al convertir a paciente: {str(e)}")
                import traceback
                traceback.print_exc()
                return JSONResponse(status_code=500, content={
                    "success": False, 
                    "error": f"Error en base de datos: {str(e)}"
                })
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en convertir_a_paciente: {str(e)}")
            return JSONResponse(status_code=500, content={
                "success": False, 
                "error": "Error interno del servidor"
            })
        
    @staticmethod
    async def eliminar_paciente(request: Request, codigo_cita: str):
        """
        Elimina un paciente por código de cita y su cita asociada
        """
        try:
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            from bd.conexion_bd import get_db_connection
            conn = get_db_connection()
            
            try:
                with conn.cursor() as cursor:
                    # 1. Verificar que existe el paciente
                    sql_check_paciente = """
                    SELECT ID_usuario, nombre_completo 
                    FROM paciente 
                    WHERE codigo_cita = %s
                    """
                    cursor.execute(sql_check_paciente, (codigo_cita,))
                    paciente = cursor.fetchone()
                    
                    if not paciente:
                        return JSONResponse(
                            status_code=404,
                            content={"success": False, "error": "Paciente no encontrado"}
                        )
                    
                    print(f"🗑️ Eliminando paciente: {paciente['nombre_completo']} (Cita: {codigo_cita})")
                    
                    # 2. Eliminar acudientes relacionados (si existe la tabla)
                    try:
                        sql_delete_acudiente = "DELETE FROM acudiente WHERE cita_id = %s"
                        cursor.execute(sql_delete_acudiente, (codigo_cita,))
                        print("✅ Acudiente eliminado (si existía)")
                    except Exception as e:
                        print(f"ℹ️ No se pudo eliminar acudiente (posiblemente tabla no existe): {e}")
                    
                    # 3. Eliminar paciente
                    sql_delete_paciente = "DELETE FROM paciente WHERE codigo_cita = %s"
                    cursor.execute(sql_delete_paciente, (codigo_cita,))
                    print("✅ Paciente eliminado")
                    
                    # 4. Eliminar la cita asociada
                    sql_delete_cita = "DELETE FROM cita WHERE cita_id = %s"
                    cursor.execute(sql_delete_cita, (codigo_cita,))
                    print("✅ Cita eliminada")
                    
                    # 5. Verificar si el usuario sigue teniendo otras citas/pacientes
                    sql_verificar_usuario = """
                    SELECT COUNT(*) as total_pacientes 
                    FROM paciente 
                    WHERE ID_usuario = %s
                    """
                    cursor.execute(sql_verificar_usuario, (paciente['ID_usuario'],))
                    resultado = cursor.fetchone()
                    
                    # 6. Si el usuario no tiene más pacientes, actualizar estado si es necesario
                    if resultado['total_pacientes'] == 0:
                        # Opcional: Actualizar algún campo en usuario para indicar que ya no es paciente
                        # sql_update_usuario = "UPDATE usuario SET es_paciente = 0 WHERE ID = %s"
                        # cursor.execute(sql_update_usuario, (paciente['ID_usuario'],))
                        print(f"ℹ️ Usuario {paciente['ID_usuario']} ya no tiene pacientes registrados")
                    
                    conn.commit()
                    
                    return JSONResponse(content={
                        "success": True,
                        "message": "Paciente, cita y registros relacionados eliminados exitosamente",
                        "data": {
                            "codigo_cita": codigo_cita,
                            "usuario_id": paciente['ID_usuario'],
                            "nombre_paciente": paciente['nombre_completo']
                        }
                    })
                    
            except Exception as e:
                conn.rollback()
                print(f"❌ Error al eliminar paciente y cita: {e}")
                return JSONResponse(
                    status_code=500, 
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en eliminar_paciente: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
        
    @staticmethod
    async def cambiar_estado_usuario(request: Request, usuario_id: int):
        """
        Activa o desactiva un usuario
        """
        try:
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener datos del body
            body = await request.json()
            nuevo_estado = body.get('estado', 'Activo')
            
            # Validar estado
            estados_validos = ['Activo', 'Inactivo', 'Pendiente']
            if nuevo_estado not in estados_validos:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": f"Estado inválido. Usa: {', '.join(estados_validos)}"}
                )
            
            from bd.conexion_bd import get_db_connection
            
            conn = get_db_connection()
            if not conn:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error de conexión a BD"}
                )
            
            try:
                with conn.cursor() as cursor:
                    # Verificar que el usuario existe
                    sql_check = "SELECT ID, estado FROM usuario WHERE ID = %s"
                    cursor.execute(sql_check, (usuario_id,))
                    usuario = cursor.fetchone()
                    
                    if not usuario:
                        return JSONResponse(
                            status_code=404,
                            content={"success": False, "error": "Usuario no encontrado"}
                        )
                    
                    # Actualizar estado
                    sql_update = "UPDATE usuario SET estado = %s WHERE ID = %s"
                    cursor.execute(sql_update, (nuevo_estado, usuario_id))
                    
                    conn.commit()
                    
                    return JSONResponse(content={
                        "success": True,
                        "message": f"Estado del usuario actualizado a '{nuevo_estado}'",
                        "data": {
                            "usuario_id": usuario_id,
                            "estado_anterior": usuario['estado'],
                            "estado_nuevo": nuevo_estado
                        }
                    })
                    
            except Exception as e:
                conn.rollback()
                print(f"❌ Error al cambiar estado de usuario: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en cambiar_estado_usuario: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )

    @staticmethod
    async def cambiar_estado_cita(request: Request, codigo_cita: str):
        """
        Cambia el estado de una cita
        """
        try:
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener datos del body
            body = await request.json()
            nuevo_estado = body.get('estado', 'pendiente')
            
            # Validar estado
            estados_validos = ['pendiente', 'confirmada', 'completada', 'cancelada']
            if nuevo_estado not in estados_validos:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": f"Estado inválido. Usa: {', '.join(estados_validos)}"}
                )
            
            from bd.conexion_bd import get_db_connection
            
            conn = get_db_connection()
            if not conn:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error de conexión a BD"}
                )
            
            try:
                with conn.cursor() as cursor:
                    # Verificar que la cita existe
                    sql_check = """
                    SELECT cita_id, estado, nombre_paciente 
                    FROM cita WHERE cita_id = %s
                    """
                    cursor.execute(sql_check, (codigo_cita,))
                    cita = cursor.fetchone()
                    
                    if not cita:
                        return JSONResponse(
                            status_code=404,
                            content={"success": False, "error": "Cita no encontrada"}
                        )
                    
                    # Actualizar estado en cita
                    sql_update_cita = "UPDATE cita SET estado = %s WHERE cita_id = %s"
                    cursor.execute(sql_update_cita, (nuevo_estado, codigo_cita))
                    
                    # Actualizar estado en paciente también (si existe)
                    sql_update_paciente = """
                    UPDATE paciente SET estado_cita = %s 
                    WHERE codigo_cita = %s
                    """
                    cursor.execute(sql_update_paciente, (nuevo_estado, codigo_cita))
                    
                    conn.commit()
                    
                    return JSONResponse(content={
                        "success": True,
                        "message": f"Estado de cita actualizado a '{nuevo_estado}'",
                        "data": {
                            "codigo_cita": codigo_cita,
                            "estado_anterior": cita['estado'],
                            "estado_nuevo": nuevo_estado,
                            "paciente": cita['nombre_paciente']
                        }
                    })
                    
            except Exception as e:
                conn.rollback()
                print(f"❌ Error al cambiar estado de cita: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en cambiar_estado_cita: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    @staticmethod
    def obtener_siguiente_codigo_admin() -> str:
        """
        Obtiene el siguiente código disponible en el pool de admin (FS-0501 a FS-1000)
        """
        from bd.conexion_bd import get_db_connection
        
        conn = get_db_connection()
        if conn is None:
            return ""
        
        try:
            with conn.cursor() as cursor:
                # Definir rango para admin
                inicio_rango, fin_rango = ('FS-0501', 'FS-1000')
                inicio_num = int(inicio_rango.split('-')[1])
                fin_num = int(fin_rango.split('-')[1])
                
                # Buscar todos los códigos de cita existentes
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
                
                # Encontrar el primer número disponible en el rango
                for num in range(inicio_num, fin_num + 1):
                    if num not in numeros_usados:
                        codigo_disponible = f"FS-{num:04d}"
                        print(f"🔢 Código disponible encontrado para admin: {codigo_disponible}")
                        return codigo_disponible
                
                # Si no hay números disponibles en el rango principal
                print("⚠️ ADVERTENCIA: No hay códigos disponibles en el rango admin (0501-1000)")
                
                # Buscar en rango extendido para admin
                return AdminUsuariosController.buscar_codigo_en_rango_extendido_admin()
                
        except Exception as e:
            print(f"❌ Error al obtener siguiente código de admin: {e}")
            import random
            return f"FS-{random.randint(2001, 3000):04d}"  # Fallback aleatorio en rango extendido
        finally:
            if conn:
                conn.close()

    @staticmethod
    def buscar_codigo_en_rango_extendido_admin() -> str:
        """
        Busca un código disponible en rangos extendidos para admin
        """
        try:
            rangos_extendidos = [
                ('FS-2001', 'FS-3000'),
                ('FS-3001', 'FS-4000')
            ]
            
            from bd.conexion_bd import get_db_connection
            
            conn = get_db_connection()
            if conn is None:
                import random
                return f"FS-{random.randint(2001, 4000):04d}"
            
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
                                print(f"🔢 Código encontrado en rango extendido admin: {codigo_disponible}")
                                return codigo_disponible
                    
                    # Si no hay en rangos extendidos, generar aleatorio
                    import random
                    return f"FS-{random.randint(9001, 9999):04d}"
                    
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error al buscar en rango extendido admin: {e}")
            import random
            return f"FS-{random.randint(9001, 9999):04d}"

    @staticmethod
    def generar_codigo_cita_para_admin() -> str:
        """
        Genera un código de cita único para admin en rango FS-0501 a FS-1000
        """
        return AdminUsuariosController.obtener_siguiente_codigo_admin()

    @staticmethod
    async def verificar_estado_codigos_admin(request: Request):
        """
        Verifica el estado del pool de códigos para admin (FS-0501 a FS-1000)
        """
        try:
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            from bd.conexion_bd import get_db_connection
            
            conn = get_db_connection()
            if conn is None:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "No hay conexión"}
                )
            
            try:
                with conn.cursor() as cursor:
                    inicio_rango, fin_rango = ('FS-0501', 'FS-1000')
                    inicio_num = int(inicio_rango.split('-')[1])
                    fin_num = int(fin_rango.split('-')[1])
                    total_codigos = fin_num - inicio_num + 1
                    
                    # Obtener todos los códigos
                    sql = "SELECT cita_id FROM cita WHERE cita_id LIKE 'FS-%'"
                    cursor.execute(sql)
                    todos_codigos = cursor.fetchall()
                    
                    # Contar códigos usados en el rango de admin
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
                    
                    # Calcular estadísticas
                    porcentaje_uso = (codigos_usados / total_codigos * 100) if total_codigos > 0 else 0
                    
                    # Determinar nivel de alerta
                    if codigos_usados < 300:
                        alerta = "BAJO"
                        color = "success"
                    elif codigos_usados < 400:
                        alerta = "MEDIO"
                        color = "warning"
                    else:
                        alerta = "ALTO"
                        color = "danger"
                    
                    return JSONResponse(content={
                        "success": True,
                        "data": {
                            "rango": f"{inicio_rango} - {fin_rango}",
                            "total_codigos": total_codigos,
                            "codigos_usados": codigos_usados,
                            "codigos_disponibles": total_codigos - codigos_usados,
                            "siguiente_disponible": siguiente_disponible,
                            "porcentaje_uso": round(porcentaje_uso, 2),
                            "alerta_nivel": alerta,
                            "alerta_color": color
                        }
                    })
                    
            except Exception as e:
                print(f"❌ Error al verificar estado de códigos: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e)}
                )
            finally:
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"❌ Error en verificar_estado_codigos_admin: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )