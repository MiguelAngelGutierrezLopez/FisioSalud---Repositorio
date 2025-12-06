from datetime import datetime
from fastapi import Request, Form, UploadFile, status
from fastapi.params import File
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from modelo.ReporteFisioModel import ReporteFisioModel
from typing import Dict, Any, Optional
import logging
import traceback

# Configurar logging
logger = logging.getLogger(__name__)

class ReporteFisioController:
    
    @staticmethod
    async def obtener_pacientes_para_filtros(request: Request):
        """API endpoint para obtener pacientes del terapeuta para filtros"""
        try:
            # OBTENER EL FISIOTERAPEUTA DE LA SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                logger.warning("❌ Intento de acceso no autorizado a pacientes-filtros")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            # Obtener el nombre del terapeuta de la sesión
            terapeuta_actual = fisioterapeuta.get('nombre_completo')
            logger.info(f"🔍 Buscando pacientes para filtros del terapeuta: {terapeuta_actual}")
            
            pacientes = ReporteFisioModel.obtener_pacientes_por_terapeuta(terapeuta_actual)
            
            return JSONResponse(
                content=jsonable_encoder({
                    "success": True,
                    "data": pacientes,
                    "total": len(pacientes),
                    "terapeuta": terapeuta_actual
                })
            )
            
        except Exception as e:
            logger.error(f"❌ Error en API de pacientes para filtros: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": f"Error al obtener pacientes: {str(e)}",
                    "data": []
                }
            )

    @staticmethod
    async def guardar_reporte(
        request: Request,
        ID: str = Form(...),
        reporte: UploadFile = File(...)
    ):
        """API endpoint para guardar reporte PDF en la base de datos - VERSIÓN CORREGIDA"""
        try:
            # VERIFICAR SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                logger.warning("❌ Intento de guardar reporte sin sesión")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            # Validar ID
            if not ID or not ID.strip():
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "error": "ID de paciente inválido"
                    }
                )
            
            # Validar archivo
            if not reporte:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "error": "No se envió archivo PDF"
                    }
                )
            
            # Verificar tipo MIME
            content_type = reporte.content_type or ""
            if content_type != "application/pdf":
                logger.warning(f"⚠️ Archivo no es PDF: {content_type}")
                # Podemos ser permisivos y solo advertir
            
            # Leer contenido
            pdf_bytes = await reporte.read()
            file_size = len(pdf_bytes)
            
            logger.info(f"📥 Guardando reporte para {ID}: {file_size} bytes, tipo: {content_type}")
            
            # Validar tamaño
            if file_size > 10 * 1024 * 1024:  # 10MB máximo
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "error": "PDF demasiado grande (máximo 10MB)"
                    }
                )
            
            if file_size < 100:  # Mínimo 100 bytes
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "success": False,
                        "error": "PDF vacío o muy pequeño"
                    }
                )
            
            # Obtener nombre del terapeuta
            terapeuta_actual = fisioterapeuta.get('nombre_completo')
            
            # Por ahora nombre genérico, podrías obtenerlo de la BD
            nombre_paciente = f"Paciente {ID}"
            
            # Guardar usando el modelo corregido
            resultado = ReporteFisioModel.guardar_reporte_paciente(ID, pdf_bytes, nombre_paciente)
            
            if resultado.get("success"):
                logger.info(f"✅ Reporte guardado exitosamente para {ID}")
                return JSONResponse(
                    content=jsonable_encoder({
                        "success": True,
                        "message": "Reporte guardado exitosamente",
                        "data": resultado
                    })
                )
            else:
                logger.error(f"❌ Error al guardar reporte: {resultado.get('error')}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "success": False,
                        "error": resultado.get("error", "Error desconocido al guardar")
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ Error al guardar reporte: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": f"Error interno del servidor: {str(e)}"
                }
            )

    @staticmethod
    async def obtener_reportes(request: Request):
        """API endpoint para obtener todos los reportes del terapeuta"""
        try:
            # OBTENER EL FISIOTERAPEUTA DE LA SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                logger.warning("❌ Intento de obtener reportes sin sesión")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            # Obtener el nombre del terapeuta de la sesión
            terapeuta_actual = fisioterapeuta.get('nombre_completo')
            logger.info(f"🔍 Buscando reportes del terapeuta: {terapeuta_actual}")
            
            reportes = ReporteFisioModel.obtener_reportes_por_terapeuta(terapeuta_actual)
            
            return JSONResponse(
                content=jsonable_encoder({
                    "success": True,
                    "data": reportes,
                    "total": len(reportes),
                    "terapeuta": terapeuta_actual
                })
            )
            
        except Exception as e:
            logger.error(f"❌ Error en API de reportes: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": f"Error al obtener reportes: {str(e)}",
                    "data": []
                }
            )

    @staticmethod
    async def descargar_reporte(request: Request, codigo_cita: str):
        """API endpoint para descargar un reporte específico - VERSIÓN CORREGIDA"""
        try:
            # VERIFICAR SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                logger.warning(f"❌ Intento de descargar reporte {codigo_cita} sin sesión")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            logger.info(f"📥 Solicitando descarga de reporte: {codigo_cita}")
            
            resultado = ReporteFisioModel.descargar_reporte(codigo_cita)
            
            if not resultado:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "success": False,
                        "error": "Reporte no encontrado"
                    }
                )
            
            pdf_bytes = resultado['pdf_bytes']
            
            # Validar que sea PDF
            if not pdf_bytes.startswith(b'%PDF'):
                logger.error(f"❌ Bytes no son un PDF válido para {codigo_cita}")
                # Aún así lo devolvemos, pero advertimos
            
            nombre_paciente = resultado['nombre_paciente'].replace(' ', '_')
            filename = f"reporte_{nombre_paciente}_{codigo_cita}.pdf"
            
            logger.info(f"✅ Enviando PDF: {len(pdf_bytes)} bytes como {filename}")
            
            # Devolver el PDF como respuesta
            return Response(
                content=pdf_bytes,
                media_type='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Length': str(len(pdf_bytes)),
                    'Content-Type': 'application/pdf',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error al descargar reporte {codigo_cita}: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "Error interno del servidor"
                }
            )

    @staticmethod
    async def obtener_estadisticas_progreso(request: Request):
        """API endpoint para obtener estadísticas del dashboard"""
        try:
            # OBTENER EL FISIOTERAPEUTA DE LA SESIÓN
            fisioterapeuta = request.session.get('fisioterapeuta')
            
            if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
                logger.warning("❌ Intento de obtener estadísticas sin sesión")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "success": False,
                        "error": "No autorizado - Inicie sesión primero"
                    }
                )
            
            # Obtener el nombre del terapeuta de la sesión
            terapeuta_actual = fisioterapeuta.get('nombre_completo')
            logger.info(f"📊 Obteniendo estadísticas para: {terapeuta_actual}")
            
            estadisticas = ReporteFisioModel.obtener_estadisticas_progreso(terapeuta_actual)
            
            return JSONResponse(
                content=jsonable_encoder({
                    "success": True,
                    "data": estadisticas,
                    "terapeuta": terapeuta_actual,
                    "timestamp": datetime.now().isoformat()
                })
            )
            
        except Exception as e:
            logger.error(f"❌ Error en API de estadísticas: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": f"Error al obtener estadísticas: {str(e)}"
                }
            )

    @staticmethod
    async def verificar_estructura(request: Request):
        """Endpoint para verificar la estructura de la tabla (debug)"""
        try:
            resultado = ReporteFisioModel.verificar_estructura_tabla()
            return JSONResponse(content=resultado)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )