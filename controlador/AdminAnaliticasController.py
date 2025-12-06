# controlador/AdminAnaliticasController.py
import datetime
from modelo.AdminAnaliticasModel import AdminAnaliticasModel
from controlador.AuthAdminController import AuthAdminController
from fastapi import Request
from fastapi.responses import JSONResponse

class AdminAnaliticasController:
    
    @staticmethod
    async def obtener_estadisticas(request: Request):
        """
        Endpoint para obtener estadísticas generales
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            estadisticas, error = AdminAnaliticasModel.obtener_estadisticas_generales()
            
            if error:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": error}
                )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": estadisticas
                }
            )
            
        except Exception as e:
            print(f"Error en obtener_estadisticas: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_datos_graficos(request: Request):
        """
        Endpoint para obtener datos para gráficos
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            # Obtener parámetros de filtro
            body = await request.json() if request.method == "POST" else {}
            periodo = body.get('periodo', 'month')
            fecha_desde = body.get('fecha_desde')
            fecha_hasta = body.get('fecha_hasta')
            
            datos_graficos, error = AdminAnaliticasModel.obtener_datos_grafico(
                periodo, fecha_desde, fecha_hasta
            )
            
            if error:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": error}
                )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": datos_graficos
                }
            )
            
        except Exception as e:
            print(f"Error en obtener_datos_graficos: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_servicios_populares(request: Request):
        """
        Endpoint para obtener servicios populares
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            servicios, error = AdminAnaliticasModel.obtener_servicios_populares()
            
            if error:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": error}
                )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": servicios
                }
            )
            
        except Exception as e:
            print(f"Error en obtener_servicios_populares: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_rendimiento_terapeutas(request: Request):
        """
        Endpoint para obtener rendimiento de terapeutas
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            terapeutas, error = AdminAnaliticasModel.obtener_rendimiento_terapeutas()
            
            if error:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": error}
                )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": terapeutas
                }
            )
            
        except Exception as e:
            print(f"Error en obtener_rendimiento_terapeutas: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_datos_financieros(request: Request):
        """
        Endpoint para obtener datos financieros
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            datos_financieros, error = AdminAnaliticasModel.obtener_datos_financieros()
            
            if error:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": error}
                )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": datos_financieros
                }
            )
            
        except Exception as e:
            print(f"Error en obtener_datos_financieros: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_tendencias(request: Request):
        """
        Endpoint para obtener tendencias
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            tendencias, error = AdminAnaliticasModel.obtener_tendencias()
            
            if error:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": error}
                )
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": tendencias
                }
            )
            
        except Exception as e:
            print(f"Error en obtener_tendencias: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
    
    @staticmethod
    async def generar_reporte(request: Request):
        """
        Endpoint para generar reporte
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            # Obtener parámetros
            body = await request.json() if request.method == "POST" else {}
            tipo_reporte = body.get('tipo', 'mensual')
            
            # Obtener todos los datos necesarios para el reporte
            estadisticas, error1 = AdminAnaliticasModel.obtener_estadisticas_generales()
            datos_financieros, error2 = AdminAnaliticasModel.obtener_datos_financieros()
            servicios, error3 = AdminAnaliticasModel.obtener_servicios_populares()
            terapeutas, error4 = AdminAnaliticasModel.obtener_rendimiento_terapeutas()
            tendencias, error5 = AdminAnaliticasModel.obtener_tendencias()
            
            # Verificar errores
            errores = [error1, error2, error3, error4, error5]
            errores_mensajes = [e for e in errores if e]
            
            if errores_mensajes:
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False, 
                        "message": f"Errores al recopilar datos: {', '.join(errores_mensajes)}"
                    }
                )
            
            # Consolidar reporte
            reporte = {
                "estadisticas_generales": estadisticas if estadisticas else {},
                "datos_financieros": datos_financieros if datos_financieros else {},
                "servicios_populares": servicios if servicios else [],
                "rendimiento_terapeutas": terapeutas if terapeutas else [],
                "tendencias": tendencias if tendencias else {},
                "fecha_generacion": datetime.datetime.now().isoformat(),
                "tipo_reporte": tipo_reporte
            }
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Reporte {tipo_reporte} generado exitosamente",
                    "data": reporte
                }
            )
            
        except Exception as e:
            print(f"Error en generar_reporte: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_datos_usuario_paciente(request: Request):
        """
        Endpoint para obtener datos de usuarios vs pacientes
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            conn = AdminAnaliticasModel.get_db_connection()
            if not conn:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": "Error de conexión"}
                )
            
            with conn.cursor() as cursor:
                # Total usuarios
                cursor.execute("SELECT COUNT(*) as total FROM usuario")
                total_usuarios = cursor.fetchone()['total']
                
                # Total pacientes
                cursor.execute("SELECT COUNT(DISTINCT ID_usuario) as total FROM paciente")
                total_pacientes = cursor.fetchone()['total']
                
                # Usuarios que no son pacientes
                usuarios_no_pacientes = total_usuarios - total_pacientes
                
                datos = {
                    'total_usuarios': total_usuarios,
                    'total_pacientes': total_pacientes,
                    'usuarios_no_pacientes': usuarios_no_pacientes,
                    'labels': ['Usuarios', 'Pacientes'],
                    'data': [total_usuarios, total_pacientes]
                }
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "data": datos
                    }
                )
                
        except Exception as e:
            print(f"Error en obtener_datos_usuario_paciente: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
    
    @staticmethod
    async def obtener_productos_servicios_populares(request: Request):
        """
        Endpoint para obtener productos y servicios más vendidos
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            # Esta función usaría datos reales de la BD
            # Por ahora devolvemos datos de ejemplo
            datos = [
                {"nombre": "Masaje Terapéutico", "tipo": "servicio", "ventas": 45, "ingresos": 2250},
                {"nombre": "Rehabilitación Post-operatoria", "tipo": "servicio", "ventas": 32, "ingresos": 2560},
                {"nombre": "Terapia Deportiva", "tipo": "servicio", "ventas": 28, "ingresos": 1960},
                {"nombre": "Proteína Whey", "tipo": "producto", "ventas": 25, "ingresos": 1250},
                {"nombre": "Banda Elástica", "tipo": "producto", "ventas": 18, "ingresos": 540}
            ]
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": datos
                }
            )
            
        except Exception as e:
            print(f"Error en obtener_productos_servicios_populares: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
        
    @staticmethod
    async def obtener_top_terapeutas(request: Request):
        """
        Endpoint para obtener terapeutas top
        """
        admin = AuthAdminController.verificar_sesion_admin(request)
        if not admin:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "No autorizado"}
            )
        
        try:
            # Obtener terapeutas top por citas
            conn = AdminAnaliticasModel.get_db_connection()
            if not conn:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": "Error de conexión"}
                )
            
            with conn.cursor() as cursor:
                mes_actual = datetime.date.today().replace(day=1)
                primer_dia_mes_actual = mes_actual
                ultimo_dia_mes_actual = (mes_actual.replace(month=mes_actual.month % 12 + 1, day=1) - datetime.timedelta(days=1))
                
                query = """
                SELECT 
                    t.nombre_completo as nombre,
                    t.especialidad,
                    COUNT(c.cita_id) as citas_atendidas
                FROM terapeuta t
                LEFT JOIN cita c ON t.nombre_completo = c.terapeuta_designado 
                    AND c.fecha_cita BETWEEN %s AND %s
                WHERE t.estado = 'Activo'
                GROUP BY t.nombre_completo, t.especialidad
                HAVING citas_atendidas > 0
                ORDER BY citas_atendidas DESC
                LIMIT 5
                """
                cursor.execute(query, (primer_dia_mes_actual, ultimo_dia_mes_actual))
                terapeutas = cursor.fetchall()
                
                resultado = []
                for terapeuta in terapeutas:
                    resultado.append({
                        'nombre': terapeuta['nombre'],
                        'especialidad': terapeuta['especialidad'],
                        'citas_atendidas': terapeuta['citas_atendidas']
                    })
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "data": resultado
                    }
                )
                
        except Exception as e:
            print(f"Error en obtener_top_terapeutas: {e}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "Error interno del servidor"}
            )
        
    # Agrega este nuevo método al controlador
@staticmethod
async def obtener_top_terapeutas(request: Request):
    """
    Endpoint específico para obtener top terapeutas
    """
    admin = AuthAdminController.verificar_sesion_admin(request)
    if not admin:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "No autorizado"}
        )
    
    try:
        terapeutas, error = AdminAnaliticasModel.obtener_rendimiento_terapeutas()
        
        if error:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": error}
            )
        
        # Filtrar solo los top 3 por citas atendidas
        top_terapeutas = []
        if terapeutas:
            # Ordenar por citas atendidas
            terapeutas_sorted = sorted(terapeutas, key=lambda x: x.get('citas_atendidas', 0), reverse=True)
            top_terapeutas = terapeutas_sorted[:3]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "top_terapeutas": top_terapeutas,
                    "total_terapeutas": len(terapeutas),
                    "citas_totales": sum(t.get('citas_atendidas', 0) for t in terapeutas)
                }
            }
        )
        
    except Exception as e:
        print(f"Error en obtener_top_terapeutas: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Error interno del servidor"}
        )

# Y actualiza este método existente
@staticmethod
async def obtener_rendimiento_terapeutas(request: Request):
    """
    Endpoint para obtener rendimiento de terapeutas (datos completos)
    """
    admin = AuthAdminController.verificar_sesion_admin(request)
    if not admin:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "No autorizado"}
        )
    
    try:
        terapeutas, error = AdminAnaliticasModel.obtener_rendimiento_terapeutas()
        
        if error:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": error}
            )
        
        # Calcular estadísticas agregadas
        if terapeutas:
            total_citas = sum(t.get('citas_atendidas', 0) for t in terapeutas)
            total_ingresos = sum(t.get('ingresos_generados', 0) for t in terapeutas)
            ocupacion_promedio = sum(t.get('ocupacion', 0) for t in terapeutas) / len(terapeutas)
            
            estadisticas = {
                "total_terapeutas": len(terapeutas),
                "total_citas": total_citas,
                "total_ingresos": round(total_ingresos, 2),
                "ocupacion_promedio": round(ocupacion_promedio, 1),
                "terapeuta_top_citas": max(terapeutas, key=lambda x: x.get('citas_atendidas', 0)) if terapeutas else None,
                "terapeuta_top_ingresos": max(terapeutas, key=lambda x: x.get('ingresos_generados', 0)) if terapeutas else None
            }
        else:
            estadisticas = {}
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "terapeutas": terapeutas,
                    "estadisticas": estadisticas
                }
            }
        )
        
    except Exception as e:
        print(f"Error en obtener_rendimiento_terapeutas: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Error interno del servidor"}
        )