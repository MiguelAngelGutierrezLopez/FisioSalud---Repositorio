from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import traceback
from modelo.AdminFisioModel import AdminFisioModel
from controlador.AuthAdminController import AuthAdminController

class AdminFisioController:
    
    @staticmethod
    async def obtener_estadisticas_fisio(request: Request):
        """
        Obtiene estadísticas para el dashboard de fisioterapeutas
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
            estadisticas = AdminFisioModel.obtener_estadisticas_terapeutas()
            
            return JSONResponse(content={
                "success": True,
                "data": estadisticas
            })
                
        except Exception as e:
            print(f"❌ Error en obtener_estadisticas_fisio: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def listar_terapeutas(request: Request):
        """
        Lista fisioterapeutas con filtros
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
            especializacion = request.query_params.get('especializacion', '')
            estado = request.query_params.get('estado', '')
            
            # Obtener terapeutas del modelo
            terapeutas = AdminFisioModel.listar_terapeutas(
                nombre=nombre,
                especializacion=especializacion,
                estado=estado
            )
            
            return JSONResponse(content={
                "success": True,
                "data": terapeutas,
                "total": len(terapeutas)
            })
                
        except Exception as e:
            print(f"❌ Error en listar_terapeutas: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_terapeuta(request: Request, codigo: str):
        """
        Obtiene un terapeuta específico por código
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener terapeuta del modelo
            terapeuta = AdminFisioModel.obtener_terapeuta_por_codigo(codigo)
            
            if not terapeuta:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Terapeuta no encontrado"}
                )
            
            return JSONResponse(content={
                "success": True,
                "data": terapeuta
            })
                
        except Exception as e:
            print(f"❌ Error en obtener_terapeuta: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def crear_terapeuta(request: Request):
        """
        Crea un nuevo fisioterapeuta
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
            required_fields = ['Codigo_trabajador', 'nombre_completo', 'fisio_correo', 'telefono']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Crear terapeuta en el modelo
            success, message, codigo_terapeuta = AdminFisioModel.crear_terapeuta(body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"codigo_trabajador": codigo_terapeuta}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"❌ Error en crear_terapeuta: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def actualizar_terapeuta(request: Request, codigo: str):
        """
        Actualiza un fisioterapeuta existente
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
            required_fields = ['nombre_completo', 'fisio_correo', 'telefono']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Actualizar terapeuta en el modelo
            success, message = AdminFisioModel.actualizar_terapeuta(codigo, body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"codigo_trabajador": codigo}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"❌ Error en actualizar_terapeuta: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def cambiar_estado_terapeuta(request: Request, codigo: str):
        """
        Cambia el estado de un fisioterapeuta
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener nuevo estado del body
            body = await request.json()
            
            if 'estado' not in body:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Campo 'estado' es requerido"}
                )
            
            nuevo_estado = body['estado']
            
            # Cambiar estado en el modelo
            success, message = AdminFisioModel.cambiar_estado_terapeuta(codigo, nuevo_estado)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"codigo_trabajador": codigo, "nuevo_estado": nuevo_estado}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"❌ Error en cambiar_estado_terapeuta: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_especializaciones(request: Request):
        """
        Obtiene lista de especializaciones únicas
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener especializaciones del modelo
            especializaciones = AdminFisioModel.obtener_especializaciones()
            
            return JSONResponse(content={
                "success": True,
                "data": especializaciones,
                "total": len(especializaciones)
            })
                
        except Exception as e:
            print(f"❌ Error en obtener_especializaciones: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )