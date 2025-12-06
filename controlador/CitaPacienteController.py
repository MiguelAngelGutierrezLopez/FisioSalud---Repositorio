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
    
    @staticmethod
    async def actualizar_estado_cita(request: Request, cita_id: str, nuevo_estado: str):
        """Actualiza el estado de una cita"""
        print(f"🔍 Iniciando actualizar_estado_cita: {cita_id} -> {nuevo_estado}")
        
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            print("❌ No autorizado - sin sesión válida")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        try:
            print(f"✅ Usuario autorizado: {usuario['email']}")
            
            # Validar que el estado sea válido
            estados_validos = ['pendiente', 'confirmada', 'completada', 'cancelada']
            if nuevo_estado not in estados_validos:
                return JSONResponse({
                    "success": False,
                    "message": f"Estado inválido. Estados válidos: {', '.join(estados_validos)}"
                }, status_code=400)
            
            # Verificar que la cita pertenece al usuario
            cita = CitaPacienteModel.obtener_cita_por_id(cita_id)
            if not cita:
                return JSONResponse({
                    "success": False,
                    "message": "Cita no encontrada"
                }, status_code=404)
            
            if cita['correo'] != usuario['email']:
                return JSONResponse({
                    "success": False,
                    "message": "No autorizado - esta cita no pertenece al usuario"
                }, status_code=403)
            
            # Verificar restricciones para cancelar
            if nuevo_estado == 'cancelada':
                fecha_cita = cita['fecha_cita']
                hora_cita = cita['hora_cita']
                
                # Crear datetime de la cita
                if isinstance(fecha_cita, str):
                    fecha_cita = datetime.strptime(fecha_cita, '%Y-%m-%d').date()
                
                cita_datetime = datetime.combine(fecha_cita, hora_cita if isinstance(hora_cita, time) else datetime.strptime(hora_cita, '%H:%M:%S').time())
                
                # No permitir cancelar citas pasadas
                if cita_datetime < datetime.now():
                    return JSONResponse({
                        "success": False,
                        "message": "No se puede cancelar una cita que ya pasó"
                    })
                
                # Verificar si es menos de 24 horas antes (regla opcional)
                tiempo_restante = cita_datetime - datetime.now()
                if tiempo_restante.total_seconds() < 24 * 3600:
                    # Puedes decidir si permitir o no cancelación con menos de 24 horas
                    print(f"⚠️ Cancelación con menos de 24 horas de anticipación: {tiempo_restante}")
                    # return JSONResponse({
                    #     "success": False,
                    #     "message": "Las cancelaciones deben hacerse con al menos 24 horas de anticipación"
                    # })
            
            # Actualizar el estado
            success, message = CitaPacienteModel.actualizar_estado_cita(cita_id, nuevo_estado)
            
            if success:
                print(f"✅ Estado actualizado exitosamente: {cita_id} -> {nuevo_estado}")
                return JSONResponse({
                    "success": True,
                    "message": message
                })
            else:
                print(f"❌ Error actualizando estado: {message}")
                return JSONResponse({
                    "success": False,
                    "message": message
                }, status_code=500)
                
        except Exception as e:
            print(f"🔥 Error en controlador actualizar_estado_cita: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Error interno del servidor")