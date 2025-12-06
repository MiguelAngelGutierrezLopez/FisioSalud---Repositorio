import pymysql
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, date
import logging

from bd.conexion_bd import get_db_connection

# Configurar logging
logger = logging.getLogger(__name__)

class ReporteFisioModel:
    
    @staticmethod
    def get_db_connection():
        """Obtiene conexión a la base de datos usando la conexión centralizada"""
        try:
            connection = get_db_connection()  # ← Usa la función centralizada
            if connection:
                return connection
            else:
                logger.error("❌ No se pudo obtener conexión a la BD")
                return None
        except Exception as e:
            logger.error(f"❌ Error inesperado en conexión: {e}")
            return None

    @staticmethod
    def convertir_a_serializable(resultado: Dict) -> Dict:
        """Convierte resultados de BD a formato serializable JSON"""
        serializable = {}
        for key, value in resultado.items():
            if value is None:
                serializable[key] = ''
            elif isinstance(value, (date, datetime)):
                serializable[key] = value.isoformat()
            elif isinstance(value, bytes):
                # Para campos binarios, solo guardamos metadatos
                serializable[key] = f"<BLOB: {len(value)} bytes>"
            else:
                serializable[key] = str(value)
        return serializable

    @staticmethod
    def guardar_reporte_paciente(codigo_cita: str, pdf_bytes: bytes, nombre_paciente: str) -> Dict[str, Any]:
        """Guarda el reporte PDF en la tabla paciente - VERSIÓN CORREGIDA"""
        connection = ReporteFisioModel.get_db_connection()
        if not connection:
            return {"success": False, "error": "Sin conexión a BD"}
            
        try:
            # Validaciones
            if not codigo_cita or not codigo_cita.strip():
                return {"success": False, "error": "Código de cita inválido"}
            
            if not pdf_bytes or len(pdf_bytes) < 100:
                return {"success": False, "error": "PDF vacío o muy pequeño"}
            
            # Verificar firma PDF
            if not pdf_bytes.startswith(b'%PDF'):
                logger.warning(f"⚠️ Archivo no tiene firma PDF válida para {codigo_cita}")
            
            with connection.cursor() as cursor:
                # SQL para guardar BLOB
                sql = """
                UPDATE paciente 
                SET reporte = %s, 
                    fecha_creacion_reporte = CURDATE(),
                    nombre_completo = COALESCE(%s, nombre_completo)
                WHERE codigo_cita = %s
                """
                
                logger.info(f"💾 Guardando PDF: {len(pdf_bytes)} bytes para {codigo_cita}")
                
                # Usar pymysql.Binary para datos binarios (CRÍTICO)
                cursor.execute(sql, (
                    pymysql.Binary(pdf_bytes),  # ← ¡ESTO ES CLAVE!
                    nombre_paciente,
                    codigo_cita
                ))
                
                affected = cursor.rowcount
                connection.commit()
                
                if affected > 0:
                    logger.info(f"✅ PDF guardado exitosamente: {codigo_cita}")
                    return {
                        "success": True,
                        "bytes_guardados": len(pdf_bytes),
                        "codigo_cita": codigo_cita,
                        "fecha": date.today().isoformat()
                    }
                else:
                    logger.warning(f"⚠️ No se actualizó ningún registro para {codigo_cita}")
                    return {
                        "success": False, 
                        "error": "No se encontró el paciente o no se actualizó"
                    }
                
        except pymysql.Error as e:
            logger.error(f"❌ Error MySQL al guardar PDF: {e}")
            if connection:
                connection.rollback()
            return {"success": False, "error": f"Error de base de datos: {str(e)}"}
        except Exception as e:
            logger.error(f"❌ Error inesperado al guardar PDF: {e}", exc_info=True)
            if connection:
                connection.rollback()
            return {"success": False, "error": f"Error interno: {str(e)}"}
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass

    @staticmethod
    def obtener_pacientes_por_terapeuta(terapeuta: str) -> List[Dict]:
        """Obtiene pacientes del terapeuta para los filtros"""
        connection = ReporteFisioModel.get_db_connection()
        if not connection:
            return []
            
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT 
                    codigo_cita,
                    nombre_completo,
                    terapeuta_asignado,
                    estado_cita,
                    fecha_creacion_reporte
                FROM paciente 
                WHERE terapeuta_asignado = %s 
                AND estado_cita = 'confirmed'
                ORDER BY nombre_completo
                """
                cursor.execute(sql, (terapeuta,))
                resultados = cursor.fetchall()
                
                pacientes_serializables = []
                for paciente in resultados:
                    pacientes_serializables.append(
                        ReporteFisioModel.convertir_a_serializable(paciente)
                    )
                
                logger.info(f"📋 Encontrados {len(pacientes_serializables)} pacientes para {terapeuta}")
                return pacientes_serializables
                
        except Exception as e:
            logger.error(f"❌ Error al obtener pacientes: {e}", exc_info=True)
            return []
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass

    @staticmethod
    def obtener_reportes_por_terapeuta(terapeuta: str) -> List[Dict]:
        """Obtiene todos los reportes generados por el terapeuta"""
        connection = ReporteFisioModel.get_db_connection()
        if not connection:
            return []
            
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT 
                    codigo_cita,
                    nombre_completo,
                    fecha_creacion_reporte,
                    tipo_plan,
                    estado_cita,
                    reporte IS NOT NULL as tiene_reporte,
                    LENGTH(reporte) as tamaño_bytes
                FROM paciente 
                WHERE terapeuta_asignado = %s 
                AND reporte IS NOT NULL
                ORDER BY fecha_creacion_reporte DESC
                """
                cursor.execute(sql, (terapeuta,))
                resultados = cursor.fetchall()
                
                reportes_serializables = []
                for reporte in resultados:
                    reportes_serializables.append(
                        ReporteFisioModel.convertir_a_serializable(reporte)
                    )
                
                logger.info(f"📄 Encontrados {len(reportes_serializables)} reportes para {terapeuta}")
                return reportes_serializables
                
        except Exception as e:
            logger.error(f"❌ Error al obtener reportes: {e}", exc_info=True)
            return []
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass

    @staticmethod
    def descargar_reporte(codigo_cita: str) -> Optional[Dict]:
        """Obtiene el reporte PDF para descargar - VERSIÓN CORREGIDA"""
        connection = ReporteFisioModel.get_db_connection()
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                sql = """
                SELECT 
                    reporte,
                    nombre_completo,
                    fecha_creacion_reporte
                FROM paciente 
                WHERE codigo_cita = %s 
                AND reporte IS NOT NULL
                """
                cursor.execute(sql, (codigo_cita,))
                resultado = cursor.fetchone()
                
                if resultado and resultado['reporte']:
                    pdf_bytes = resultado['reporte']
                    
                    # Validar que sea bytes
                    if isinstance(pdf_bytes, (bytes, bytearray)):
                        # Verificar firma PDF
                        if pdf_bytes.startswith(b'%PDF'):
                            logger.info(f"✅ PDF válido de {len(pdf_bytes)} bytes para {codigo_cita}")
                        else:
                            logger.warning(f"⚠️ Bytes no tienen firma PDF para {codigo_cita}")
                        
                        return {
                            'pdf_bytes': pdf_bytes,
                            'nombre_paciente': resultado['nombre_completo'] or f"Paciente {codigo_cita}",
                            'fecha_reporte': resultado['fecha_creacion_reporte'].isoformat() 
                                if resultado['fecha_creacion_reporte'] else date.today().isoformat()
                        }
                    else:
                        logger.error(f"❌ Reporte no es binario para {codigo_cita}, tipo: {type(pdf_bytes)}")
                        return None
                else:
                    logger.warning(f"⚠️ No se encontró reporte para {codigo_cita}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ Error al descargar reporte: {e}", exc_info=True)
            return None
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass

    @staticmethod
    def obtener_estadisticas_progreso(terapeuta: str) -> Dict:
        """Obtiene estadísticas para las tarjetas del dashboard"""
        connection = ReporteFisioModel.get_db_connection()
        if not connection:
            return {}
            
        try:
            with connection.cursor() as cursor:
                # 1. Pacientes activos
                sql_pacientes = """
                SELECT COUNT(*) as total 
                FROM paciente 
                WHERE terapeuta_asignado = %s 
                AND estado_cita = 'confirmed'
                """
                cursor.execute(sql_pacientes, (terapeuta,))
                total_pacientes = cursor.fetchone()['total'] or 0
                
                # 2. Evaluaciones este mes
                sql_evaluaciones_mes = """
                SELECT COUNT(DISTINCT codigo_cita) as total 
                FROM paciente 
                WHERE terapeuta_asignado = %s 
                AND fecha_creacion_reporte IS NOT NULL
                AND MONTH(fecha_creacion_reporte) = MONTH(CURDATE())
                AND YEAR(fecha_creacion_reporte) = YEAR(CURDATE())
                """
                cursor.execute(sql_evaluaciones_mes, (terapeuta,))
                evaluaciones_mes = cursor.fetchone()['total'] or 0
                
                # 3. Pacientes con reportes (histórico)
                sql_con_reportes = """
                SELECT COUNT(DISTINCT codigo_cita) as total 
                FROM paciente 
                WHERE terapeuta_asignado = %s 
                AND reporte IS NOT NULL
                """
                cursor.execute(sql_con_reportes, (terapeuta,))
                con_reportes = cursor.fetchone()['total'] or 0
                
                # 4. Alertas (pacientes sin reportes recientes)
                sql_sin_reportes_recientes = """
                SELECT COUNT(*) as total 
                FROM paciente 
                WHERE terapeuta_asignado = %s 
                AND estado_cita = 'confirmed'
                AND (
                    fecha_creacion_reporte IS NULL 
                    OR fecha_creacion_reporte < DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                )
                """
                cursor.execute(sql_sin_reportes_recientes, (terapeuta,))
                alertas = cursor.fetchone()['total'] or 0
                
                # 5. Progreso promedio (porcentaje de pacientes con reporte)
                progreso_promedio = 0
                if total_pacientes > 0:
                    progreso_promedio = round((con_reportes / total_pacientes) * 100, 1)
                
                estadisticas = {
                    'pacientes_seguimiento': total_pacientes,
                    'evaluaciones_mes': evaluaciones_mes,
                    'pacientes_con_reportes': con_reportes,
                    'alertas_activas': alertas,
                    'progreso_promedio': progreso_promedio
                }
                
                logger.info(f"📊 Estadísticas para {terapeuta}: {estadisticas}")
                return estadisticas
                
        except Exception as e:
            logger.error(f"❌ Error al obtener estadísticas: {e}", exc_info=True)
            return {
                'pacientes_seguimiento': 0,
                'evaluaciones_mes': 0,
                'pacientes_con_reportes': 0,
                'alertas_activas': 0,
                'progreso_promedio': 0
            }
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass

    @staticmethod
    def verificar_estructura_tabla():
        """Verifica que la tabla tenga la estructura correcta"""
        connection = ReporteFisioModel.get_db_connection()
        if not connection:
            return {"error": "Sin conexión"}
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = 'fisiosalud-2' 
                    AND TABLE_NAME = 'paciente'
                    AND COLUMN_NAME = 'reporte'
                """)
                resultado = cursor.fetchone()
                
                if resultado:
                    logger.info(f"🔍 Estructura campo 'reporte': {resultado}")
                    return {
                        "column_name": resultado['COLUMN_NAME'],
                        "data_type": resultado['DATA_TYPE'],
                        "column_type": resultado['COLUMN_TYPE'],
                        "es_blob": resultado['DATA_TYPE'].upper() in ['BLOB', 'LONGBLOB', 'MEDIUMBLOB', 'TINYBLOB']
                    }
                return {"error": "Campo 'reporte' no encontrado"}
                
        except Exception as e:
            logger.error(f"Error verificando estructura: {e}")
            return {"error": str(e)}
        finally:
            if connection:
                try:
                    connection.close()
                except:
                    pass