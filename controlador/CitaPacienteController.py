# controlador/CitaPacienteController.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from modelo.CitaPacienteModel import CitaPacienteModel
from controlador.AuthController import AuthController
from datetime import datetime, date, time, timedelta
import traceback

class CitaPacienteController:
    
    @staticmethod
    def serializar_cita(cita):
        """Convierte objetos date/datetime/timedelta a strings para JSON"""
        if not cita:
            return cita
            
        cita_serializada = dict(cita)
        
        # Convertir todos los campos problemáticos
        for key, value in cita_serializada.items():
            if isinstance(value, (date, datetime)):
                cita_serializada[key] = value.isoformat()
            elif isinstance(value, time):
                cita_serializada[key] = value.strftime('%H:%M:%S')
            elif isinstance(value, timedelta):
                # Convertir timedelta a string (horas:minutos:segundos)
                total_seconds = int(value.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                cita_serializada[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            elif isinstance(value, (int, float)) and key in ['total_citas', 'completadas', 'pendientes', 'confirmadas', 'canceladas']:
                # Asegurar que los números sean integers
                cita_serializada[key] = int(value)
        
        return cita_serializada
    
    @staticmethod
    async def obtener_citas_paciente(request: Request):
        """Obtiene todas las citas del paciente logueado"""
        print("🔍 Iniciando obtener_citas_paciente...")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']}")
            
            citas = CitaPacienteModel.obtener_citas_por_paciente(usuario['email'])
            print(f"📊 Citas encontradas: {len(citas)}")
            
            # Debug: mostrar tipos de datos problemáticos
            if citas:
                print("🔍 Analizando tipos de datos en citas...")
                primera_cita = citas[0]
                for key, value in primera_cita.items():
                    print(f"   {key}: {type(value)} = {value}")
            
            # Serializar todas las citas
            citas_serializadas = [CitaPacienteController.serializar_cita(cita) for cita in citas]
            
            return JSONResponse({
                "success": True,
                "citas": citas_serializadas
            })
        except Exception as e:
            print(f"🔥 Error en controlador obtener_citas_paciente: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    @staticmethod
    async def obtener_citas_proximas(request: Request):
        """Obtiene citas próximas del paciente"""
        print("🔍 Iniciando obtener_citas_proximas...")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']}")
            
            citas = CitaPacienteModel.obtener_citas_proximas(usuario['email'])
            print(f"📊 Citas próximas encontradas: {len(citas)}")
            
            # Serializar todas las citas
            citas_serializadas = [CitaPacienteController.serializar_cita(cita) for cita in citas]
            
            return JSONResponse({
                "success": True,
                "citas": citas_serializadas
            })
        except Exception as e:
            print(f"🔥 Error en controlador obtener_citas_proximas: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    @staticmethod
    async def obtener_estadisticas(request: Request):
        """Obtiene estadísticas del paciente"""
        print("🔍 Iniciando obtener_estadisticas...")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']}")
            
            estadisticas = CitaPacienteModel.obtener_estadisticas_paciente(usuario['email'])
            print(f"📊 Estadísticas encontradas: {estadisticas}")
            
            # Debug: mostrar tipos de datos en estadísticas
            if estadisticas:
                print("🔍 Analizando tipos de datos en estadísticas...")
                for key, value in estadisticas.items():
                    print(f"   {key}: {type(value)} = {value}")
            
            # Serializar estadísticas
            if estadisticas:
                stats_dict = dict(estadisticas)
                
                # Convertir todos los campos problemáticos
                for key, value in stats_dict.items():
                    if isinstance(value, (date, datetime)):
                        stats_dict[key] = value.isoformat()
                    elif isinstance(value, timedelta):
                        # Convertir timedelta a string
                        total_seconds = int(value.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        stats_dict[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    elif isinstance(value, (int, float)):
                        # Asegurar que los números sean integers
                        stats_dict[key] = int(value) if value is not None else 0
            else:
                stats_dict = {
                    'total_citas': 0,
                    'completadas': 0,
                    'pendientes': 0,
                    'confirmadas': 0,
                    'canceladas': 0,
                    'primera_cita': None,
                    'ultima_cita': None
                }
            
            print(f"📊 Estadísticas serializadas: {stats_dict}")
            
            return JSONResponse({
                "success": True,
                "estadisticas": stats_dict
            })
        except Exception as e:
            print(f"🔥 Error en controlador obtener_estadisticas: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")
    
    @staticmethod
    async def obtener_cita_por_id(request: Request, cita_id: str):
        """Obtiene una cita específica por ID"""
        print(f"🔍 Iniciando obtener_cita_por_id: {cita_id}")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']}")
            
            cita = CitaPacienteModel.obtener_cita_por_id(cita_id)
            if not cita or cita['correo'] != usuario['email']:
                return JSONResponse({
                    "success": False,
                    "message": "Cita no encontrada o no autorizada"
                })
            
            # Serializar la cita
            cita_serializada = CitaPacienteController.serializar_cita(cita)
            
            return JSONResponse({
                "success": True,
                "cita": cita_serializada
            })
        except Exception as e:
            print(f"🔥 Error en controlador obtener_cita_por_id: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")