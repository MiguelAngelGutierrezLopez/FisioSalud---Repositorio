from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import traceback
from modelo.AdminCitaModel import AdminCitaModel
from controlador.AuthAdminController import AuthAdminController

class AdminCitaController:
    
    # ===== ESTADÍSTICAS =====
    
    @staticmethod
    async def obtener_estadisticas(request: Request):
        """
        Obtiene estadísticas generales de citas
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
            estadisticas = AdminCitaModel.obtener_estadisticas_citas()
            
            return JSONResponse(content={
                "success": True,
                "data": estadisticas
            })
                
        except Exception as e:
            print(f"Error en obtener_estadisticas: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== LISTAR CITAS =====
    
    @staticmethod
    async def listar_citas(request: Request):
        """
        Lista citas con filtros
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
            fecha = request.query_params.get('fecha')
            paciente = request.query_params.get('paciente', '')
            terapeuta = request.query_params.get('terapeuta', '')
            estado = request.query_params.get('estado', '')
            fecha_desde = request.query_params.get('fecha_desde')
            fecha_hasta = request.query_params.get('fecha_hasta')
            
            # Preparar filtros
            filtros = {}
            if fecha:
                filtros['fecha'] = fecha
            if paciente:
                filtros['paciente'] = paciente
            if terapeuta:
                filtros['terapeuta'] = terapeuta
            if estado:
                filtros['estado'] = estado
            if fecha_desde:
                filtros['fecha_desde'] = fecha_desde
            if fecha_hasta:
                filtros['fecha_hasta'] = fecha_hasta
            
            # Obtener citas del modelo
            citas = AdminCitaModel.listar_citas(filtros)
            
            return JSONResponse(content={
                "success": True,
                "data": citas,
                "total": len(citas)
            })
                
        except Exception as e:
            print(f"Error en listar_citas: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== OBTENER CITA ESPECÍFICA =====
    
    @staticmethod
    async def obtener_cita(request: Request, cita_id: str):
        """
        Obtiene una cita específica por ID
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Obtener cita del modelo
            cita = AdminCitaModel.obtener_cita_por_id(cita_id)
            
            if not cita:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Cita no encontrada"}
                )
            
            return JSONResponse(content={
                "success": True,
                "data": cita
            })
                
        except Exception as e:
            print(f"Error en obtener_cita: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== CREAR CITA =====
    
    @staticmethod
    async def crear_cita(request: Request):
        """
        Crea una nueva cita
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
            required_fields = ['nombre_paciente', 'servicio', 'terapeuta_designado', 
                             'fecha_cita', 'hora_cita', 'tipo_pago']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Crear cita en el modelo
            success, message, cita_id = AdminCitaModel.crear_cita(body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"cita_id": cita_id}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"Error en crear_cita: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== ACTUALIZAR CITA =====
    
    @staticmethod
    async def actualizar_cita(request: Request, cita_id: str):
        """
        Actualiza una cita existente
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
            required_fields = ['nombre_paciente', 'servicio', 'terapeuta_designado', 
                             'fecha_cita', 'hora_cita', 'tipo_pago']
            for field in required_fields:
                if field not in body or not body[field]:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": f"Campo '{field}' es requerido"}
                    )
            
            # Actualizar cita en el modelo
            success, message = AdminCitaModel.actualizar_cita(cita_id, body)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"cita_id": cita_id}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"Error en actualizar_cita: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== CAMBIAR ESTADO CITA =====
    
    @staticmethod
    async def cambiar_estado_cita(request: Request, cita_id: str):
        """
        Cambia el estado de una cita
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
            
            if 'nuevo_estado' not in body or not body['nuevo_estado']:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Campo 'nuevo_estado' es requerido"}
                )
            
            nuevo_estado = body['nuevo_estado']
            estados_validos = ['Pendiente', 'Confirmada', 'Completada', 'Cancelada']
            
            if nuevo_estado not in estados_validos:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"}
                )
            
            # Cambiar estado en el modelo
            success, message = AdminCitaModel.cambiar_estado_cita(cita_id, nuevo_estado)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message,
                    "data": {"cita_id": cita_id, "nuevo_estado": nuevo_estado}
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"Error en cambiar_estado_cita: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== ELIMINAR CITA =====
    
    @staticmethod
    async def eliminar_cita(request: Request, cita_id: str):
        """
        Elimina una cita
        """
        try:
            # Verificar sesión de administrador
            admin = AuthAdminController.verificar_sesion_admin(request)
            if not admin:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "error": "Acceso no autorizado"}
                )
            
            # Eliminar cita en el modelo
            success, message = AdminCitaModel.eliminar_cita(cita_id)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": message
                })
            else:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": message}
                )
                
        except Exception as e:
            print(f"Error en eliminar_cita: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )
    
    # ===== OBTENER CITAS POR SEMANA =====
    
    @staticmethod
    async def obtener_citas_semana(request: Request):
        """
        Obtiene citas para una semana específica
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
            fecha_inicio = request.query_params.get('fecha_inicio')
            fecha_fin = request.query_params.get('fecha_fin')
            
            if not fecha_inicio or not fecha_fin:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Los parámetros 'fecha_inicio' y 'fecha_fin' son requeridos"}
                )
            
            # Obtener citas del modelo
            citas = AdminCitaModel.obtener_citas_semana(fecha_inicio, fecha_fin)
            
            return JSONResponse(content={
                "success": True,
                "data": citas,
                "total": len(citas)
            })
                
        except Exception as e:
            print(f"Error en obtener_citas_semana: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor"}
            )