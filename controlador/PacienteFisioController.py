from fastapi import Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from modelo.PacienteFisioModel import PacienteFisioModel
from typing import Optional, List
import traceback
import json


class PacienteFisioController:
    
    @staticmethod
    async def obtener_pacientes(request: Request):
        """API endpoint para obtener los pacientes confirmados del terapeuta logueado"""
        try:
            # OBTENER EL FISIOTERAPEUTA DE LA SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            # Obtener el nombre del terapeuta de la sesión
            terapeuta_actual = fisioterapeuta.get('nombre_completo')
            print(f"🔍 Buscando pacientes confirmados para el terapeuta: {terapeuta_actual}")
            
            pacientes = PacienteFisioModel.obtener_pacientes_por_terapeuta(terapeuta_actual)
            print(f"Pacientes confirmados obtenidos para {terapeuta_actual}: {len(pacientes)}")
            
            return JSONResponse(content={
                "success": True,
                "data": pacientes,
                "total": len(pacientes)
            })
            
        except Exception as e:
            print(f"Error en API de pacientes: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Error al obtener pacientes: {str(e)}",
                    "data": []
                }
            )

    @staticmethod
    async def obtener_ejercicios(request: Request):
        """API endpoint para obtener todos los ejercicios disponibles"""
        try:
            ejercicios = PacienteFisioModel.obtener_ejercicios_disponibles()
            
            return JSONResponse(content={
                "success": True,
                "data": ejercicios,
                "total": len(ejercicios)
            })
            
        except Exception as e:
            print(f"Error en API de ejercicios: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Error al obtener ejercicios: {str(e)}",
                    "data": []
                }
            )

    @staticmethod
    async def asignar_ejercicios(
        request: Request,
        codigo_cita: str = Form(...),
        ejercicios_seleccionados: List[str] = Form(...)
    ):
        """API endpoint para asignar ejercicios a un paciente"""
        try:
            # VERIFICAR SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            print(f"📥 Asignando ejercicios al paciente: {codigo_cita}")
            print(f"📋 Ejercicios seleccionados: {ejercicios_seleccionados}")
            
            # Actualizar ejercicios del paciente
            actualizado = PacienteFisioModel.actualizar_ejercicios_paciente(codigo_cita, ejercicios_seleccionados)
            
            if actualizado:
                print("✅ Ejercicios asignados exitosamente")
                return JSONResponse(
                    content={
                        "success": True,
                        "message": "Ejercicios asignados exitosamente",
                        "data": {
                            "codigo_cita": codigo_cita,
                            "ejercicios": ejercicios_seleccionados
                        }
                    }
                )
            else:
                print("❌ Error al asignar ejercicios en el modelo")
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": "Error al asignar los ejercicios en la base de datos"
                    }
                )
            
        except Exception as e:
            print(f"❌ Error al asignar ejercicios: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Error interno del servidor: {str(e)}"
                }
            )

    @staticmethod
    async def obtener_ejercicios_paciente(request: Request, codigo_cita: str):
        """API endpoint para obtener los ejercicios de un paciente específico"""
        try:
            # VERIFICAR SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            ejercicios = PacienteFisioModel.obtener_ejercicios_paciente(codigo_cita)
            
            return JSONResponse(content={
                "success": True,
                "data": ejercicios
            })
            
        except Exception as e:
            print(f"Error al obtener ejercicios del paciente: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Error interno del servidor"
                }
            )

    @staticmethod
    async def eliminar_paciente(request: Request, codigo_cita: str):
        """API endpoint para eliminar un paciente"""
        try:
            # VERIFICAR SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            eliminado = PacienteFisioModel.eliminar_paciente(codigo_cita)
            
            if eliminado:
                return JSONResponse(
                    content={
                        "success": True,
                        "message": "Paciente eliminado exitosamente"
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": "Error al eliminar el paciente"
                    }
                )
            
        except Exception as e:
            print(f"Error al eliminar paciente: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Error interno del servidor"
                }
            )

    @staticmethod
    async def obtener_estadisticas_pacientes(request: Request):
        """API endpoint para obtener estadísticas de pacientes"""
        try:
            # OBTENER EL FISIOTERAPEUTA DE LA SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            # Obtener el nombre del terapeuta de la sesión
            terapeuta_actual = fisioterapeuta.get('nombre_completo')
            
            estadisticas = PacienteFisioModel.obtener_estadisticas_pacientes(terapeuta_actual)
            
            return JSONResponse(content={
                "success": True,
                "data": estadisticas
            })
            
        except Exception as e:
            print(f"Error en API de estadísticas: {e}")
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Error al obtener estadísticas: {str(e)}"
                }
            )