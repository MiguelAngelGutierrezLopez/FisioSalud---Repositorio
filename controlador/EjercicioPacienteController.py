# controlador/EjercicioPacienteController.py
import json
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from bd.conexion_bd import close_db_connection, get_db_connection
from modelo.EjercicioPacienteModel import EjercicioPacienteModel
from controlador.AuthController import AuthController
from datetime import datetime, date, time, timedelta
import traceback

class EjercicioPacienteController:
    
    @staticmethod
    def serializar_ejercicio(ejercicio):
        """Convierte objetos date/datetime/timedelta a strings para JSON"""
        if not ejercicio:
            return ejercicio
            
        ejercicio_serializado = dict(ejercicio)
        
        # Convertir todos los campos problemáticos
        for key, value in ejercicio_serializado.items():
            if isinstance(value, (date, datetime)):
                ejercicio_serializado[key] = value.isoformat()
            elif isinstance(value, time):
                ejercicio_serializado[key] = value.strftime('%H:%M:%S')
            elif isinstance(value, timedelta):
                # Convertir timedelta a string
                total_seconds = int(value.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                ejercicio_serializado[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            elif key == 'duracion (minutos)':
                # Manejar específicamente la duración
                if isinstance(value, time):
                    ejercicio_serializado['duracion_minutos'] = f"{value.hour:02d}:{value.minute:02d}"
                elif isinstance(value, str):
                    ejercicio_serializado['duracion_minutos'] = value
        
        return ejercicio_serializado
    
    @staticmethod
    async def obtener_ejercicios_paciente(request: Request):
        """Obtiene todos los ejercicios del paciente logueado"""
        print("🔍 Iniciando obtener_ejercicios_paciente...")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']} - ID: {usuario['id']}")
            
            ejercicios = EjercicioPacienteModel.obtener_ejercicios_por_paciente(usuario['id'])
            print(f"💪 Ejercicios encontrados: {len(ejercicios)}")
            
            # Serializar todos los ejercicios
            ejercicios_serializados = [EjercicioPacienteController.serializar_ejercicio(ej) for ej in ejercicios]
            
            return JSONResponse({
                "success": True,
                "ejercicios": ejercicios_serializados
            })
        except Exception as e:
            print(f"🔥 Error en controlador obtener_ejercicios_paciente: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    @staticmethod
    async def obtener_ejercicios_completados(request: Request):
        """Obtiene ejercicios completados del paciente"""
        print("🔍 Iniciando obtener_ejercicios_completados...")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']} - ID: {usuario['id']}")
            
            ejercicios = EjercicioPacienteModel.obtener_ejercicios_completados(usuario['id'])
            print(f"✅ Ejercicios completados encontrados: {len(ejercicios)}")
            
            # Serializar todos los ejercicios
            ejercicios_serializados = [EjercicioPacienteController.serializar_ejercicio(ej) for ej in ejercicios]
            
            return JSONResponse({
                "success": True,
                "ejercicios": ejercicios_serializados
            })
        except Exception as e:
            print(f"🔥 Error en controlador obtener_ejercicios_completados: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    @staticmethod
    async def obtener_ejercicios_pendientes(request: Request):
        """Obtiene ejercicios pendientes del paciente"""
        print("🔍 Iniciando obtener_ejercicios_pendientes...")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']} - ID: {usuario['id']}")
            
            ejercicios = EjercicioPacienteModel.obtener_ejercicios_pendientes(usuario['id'])
            print(f"⏳ Ejercicios pendientes encontrados: {len(ejercicios)}")
            
            # Serializar todos los ejercicios
            ejercicios_serializados = [EjercicioPacienteController.serializar_ejercicio(ej) for ej in ejercicios]
            
            return JSONResponse({
                "success": True,
                "ejercicios": ejercicios_serializados
            })
        except Exception as e:
            print(f"🔥 Error en controlador obtener_ejercicios_pendientes: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    @staticmethod
    async def obtener_estadisticas(request: Request):
        """Obtiene estadísticas de ejercicios del paciente"""
        print("🔍 Iniciando obtener_estadisticas_ejercicios...")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']} - ID: {usuario['id']}")
            
            estadisticas = EjercicioPacienteModel.obtener_estadisticas_ejercicios(usuario['id'])
            print(f"📊 Estadísticas de ejercicios: {estadisticas}")
            
            return JSONResponse({
                "success": True,
                "estadisticas": estadisticas
            })
        except Exception as e:
            print(f"🔥 Error en controlador obtener_estadisticas_ejercicios: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    @staticmethod
    async def marcar_como_completado(request: Request):
        """Marca un ejercicio como completado - VERSIÓN CORREGIDA"""
        print("🔍 Iniciando marcar_como_completado...")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            # ✅ CORRECCIÓN: Leer el cuerpo de la solicitud correctamente
            body = await request.body()
            if not body:
                return JSONResponse({
                    "success": False,
                    "message": "Cuerpo de solicitud vacío"
                })
            
            data = json.loads(body.decode('utf-8'))
            codigo_ejercicio = data.get('codigo_ejercicio')
            feedback = data.get('feedback', '')
            nivel_dificultad = data.get('nivel_dificultad', '')
            
            print(f"🔍 Datos recibidos: {data}")
            
            if not codigo_ejercicio:
                return JSONResponse({
                    "success": False,
                    "message": "Código de ejercicio requerido"
                })
            
            print(f"✅ Marcando ejercicio {codigo_ejercicio} como completado...")
            
            success, message = EjercicioPacienteModel.marcar_como_completado(
                usuario['id'], codigo_ejercicio, feedback, nivel_dificultad
            )
            
            return JSONResponse({
                "success": success,
                "message": message
            })
            
        except json.JSONDecodeError as e:
            print(f"❌ Error decodificando JSON: {e}")
            return JSONResponse({
                "success": False,
                "message": "Formato JSON inválido"
            })  
        except Exception as e:
            print(f"🔥 Error en controlador marcar_como_completado: {e}")
            print(traceback.format_exc())
            return JSONResponse({
                "success": False,
                "message": "Error interno del servidor"
            })
        
    @staticmethod
    async def obtener_ejercicio_por_codigo(request: Request, codigo_ejercicio: str):
        """Obtiene un ejercicio específico por su código"""
        print(f"🔍 Iniciando obtener_ejercicio_por_codigo: {codigo_ejercicio}")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']}")
            
            ejercicio = EjercicioPacienteModel.obtener_ejercicio_por_codigo(codigo_ejercicio)
            if not ejercicio:
                return JSONResponse({
                    "success": False,
                    "message": "Ejercicio no encontrado"
                })
            
            # Verificar que el ejercicio esté asignado al paciente
            ejercicios_asignados = EjercicioPacienteModel.obtener_ejercicios_por_paciente(usuario['id'])
            codigos_asignados = [ej['codigo_ejercicio'] for ej in ejercicios_asignados]
            
            if codigo_ejercicio not in codigos_asignados:
                return JSONResponse({
                    "success": False,
                    "message": "Ejercicio no asignado a este paciente"
                })
            
            # Serializar el ejercicio
            ejercicio_serializado = EjercicioPacienteController.serializar_ejercicio(ejercicio)
            
            return JSONResponse({
                "success": True,
                "ejercicio": ejercicio_serializado
            })
        except Exception as e:
            print(f"🔥 Error en controlador obtener_ejercicio_por_codigo: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")