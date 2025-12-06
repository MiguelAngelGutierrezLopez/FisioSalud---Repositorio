from fastapi import Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from modelo import EmailModel
from modelo.EmailModel import EmailModel
from modelo.CitaModel import CitaModel
from typing import Optional
import json
from datetime import datetime

class CitaController:
    
    @staticmethod
    async def mostrar_formulario_cita(request: Request, servicio_codigo: Optional[str] = None):
        """Muestra el formulario para agendar citas de terapia"""
        try:
            servicios = CitaModel.obtener_servicios_terapia()
            
            # Si viene un código de servicio, buscar ese servicio específico
            servicio_seleccionado = None
            if servicio_codigo:
                servicio_seleccionado = next(
                    (s for s in servicios if s['codigo'] == servicio_codigo), 
                    None
                )
            
            from fastapi.templating import Jinja2Templates
            templates = Jinja2Templates(directory="./vista")
            
            return templates.TemplateResponse(
                "cita.html",
                {
                    "request": request,
                    "servicios": servicios,
                    "servicio_seleccionado": servicio_seleccionado
                }
            )
        except Exception as e:
            print(f"Error al mostrar formulario de cita: {e}")
            raise HTTPException(status_code=500, detail="Error interno del servidor")

    @staticmethod
    async def obtener_servicios_api(request: Request):
        """API endpoint para obtener servicios de terapia (serializable a JSON)"""
        try:
            servicios = CitaModel.obtener_servicios_terapia()
            
            # Formatear para JSON serializable
            servicios_formateados = []
            for servicio in servicios:
                servicio_formateado = {
                    'codigo': servicio.get('codigo', ''),
                    'nombre': servicio.get('nombre', ''),
                    'descripcion': servicio.get('descripcion', ''),
                    'terapeuta_disponible': servicio.get('terapeuta_disponible', ''),
                    'inicio_jornada': servicio.get('inicio_jornada', ''),
                    'final_jornada': servicio.get('final_jornada', ''),
                    'duracion': servicio.get('duracion', ''),
                    'modalidad': servicio.get('modalidad', ''),
                    'precio': float(servicio.get('precio', 0)),  # Asegurar float
                    'beneficios': servicio.get('beneficios', ''),
                    'recomendacion_precita': servicio.get('recomendacion_precita', ''),
                    'condiciones_tratar': servicio.get('condiciones_tratar', ''),
                    'requisitos': servicio.get('requisitos', ''),
                    'consideraciones': servicio.get('consideraciones', '')
                }
                servicios_formateados.append(servicio_formateado)
            
            return JSONResponse(content={"servicios": servicios_formateados})
            
        except Exception as e:
            print(f"Error en API de servicios: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"error": "Error al obtener servicios", "detalle": str(e)}
            )

    @staticmethod
    async def agendar_cita(
        request: Request,
        servicio: str = Form(...),
        terapeuta_designado: str = Form(...),
        nombre_paciente: str = Form(...),
        telefono: str = Form(...),
        correo: str = Form(...),
        fecha_cita: str = Form(...),
        hora_cita: str = Form(...),
        tipo_pago: str = Form(...),
        notas_adicionales: Optional[str] = Form(None),
        acudiente_nombre: Optional[str] = Form(None),
        acudiente_id: Optional[str] = Form(None),
        acudiente_telefono: Optional[str] = Form(None),
        acudiente_correo: Optional[str] = Form(None),
        emails_adicionales: Optional[str] = Form(None)
    ):
        """Procesa el agendamiento de una nueva cita por usuario"""
        try:
            print(f"Iniciando agendamiento para usuario: {nombre_paciente}")
            
            # Validaciones básicas
            if not all([servicio, terapeuta_designado, nombre_paciente, telefono, correo, fecha_cita, hora_cita, tipo_pago]):
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Todos los campos obligatorios deben ser completados"}
                )

            # Validar fecha
            try:
                fecha_obj = datetime.strptime(fecha_cita, '%Y-%m-%d')
                if fecha_obj.date() < datetime.now().date():
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "error": "No se pueden agendar citas en fechas pasadas"}
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Formato de fecha inválido"}
                )

            # 1. VERIFICAR DISPONIBILIDAD
            disponible = CitaModel.verificar_disponibilidad_cita(
                fecha_cita, hora_cita, terapeuta_designado
            )
            
            if not disponible:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "El horario seleccionado no está disponible para este terapeuta"}
                )
            
            # 2. OBTENER INFORMACIÓN COMPLETA DEL SERVICIO
            servicios = CitaModel.obtener_servicios_terapia()
            servicio_info = next((s for s in servicios if s['nombre'] == servicio), None)
            
            if not servicio_info:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "error": "Servicio no encontrado"}
                )
            
            # 3. CREAR LA CITA
            datos_cita = {
                'servicio': servicio,
                'terapeuta_designado': terapeuta_designado,
                'nombre_paciente': nombre_paciente,
                'telefono': telefono,
                'correo': correo,
                'fecha_cita': fecha_cita,
                'hora_cita': hora_cita,
                'notas_adicionales': notas_adicionales or '',
                'tipo_pago': tipo_pago
            }
            
            # Usar tipo_usuario = 'usuario' para autogestión
            codigo_cita = CitaModel.crear_cita(datos_cita, tipo_usuario='usuario')
            
            if not codigo_cita:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": "Error al crear la cita en el sistema"}
                )
            
            # 4. CREAR ACUDIENTE SI EXISTE
            acudiente_creado = False
            if acudiente_nombre and acudiente_id:
                datos_acudiente = {
                    'nombre_completo': acudiente_nombre,
                    'identificacion': acudiente_id,
                    'telefono': acudiente_telefono or '',
                    'correo': acudiente_correo or ''
                }
                
                acudiente_creado = CitaModel.crear_acudiente(codigo_cita, datos_acudiente)
                if not acudiente_creado:
                    print(f"Advertencia: No se pudo crear el acudiente para la cita {codigo_cita}")
            
            # 5. PROCESAR EMAILS ADICIONALES PARA ENVÍO
            emails_list = [correo]  # Siempre enviar al email principal
            
            if emails_adicionales:
                try:
                    emails_data = json.loads(emails_adicionales)
                    if isinstance(emails_data, list):
                        emails_list.extend([email for email in emails_data if email.strip()])
                except json.JSONDecodeError:
                    # Si no es JSON válido, tratar como string simple
                    if emails_adicionales.strip():
                        emails_list.append(emails_adicionales.strip())
            
            # Agregar email del acudiente si existe
            if acudiente_correo and acudiente_correo.strip():
                emails_list.append(acudiente_correo.strip())
            
            # Eliminar duplicados
            emails_list = list(set([e for e in emails_list if e]))
            
            # 6. ENVIAR CORREOS DE CONFIRMACIÓN
            resultados_envio = []
            if emails_list and len(emails_list) > 0:
                print(f"Preparando envío de correos a: {emails_list}")
                
                # Preparar datos para el correo
                datos_correo = {
                    'codigo_cita': codigo_cita,
                    'nombre_paciente': nombre_paciente,
                    'servicio': servicio,
                    'terapeuta_designado': terapeuta_designado,
                    'fecha_cita': fecha_cita,
                    'hora_cita': hora_cita,
                    'precio': servicio_info.get('precio', 'Consultar'),
                    'modalidad': servicio_info.get('modalidad', 'Presencial'),
                    'notas_adicionales': notas_adicionales or 'Ninguna',
                    'tipo_pago': tipo_pago,
                    'recomendaciones_precita': servicio_info.get('recomendacion_precita', '')
                }
                
                # Enviar correos usando EmailModel
                try:
                    resultado = EmailModel.enviar_correo_confirmacion_cita(datos_correo, emails_list)
                    resultados_envio = resultado.get('detalles', [])
                    print(f"Resultado envío correos: {resultado}")
                except Exception as email_error:
                    print(f"Error enviando correos: {email_error}")
                    resultados_envio = [{"email": email, "estado": "error", "error": str(email_error)} for email in emails_list]
            else:
                print("No hay emails para enviar")
            
            # 7. RESPUESTA EXITOSA
            response_data = {
                "success": True,
                "message": "Cita agendada exitosamente",
                "codigo_cita": codigo_cita,
                "tipo_usuario": "usuario",
                "cita": {
                    "servicio": servicio,
                    "terapeuta_designado": terapeuta_designado,
                    "fecha_cita": fecha_cita,
                    "hora_cita": hora_cita,
                    "nombre_paciente": nombre_paciente,
                    "precio": servicio_info.get('precio', 'Consultar'),
                    "modalidad": servicio_info.get('modalidad', 'Presencial')
                },
                "acudiente_creado": acudiente_creado,
                "correos_enviados": {
                    "total": len([r for r in resultados_envio if isinstance(r, dict) and r.get("estado") == "enviado"]),
                    "detalles": resultados_envio
                }
            }
            
            print(f"Cita agendada exitosamente por usuario: {codigo_cita}")
            print(f"Correos a enviar: {emails_list}")
            
            return JSONResponse(content=response_data)
            
        except Exception as e:
            print(f"Error al agendar cita: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error interno del servidor al procesar la cita"}
            )
    
    