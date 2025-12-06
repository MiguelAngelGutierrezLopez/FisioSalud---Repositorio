from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import traceback
from modelo.AdminServicioModel import AdminServicioModel
from controlador.AuthAdminController import AuthAdminController

class AdminServicioController:
    
    # ===== ESTADÍSTICAS GENERALES =====
    
    @staticmethod
    async def obtener_estadisticas_generales(request: Request):
        """
        Obtiene estadísticas generales de todos los servicios
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener estadísticas del modelo
            estadisticas = AdminServicioModel.obtener_estadisticas_generales()
            
            return JSONResponse(content={
                "success": True,
                "data": estadisticas
            })
                
        except Exception as e:
            print(f"❌ Error en obtener_estadisticas_generales: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== TERAPIAS =====
    
    @staticmethod
    async def listar_terapias(request: Request):
        """
        Lista servicios de terapia con filtros
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
            modalidad = request.query_params.get('modalidad', '')
            duracion_min = request.query_params.get('duracion_min')
            duracion_max = request.query_params.get('duracion_max')
            
            # Preparar filtros
            filtros = {}
            if nombre:
                filtros['nombre'] = nombre
            if modalidad:
                filtros['modalidad'] = modalidad
            if duracion_min and duracion_min.isdigit():
                filtros['duracion_min'] = int(duracion_min)
            if duracion_max and duracion_max.isdigit():
                filtros['duracion_max'] = int(duracion_max)
            
            # Obtener terapias del modelo
            terapias = AdminServicioModel.listar_terapias(filtros)
            
            return JSONResponse(content={
                "success": True,
                "data": terapias,
                "total": len(terapias)
            })
                
        except Exception as e:
            print(f"❌ Error en listar_terapias: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_terapia(request: Request, codigo: str):
        """
        Obtiene una terapia específica por código
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener terapia del modelo
            terapia = AdminServicioModel.obtener_terapia_por_codigo(codigo)
            
            if not terapia:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Terapia no encontrada"}
                )
            
            return JSONResponse(content={
                "success": True,
                "data": terapia
            })
                
        except Exception as e:
            print(f"❌ Error en obtener_terapia: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def crear_terapia(request: Request):
        """
        Crea un nuevo servicio de terapia
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
            required_fields = ['codigo', 'nombre', 'precio']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Crear terapia en el modelo
            success, message, codigo_terapia = AdminServicioModel.crear_terapia(body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"codigo": codigo_terapia}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"❌ Error en crear_terapia: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def actualizar_terapia(request: Request, codigo: str):
        """
        Actualiza un servicio de terapia existente
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
            required_fields = ['nombre', 'precio']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Actualizar terapia en el modelo
            success, message = AdminServicioModel.actualizar_terapia(codigo, body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"codigo": codigo}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"❌ Error en actualizar_terapia: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== NUTRICIÓN =====
    
    @staticmethod
    async def listar_nutricion(request: Request):
        """
        Lista productos de nutrición con filtros
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
            sabor = request.query_params.get('sabor', '')
            porciones_min = request.query_params.get('porciones_min')
            porciones_max = request.query_params.get('porciones_max')
            
            # Preparar filtros
            filtros = {}
            if nombre:
                filtros['nombre'] = nombre
            if sabor:
                filtros['sabor'] = sabor
            if porciones_min and porciones_min.isdigit():
                filtros['porciones_min'] = int(porciones_min)
            if porciones_max and porciones_max.isdigit():
                filtros['porciones_max'] = int(porciones_max)
            
            # Obtener nutrición del modelo
            nutricion = AdminServicioModel.listar_nutricion(filtros)
            
            return JSONResponse(content={
                "success": True,
                "data": nutricion,
                "total": len(nutricion)
            })
                
        except Exception as e:
            print(f"❌ Error en listar_nutricion: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_nutricion(request: Request, codigo: str):
        """
        Obtiene un producto de nutrición específico por código
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener nutrición del modelo
            producto = AdminServicioModel.obtener_nutricion_por_codigo(codigo)
            
            if not producto:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Producto de nutrición no encontrado"}
                )
            
            return JSONResponse(content={
                "success": True,
                "data": producto
            })
                
        except Exception as e:
            print(f"❌ Error en obtener_nutricion: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def crear_nutricion(request: Request):
        """
        Crea un nuevo producto de nutrición
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
            required_fields = ['codigo', 'nombre', 'precio', 'porciones']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Crear nutrición en el modelo
            success, message, codigo_producto = AdminServicioModel.crear_nutricion(body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"codigo": codigo_producto}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"❌ Error en crear_nutricion: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def actualizar_nutricion(request: Request, codigo: str):
        """
        Actualiza un producto de nutrición existente
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
            required_fields = ['nombre', 'precio', 'porciones']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Actualizar nutrición en el modelo
            success, message = AdminServicioModel.actualizar_nutricion(codigo, body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"codigo": codigo}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"❌ Error en actualizar_nutricion: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== IMPLEMENTOS =====
    
    @staticmethod
    async def listar_implementos(request: Request):
        """
        Lista implementos con filtros
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
            material = request.query_params.get('material', '')
            grupo_muscular = request.query_params.get('grupo_muscular', '')
            dificultad_min = request.query_params.get('dificultad_min')
            dificultad_max = request.query_params.get('dificultad_max')
            
            # Preparar filtros
            filtros = {}
            if nombre:
                filtros['nombre'] = nombre
            if material:
                filtros['material'] = material
            if grupo_muscular:
                filtros['grupo_muscular'] = grupo_muscular
            if dificultad_min and dificultad_min.isdigit():
                filtros['dificultad_min'] = int(dificultad_min)
            if dificultad_max and dificultad_max.isdigit():
                filtros['dificultad_max'] = int(dificultad_max)
            
            # Obtener implementos del modelo
            implementos = AdminServicioModel.listar_implementos(filtros)
            
            return JSONResponse(content={
                "success": True,
                "data": implementos,
                "total": len(implementos)
            })
                
        except Exception as e:
            print(f"❌ Error en listar_implementos: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_implemento(request: Request, codigo: str):
        """
        Obtiene un implemento específico por código
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener implemento del modelo
            implemento = AdminServicioModel.obtener_implemento_por_codigo(codigo)
            
            if not implemento:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Implemento no encontrado"}
                )
            
            return JSONResponse(content={
                "success": True,
                "data": implemento
            })
                
        except Exception as e:
            print(f"❌ Error en obtener_implemento: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def crear_implemento(request: Request):
        """
        Crea un nuevo implemento
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
            required_fields = ['codigo', 'nombre', 'precio', 'peso']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Crear implemento en el modelo
            success, message, codigo_implemento = AdminServicioModel.crear_implemento(body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"codigo": codigo_implemento}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"❌ Error en crear_implemento: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def actualizar_implemento(request: Request, codigo: str):
        """
        Actualiza un implemento existente
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
            required_fields = ['nombre', 'precio', 'peso']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Actualizar implemento en el modelo
            success, message = AdminServicioModel.actualizar_implemento(codigo, body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"codigo": codigo}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"❌ Error en actualizar_implemento: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )