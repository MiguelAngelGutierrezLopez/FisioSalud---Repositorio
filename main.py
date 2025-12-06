from datetime import datetime
from http.client import HTTPException
from fastapi import APIRouter, FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bd.conexion_bd import close_db_connection, get_db_connection
from controlador import  AdminServicioController, CarritoController, CitaPacienteController, ReporteFisioController
from controlador.AdminAnaliticasController import AdminAnaliticasController
from controlador.AdminFisioController import AdminFisioController
from controlador.AuthFisioController import AuthFisioController
from controlador.AuthController import AuthController
from starlette.middleware.sessions import SessionMiddleware
from typing import Dict, Optional
from controlador.EjercicioPacienteController import EjercicioPacienteController
from controlador.ReporteFisioController import ReporteFisioController
from controlador.CitaController import CitaController
from controlador.CitaPacienteController import CitaPacienteController 
from controlador.ServicioController import ServicioController
from controlador.ServicioNutricionController import ServicioNutricionController
from controlador.PacienteFisioController import PacienteFisioController
from controlador.ServicioImplementosController import ServicioImplementosController
from controlador.CitaFisioController import CitaFisioController
from starlette.middleware.sessions import SessionMiddleware
from controlador.FisioBotController import router as chatbot_router
from controlador.AdminUsuariosController import AdminUsuariosController
from controlador.AuthAdminController import AuthAdminController
from modelo import CitaModel
from modelo.AdministradorModel import AdministradorModel
from controlador.AdminServicioController import AdminServicioController
from controlador.AdminCitaController import AdminCitaController
from controlador.PasswordResetController import PasswordResetController as PRController
from dotenv import load_dotenv
print("\n" + "="*60)
print("🚀 INICIANDO APLICACIÓN EN RAILWAY")
print("="*60)
import os
from fastapi import Form, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware  # ✅ IMPORTANTE: Agregar esto
import secrets
import shutil
import os
app = FastAPI()

check_vars = [
    'MYSQLHOST', 'MYSQLPORT', 'MYSQLDATABASE', 'MYSQLUSER', 'MYSQLPASSWORD',
    'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
    'DATABASE_URL', 'PORT', 'RAILWAY_ENVIRONMENT'
]

print("📋 VARIABLES DE ENTORNO DETECTADAS:")
print("-"*60)

found_vars = []
for var in check_vars:
    if var in os.environ:
        value = os.environ[var]
        if 'PASSWORD' in var:
            print(f"✅ {var}: {'*' * len(value)} ({len(value)} caracteres)")
        else:
            print(f"✅ {var}: {value}")
        found_vars.append(var)
    else:
        print(f"❌ {var}: NO DEFINIDA")

print("-"*60)
print(f"Total variables encontradas: {len(found_vars)}/{len(check_vars)}")

# Mostrar todas las variables que contengan "MYSQL" o "DB"
print("\n🔍 BUSCANDO TODAS LAS VARIABLES CON 'MYSQL' O 'DB':")
for key in sorted(os.environ.keys()):
    key_upper = key.upper()
    if 'MYSQL' in key_upper or ('DB' in key_upper and 'DB_' in key_upper):
        value = os.environ[key]
        if 'PASS' in key_upper:
            print(f"   {key}: {'*' * len(value)}")
        else:
            print(f"   {key}: {value}")

print("="*60 + "\n")

load_dotenv()
PORT = int(os.getenv("PORT", 8000))
app.add_middleware(
    SessionMiddleware,
    secret_key="tu_clave_secreta_muy_larga_aqui_1234567890",  
    session_cookie="fisiosalud_session",
    max_age=3600,
    same_site="lax",
    https_only=False
)

app.include_router(chatbot_router)

templates = Jinja2Templates(directory="./vista")
templates_panel = Jinja2Templates(directory="./vista_panel")
templates_admin = Jinja2Templates(directory="./vista_admin")
templates_fisio = Jinja2Templates(directory="./vista_fisio")

@app.get("/test-db-connect")
async def test_database_connection():
    """Test directo de conexión a MySQL"""
    from bd.conexion_bd import get_db_connection, close_db_connection
    
    try:
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Query simple
                    cursor.execute("SELECT VERSION() as version, DATABASE() as db_name, USER() as user")
                    result = cursor.fetchone()
                    
                    return {
                        "success": True,
                        "message": "✅ Conexión exitosa a MySQL",
                        "database": {
                            "version": result['version'],
                            "name": result['db_name'],
                            "user": result['user']
                        }
                    }
            finally:
                close_db_connection(conn)
        else:
            return {
                "success": False,
                "message": "❌ No se pudo obtener conexión (get_db_connection retornó None)"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error de conexión: {str(e)}",
            "error_type": type(e).__name__
        }
@app.get("/debug-env")
async def debug_environment():
    """Endpoint para debuguear variables de entorno en Railway"""
    import os
    
    result = {
        "status": "checking",
        "timestamp": datetime.now().isoformat(),
        "mysql_variables": {},
        "db_variables": {},
        "database_url": os.environ.get('DATABASE_URL', 'NO DEFINIDA'),
        "all_variables_count": len(os.environ)
    }
    
    mysql_vars = ['MYSQLHOST', 'MYSQLPORT', 'MYSQLDATABASE', 'MYSQLUSER', 'MYSQLPASSWORD']
    for var in mysql_vars:
        if var in os.environ:
            if 'PASSWORD' in var:
                result["mysql_variables"][var] = f"*** ({len(os.environ[var])} caracteres)"
            else:
                result["mysql_variables"][var] = os.environ[var]
        else:
            result["mysql_variables"][var] = "NO DEFINIDA"
    
    db_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    for var in db_vars:
        if var in os.environ:
            if 'PASSWORD' in var:
                result["db_variables"][var] = f"*** ({len(os.environ[var])} caracteres)"
            else:
                result["db_variables"][var] = os.environ[var]
        else:
            result["db_variables"][var] = "NO DEFINIDA"
    
    important_vars = ['PORT', 'RAILWAY_ENVIRONMENT', 'RAILWAY_SERVICE_NAME', 'RAILWAY_PROJECT_NAME']
    result["other_important"] = {}
    for var in important_vars:
        if var in os.environ:
            result["other_important"][var] = os.environ[var]
    
    result["final_config"] = {
        "host": os.environ.get('MYSQLHOST') or os.environ.get('DB_HOST', 'localhost'),
        "port": os.environ.get('MYSQLPORT') or os.environ.get('DB_PORT', '3306'),
        "database": os.environ.get('MYSQLDATABASE') or os.environ.get('DB_NAME', 'railway'),
        "user": os.environ.get('MYSQLUSER') or os.environ.get('DB_USER', 'root')
    }
    
    result["railway_specific"] = {}
    for key in os.environ:
        if 'RAILWAY' in key or 'SERVICE' in key:
            result["railway_specific"][key] = os.environ[key]
    
    return JSONResponse(content=result)

@app.get("/debug-db")
async def debug_database():
    """Endpoint para diagnosticar problemas de conexión"""
    import os
    
    result = {
        "status": "checking",
        "variables_found": {},
        "connection_test": None
    }
    
    # Buscar variables de base de datos
    for key, value in os.environ.items():
        key_upper = key.upper()
        if any(kw in key_upper for kw in ['MYSQL', 'DB', 'DATABASE', 'HOST', 'PORT', 'USER']):
            if 'PASSWORD' in key_upper or 'SECRET' in key_upper:
                result["variables_found"][key] = "*******"
            else:
                result["variables_found"][key] = value
    
    # Intentar conexión
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 as test, DATABASE() as db, USER() as user")
                db_info = cursor.fetchone()
                result["connection_test"] = {
                    "success": True,
                    "database": db_info['db'],
                    "user": db_info['user']
                }
            close_db_connection(conn)
        else:
            result["connection_test"] = {"success": False, "error": "get_db_connection returned None"}
    except Exception as e:
        result["connection_test"] = {"success": False, "error": str(e)}
    
    return JSONResponse(content=result)

@app.get("/check-env")
async def check_env():
    """Ruta SIMPLE para ver variables en Railway"""
    import os
    
    # Variables importantes
    important_vars = {}
    
    for key, value in os.environ.items():
        if any(x in key for x in ['MYSQL', 'DB_', 'HOST', 'PORT', 'DATABASE']):
            if 'PASSWORD' in key:
                important_vars[key] = "***HIDDEN***"
            else:
                important_vars[key] = value
    
    # Si no hay nada, mostrar ALGO
    if not important_vars:
        important_vars = {
            "message": "No variables found with MYSQL/DB keywords",
            "total_variables": len(os.environ),
            "sample_variables": {k: v for k, v in list(os.environ.items())[:5]}
        }
    
    return important_vars

@app.get("/show-vars")
async def show_vars():
    """Muestra todas las variables que Railway inyecta"""
    import os
    import json
    
    result = {}
    
    # Buscar cualquier variable que contenga estas palabras
    keywords = ['MYSQL', 'DB', 'HOST', 'PORT', 'DATABASE', 'USER', 'PASSWORD']
    
    for key, value in os.environ.items():
        if any(kw in key.upper() for kw in keywords):
            if 'PASSWORD' in key:
                result[key] = "*****"  # Ocultar contraseñas
            else:
                result[key] = value
    
    # Si no hay nada, mostrar TODAS las variables (con cuidado)
    if not result:
        result = {"message": "No se encontraron variables de BD. Todas las variables:"}
        for key, value in os.environ.items():
            if 'PASSWORD' not in key and 'SECRET' not in key and 'KEY' not in key:
                result[key] = value
    
    return JSONResponse(content=result)

@app.get("/", response_class=HTMLResponse)
def pagina_inicio(request: Request):
    return templates.TemplateResponse("landing_page.html", {"request": request})

@app.get("/inicio", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("landing_page.html", {"request": request})


@app.get("/nosotros", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("nosotros.html", {"request": request})

@app.get("/serv_terapia", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("serv_terapia.html", {"request": request})

@app.get("/requisitos_especiales", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("requisitos_analisis.html", {"request": request})

@app.get("/servicios_terapia", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("serv_terapia.html", {"request": request})

@app.get("/implementos", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("serv_implementos.html", {"request": request})

@app.get("/nutricionales", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("serv_alimentos.html", {"request": request})

@app.get("/advertencia", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("advertencia.html", {"request": request})

@app.get("/anuncio", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("Anuncio.html", {"request": request})

@app.get("/anuncio_2", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("anuncio_2.html", {"request": request})

@app.get("/administrador", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates_admin.TemplateResponse("panel_login_admin.html", {"request": request})

@app.get("/fisioterapeuta", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates_fisio.TemplateResponse("panel_login_fisio.html", {"request": request})

@app.get("/panel_fisio", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates_fisio.TemplateResponse("panel_login_fisio.html", {"request": request})

@app.get("/fisioapp", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("fisiobot.html", {"request": request})


@app.get("/Fisiobot", response_class=HTMLResponse)
async def fisiobot_page(request: Request):
    """Página del chatbot"""
    return templates.TemplateResponse("Chatbot.html", {
        "request": request,
        "title": "FisioBot - Asistente Virtual"
    })

# 4. (OPCIONAL) Agrega esta ruta de prueba
@app.get("/test-chatbot")
async def test_chatbot():
    """Ruta de prueba para el chatbot"""
    try:
        from modelo.FisioBotModel import fisiobot_model
        test_questions = ["hola", "horarios", "teléfono"]
        results = []
        
        for question in test_questions:
            resp = fisiobot_model.find_best_answer(question)
            results.append({
                "pregunta": question,
                "respuesta": resp["answer"][:50] + "...",
                "score": resp["score"]
            })
        
        return {
            "status": "ok",
            "chatbot": "FisioBot",
            "total_preguntas": len(fisiobot_model.questions),
            "pruebas": results
        }
        
    except Exception as e:
        return {"error": str(e)}

# ─────────────────────────────────────────────────────────────
# LANDING PAGE
# ─────────────────────────────────────────────────────────────

# -- Barra de navegacion -- ─────────────────────────────────────────────────────────────



@app.get("/servicios", response_class=HTMLResponse)
def pagina_servicios(request: Request):
    return templates.TemplateResponse("servicios.html", {"request": request})

@app.get("/fisiobot", response_class=HTMLResponse)
def pagina_servicios(request: Request):
    return templates.TemplateResponse("Fisio_AI.html", {"request": request})

@app.get("/contacto", response_class=HTMLResponse)
def pagina_servicios(request: Request):
    return templates.TemplateResponse("info_contacto.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def pagina_servicios(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/registro", response_class=HTMLResponse)
def pagina_servicios(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

# -- Main Page -- ─────────────────────────────────────────────────────────────
@app.get("/servicios", response_class=HTMLResponse)
def pagina_servicios(request: Request):
    return templates.TemplateResponse("servicios.html", {"request": request})

@app.get("/cita", response_class=HTMLResponse)
async def pagina_servicios(request: Request, servicio: Optional[str] = None):
    return await CitaController.mostrar_formulario_cita(request, servicio_codigo=servicio)

# -- Servicios -- ─────────────────────────────────────────────────────────────

@app.get("/servicios_terapeuticos", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("serv_terapia.html", {"request": request})

from fastapi import FastAPI, Request, Form
from controlador.ServicioController import ServicioController


@app.get("/servicios")
async def servicios(request: Request):
    return await ServicioController.listar_servicios_terapeuticos(request)

@app.get("/servicios/categoria/{categoria}")
async def servicios_categoria(request: Request, categoria: str):
    return await ServicioController.filtrar_servicios(request, categoria)

@app.get("/servicios/terapeuta/{terapeuta_busqueda}")
async def servicios_terapeuta(request: Request, terapeuta_busqueda: str):
    return await ServicioController.filtrar_servicios_terapeuta(request, terapeuta_busqueda)

@app.post("/servicios/buscar-terapeuta")
async def buscar_servicios_terapeuta(request: Request, terapeuta: str = Form(...)):
    return await ServicioController.filtrar_servicios_terapeuta(request, terapeuta)

@app.get("/servicio/{codigo}")
async def detalle_servicio(request: Request, codigo: str):
    return await ServicioController.detalle_servicio(request, codigo)

@app.get("/servicios_alimenticios", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("serv_alimentos.html", {"request": request})
    
@app.get("/servicios_implementos", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("serv_implementos.html", {"request": request})

# -- AI seccion -- ─────────────────────────────────────────────────────────────

@app.get("/Fisiobot", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("fisiobot.html", {"request": request})

@app.get("/contacto", response_class=HTMLResponse)
def pagina_servicios(request: Request):
    return templates.TemplateResponse("info_contacto.html", {"request": request})

@app.get("/analisis", response_class=HTMLResponse)
def pagina_servicios(request: Request):
    return templates.TemplateResponse("analisis_previo.html", {"request": request})


# ─────────────────────────────────────────────────────────────
# lOGIN Y REGISTRO
# ─────────────────────────────────────────────────────────────


@app.get("/registro_user", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@app.get("/inicio", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("landing_page.html", {"request": request})

@app.get("/login_user", response_class=HTMLResponse)
def pagina_servicios_terapeuticos(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



# ─────────────────────────────────────────────────────────────
# RESTFULL API PARA REGISTRO DE USUARIOS
# ─────────────────────────────────────────────────────────────


@app.post("/validar_acceso", response_class=HTMLResponse)
async def validar_acceso(
    request: Request, 
    correo: str = Form(...), 
    contraseña: str = Form(...)
):
    return await AuthController.validar_acceso(request, correo, contraseña)

# Agregar estos endpoints después de los existentes
@app.get("/olvidar-contrasena", response_class=HTMLResponse)
async def olvidar_contrasena_page(request: Request):
    """Muestra el formulario para solicitar reset de contraseña"""
    # Limpiar mensajes previos
    success = request.session.pop('success_message', None)
    error = request.session.pop('error', None)
    
    return templates.TemplateResponse("olvidar_contraseña.html", {
        "request": request,
        "success_message": success,
        "error": error
    })

@app.post("/solicitar-reset", response_class=HTMLResponse)
async def solicitar_reset_password(
    request: Request,
    correo: str = Form(...)
):
    # ❌ ELIMINA esta línea dentro de la función:
    # from controlador.PasswordResetController import PasswordResetController
    
    # ✅ USA la importación correcta:
    return await PRController.solicitar_reset(request, correo)

@app.get("/resetear-contrasena/{token}", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str):
    return await PRController.validar_token_reset(request, token)

@app.post("/actualizar-contrasena", response_class=HTMLResponse)
async def actualizar_contrasena(
    request: Request,
    token: str = Form(...),
    nueva_contrasena: str = Form(...),
    confirmar_contrasena: str = Form(...)
):
    return await PRController.actualizar_contrasena(
        request, token, nueva_contrasena, confirmar_contrasena
    )


# ─────────────────────────────────────────────────────────────
# RESTFULL API PARA SERVICIOS
# ─────────────────────────────────────────────────────────────

@app.get("/serv_terapia", response_class=HTMLResponse)
async def pagina_servicios_terapeuticos(request: Request):
    return await ServicioController.listar_servicios_terapeuticos(request)

@app.get("/servicio/{codigo}", response_class=HTMLResponse)
async def detalle_servicio(request: Request, codigo: str):
    return await ServicioController.detalle_servicio(request, codigo)

@app.get("/servicios/filtrar/{categoria}", response_class=HTMLResponse)
async def filtrar_servicios(request: Request, categoria: str):
    return await ServicioController.filtrar_servicios(request, categoria)


@app.get("/nutricion/{codigo}", response_class=HTMLResponse)
async def detalle_nutricion(request: Request, codigo: str):
    return await ServicioNutricionController.detalle_servicio(request, codigo)

@app.get("/nutricionales", response_class=HTMLResponse)
async def pagina_servicios_nutricion(request: Request):
    return await ServicioNutricionController.listar_servicios_nutricion(request)

@app.get("/implementos/{codigo}", response_class=HTMLResponse)
async def detalle_implementos(request: Request, codigo: str):
    return await ServicioImplementosController.detalle_servicio(request, codigo)

@app.get("/implementos", response_class=HTMLResponse)
async def pagina_servicios_implementos(request: Request):
    return await ServicioImplementosController.listar_servicios_implementos(request)



# ─────────────────────────────────────────────────────────────
# RESTFULL API PARA CITAS
# ─ ────────────────────────────────────────────────────────────
@app.get("/agendar-cita", response_class=HTMLResponse)
async def formulario_cita_page(
    request: Request,
    servicio: Optional[str] = None
):
    """Muestra el formulario HTML para agendar citas"""
    return await CitaController.mostrar_formulario_cita(request, servicio)

# 2. APIS PARA EL FRONTEND

# 2.1 API para obtener servicios de terapia
@app.get("/api/servicios-terapia")
async def obtener_servicios_terapia_api(request: Request):
    """API para obtener todos los servicios de terapia disponibles"""
    return await CitaController.obtener_servicios_api(request)



# 2.2 API para obtener información de terapeutas
@app.get("/api/terapeutas")
async def obtener_terapeutas_api(request: Request):
    """API endpoint para obtener información de terapeutas"""
    try:
        conn = get_db_connection()
        if conn is None:
            return JSONResponse(
                status_code=500,
                content={"error": "Error de conexión a la base de datos"}
            )
        
        with conn.cursor() as cursor:
            sql = """
            SELECT nombre_completo, franja_horaria_dias, franja_horaria_horas
            FROM terapeuta
            WHERE estado = 'Activo' OR estado IS NULL
            """
            cursor.execute(sql)
            terapeutas = cursor.fetchall()
            
        close_db_connection(conn)
        
        return JSONResponse(content={"terapeutas": terapeutas})
        
    except Exception as e:
        print(f"Error en API de terapeutas: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error al obtener información de terapeutas"}
        )

# 2.3 API para agendar cita - USUARIO (pool FS-0001 a FS-0500)
@app.post("/api/agendar-cita")
async def agendar_cita_api(
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
    """API para agendar una nueva cita (usuario autogestionado)"""
    return await CitaController.agendar_cita(
        request=request,
        servicio=servicio,
        terapeuta_designado=terapeuta_designado,
        nombre_paciente=nombre_paciente,
        telefono=telefono,
        correo=correo,
        fecha_cita=fecha_cita,
        hora_cita=hora_cita,
        notas_adicionales=notas_adicionales,
        tipo_pago=tipo_pago,
        acudiente_nombre=acudiente_nombre,
        acudiente_id=acudiente_id,
        acudiente_telefono=acudiente_telefono,
        acudiente_correo=acudiente_correo,
        emails_adicionales=emails_adicionales
    )

# 2.4 API para agendar cita - ADMINISTRADOR (pool FS-0501 a FS-1000)
@app.post("/api/agendar-cita-admin")
async def agendar_cita_admin_api(
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
    """API para agendar cita como administrador (pool diferente)"""
    try:
        from controlador.CitaController import CitaController
        
        # Datos de la cita
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
        
        # Usar tipo_usuario = 'admin' para usar pool diferente
        codigo_cita = CitaModel.crear_cita(datos_cita, tipo_usuario='admin')
        
        if not codigo_cita:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error al crear la cita como administrador"}
            )
        
        # Crear acudiente si existe
        acudiente_creado = False
        if acudiente_nombre and acudiente_id:
            datos_acudiente = {
                'nombre_completo': acudiente_nombre,
                'identificacion': acudiente_id,
                'telefono': acudiente_telefono or '',
                'correo': acudiente_correo or ''
            }
            
            acudiente_creado = CitaModel.crear_acudiente(codigo_cita, datos_acudiente)
        
        return JSONResponse(content={
            "success": True,
            "message": "Cita agendada exitosamente como administrador",
            "codigo_cita": codigo_cita,
            "tipo_usuario": "admin",
            "acudiente_creado": acudiente_creado
        })
        
    except Exception as e:
        print(f"Error al agendar cita como admin: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Error interno del servidor"}
        )

# 2.5 API para agendar cita - FISIOTERAPEUTA (pool FS-1001 a FS-2000)
@app.post("/api/agendar-cita-fisio")
async def agendar_cita_fisio_api(
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
    """API para agendar cita como fisioterapeuta (pool diferente)"""
    try:
        from controlador.CitaController import CitaController
        
        # Datos de la cita
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
        
        # Usar tipo_usuario = 'fisio' para usar pool diferente
        codigo_cita = CitaModel.crear_cita(datos_cita, tipo_usuario='fisio')
        
        if not codigo_cita:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Error al crear la cita como fisioterapeuta"}
            )
        
        # Crear acudiente si existe
        acudiente_creado = False
        if acudiente_nombre and acudiente_id:
            datos_acudiente = {
                'nombre_completo': acudiente_nombre,
                'identificacion': acudiente_id,
                'telefono': acudiente_telefono or '',
                'correo': acudiente_correo or ''
            }
            
            acudiente_creado = CitaModel.crear_acudiente(codigo_cita, datos_acudiente)
        
        return JSONResponse(content={
            "success": True,
            "message": "Cita agendada exitosamente como fisioterapeuta",
            "codigo_cita": codigo_cita,
            "tipo_usuario": "fisio",
            "acudiente_creado": acudiente_creado
        })
        
    except Exception as e:
        print(f"Error al agendar cita como fisio: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Error interno del servidor"}
        )

# 2.6 API para verificar estado del pool de códigos
@app.get("/api/estado-pool-citas")
async def verificar_pool_codigos_api(request: Request):
    """Verifica el estado del pool de códigos FS-0001 a FS-0500"""
    try:
        estado = CitaModel.verificar_estado_pool_usuario()
        return JSONResponse(content=estado)
    except Exception as e:
        print(f"Error al verificar pool: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error al verificar pool de códigos"}
        )

# 2.7 API para verificar disponibilidad de horario
@app.get("/api/verificar-disponibilidad")
async def verificar_disponibilidad_api(
    request: Request,
    fecha: str,
    hora: str,
    terapeuta: str
):
    """Verifica si un horario está disponible para un terapeuta"""
    try:
        disponible = CitaModel.verificar_disponibilidad_cita(fecha, hora, terapeuta)
        return JSONResponse(content={
            "disponible": disponible,
            "fecha": fecha,
            "hora": hora,
            "terapeuta": terapeuta
        })
    except Exception as e:
        print(f"Error al verificar disponibilidad: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error al verificar disponibilidad"}
        )

# 2.8 API para obtener detalles de una cita
@app.get("/api/cita/{codigo_cita}")
async def obtener_cita_api(request: Request, codigo_cita: str):
    """Obtiene los detalles de una cita específica"""
    try:
        conn = get_db_connection()
        if conn is None:
            return JSONResponse(
                status_code=500,
                content={"error": "Error de conexión"}
            )
        
        with conn.cursor() as cursor:
            # Obtener cita
            sql = """
            SELECT * FROM cita WHERE cita_id = %s
            """
            cursor.execute(sql, (codigo_cita,))
            cita = cursor.fetchone()
            
            if not cita:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Cita no encontrada"}
                )
            
            # Obtener acudiente si existe
            cursor.execute("SELECT * FROM acudiente WHERE cita_id = %s", (codigo_cita,))
            acudiente = cursor.fetchone()
            
        close_db_connection(conn)
        
        return JSONResponse(content={
            "cita": dict(cita) if cita else None,
            "acudiente": dict(acudiente) if acudiente else None
        })
        
    except Exception as e:
        print(f"Error al obtener cita: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error al obtener información de la cita"}
        )

# 2.9 API para obtener citas por fecha
@app.get("/api/citas-por-fecha")
async def obtener_citas_fecha_api(
    request: Request,
    fecha: str
):
    """Obtiene todas las citas de una fecha específica"""
    try:
        conn = get_db_connection()
        if conn is None:
            return JSONResponse(
                status_code=500,
                content={"error": "Error de conexión"}
            )
        
        with conn.cursor() as cursor:
            sql = """
            SELECT cita_id, nombre_paciente, servicio, terapeuta_designado, 
                   hora_cita, estado, tipo_pago
            FROM cita 
            WHERE fecha_cita = %s
            ORDER BY hora_cita
            """
            cursor.execute(sql, (fecha,))
            citas = cursor.fetchall()
            
        close_db_connection(conn)
        
        return JSONResponse(content={
            "fecha": fecha,
            "total_citas": len(citas),
            "citas": [dict(cita) for cita in citas]
        })
        
    except Exception as e:
        print(f"Error al obtener citas por fecha: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Error al obtener citas"}
        )

# ─────────────────────────────────────────────────────────────
# PANELES DE USUARIO
# ─────────────────────────────────────────────────────────────

@app.get("/registro")
async def registro_page(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@app.get("/login_user")
async def login_user_page(request: Request):
    error = request.session.pop('error', None)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error_message": error
    })

@app.post("/login_user")
async def login_user(
    request: Request,
    correo: str = Form(...),
    contraseña: str = Form(...)
):
    return await AuthController.validar_acceso(request, correo, contraseña)

@app.get("/logout_user")
async def logout_user(request: Request):
    return await AuthController.cerrar_sesion(request)

@app.post("/registro_usuario")
async def registrar_usuario(
    request: Request,
    nombre: str = Form(...),
    apellido: str = Form(...),
    genero: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    contraseña: str = Form(...),
    contraseña_confirmada: str = Form(...),
    ID: str = Form(...),
    historial_medico: UploadFile = File(None)
):
    from controlador.AuthController import AuthController
    return await AuthController.registrar_usuario(
        request, nombre, apellido, genero, email, telefono, 
        contraseña, contraseña_confirmada, ID, historial_medico
    )

@app.get("/panel_citas", response_class=HTMLResponse)
async def panel_citas(request: Request):
    """Panel de citas del usuario con verificación de sesión"""
    print("🔍 Accediendo a /panel_citas...")
    usuario = AuthController.verificar_sesion_usuario(request)
    
    if not usuario:
        print("❌ No hay sesión en /panel_citas, redirigiendo...")
        request.session['error'] = 'Por favor, inicie sesión primero'
        return RedirectResponse(url="/login_user", status_code=302)
    
    print(f"✅ Sesión válida para: {usuario['email']}")
    return templates_panel.TemplateResponse("panel_citas.html", {
        "request": request,
        "usuario": usuario
    })


@app.get("/panel_progreso", response_class=HTMLResponse)
async def panel_progreso(request: Request):
    """Panel de progreso del usuario con verificación de sesión"""
    usuario = AuthController.verificar_sesion_usuario(request)
    if not usuario:
        request.session['error'] = 'Por favor, inicie sesión primero'
        return RedirectResponse(url="/login_user", status_code=302)
    
    return templates_panel.TemplateResponse("panel_progreso.html", {
        "request": request,
        "usuario": usuario
    })

@app.get("/panel_ejercicios", response_class=HTMLResponse)
async def panel_ejercicios(request: Request):
    """Panel de ejercicios del usuario con verificación de sesión"""
    usuario = AuthController.verificar_sesion_usuario(request)
    if not usuario:
        request.session['error'] = 'Por favor, inicie sesión primero'
        return RedirectResponse(url="/login_user", status_code=302)
    
    return templates_panel.TemplateResponse("panel_ejercicios.html", {
        "request": request,
        "usuario": usuario
    })




# ─────────────────────────────────────────────────────────────
# PANELES DE USUARIO - CITAS
# ─────────────────────────────────────────────────────────────

@app.get("/api/citas/paciente")
async def api_obtener_citas_paciente(request: Request):
    print("🔍 [ROUTE] /api/citas/paciente llamado")
    return await CitaPacienteController.obtener_citas_paciente(request)

@app.get("/api/citas/proximas")
async def api_obtener_citas_proximas(request: Request):
    print("🔍 [ROUTE] /api/citas/proximas llamado")
    return await CitaPacienteController.obtener_citas_proximas(request)

@app.get("/api/citas/{cita_id}") 
async def api_obtener_cita_por_id(request: Request, cita_id: str):
    print(f"🔍 [ROUTE] /api/citas/{cita_id} llamado")
    return await CitaPacienteController.obtener_cita_por_id(request, cita_id)

@app.get("/api/citas/estadisticas")
async def api_obtener_estadisticas(request: Request):
    print("🔍 [ROUTE] /api/citas/estadisticas llamado")
    return await CitaPacienteController.obtener_estadisticas(request)


# ─────────────────────────────────────────────────────────────
# PANELES DE USUARIO - EJERCICIOS
# ─────────────────────────────────────────────────────────────

# Agregar estos endpoints a tu archivo principal

@app.get("/api/ejercicios/debug-ejercicios")
async def api_debug_ejercicios_bd(request: Request):
    """Endpoint para ver todos los ejercicios en la BD"""
    from bd.conexion_bd import get_db_connection
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT codigo_ejercicio, nombre_ejercicio FROM ejercicios")
            ejercicios = cursor.fetchall()
            
            print("🔍 TODOS LOS EJERCICIOS EN LA BD:")
            for ej in ejercicios:
                print(f"   - Código: '{ej['codigo_ejercicio']}', Nombre: '{ej['nombre_ejercicio']}'")
            
            return JSONResponse({
                "success": True,
                "ejercicios": ejercicios
            })
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse({"success": False, "error": str(e)})
    finally:
        conn.close()

@app.get("/api/ejercicios/paciente")
async def api_obtener_ejercicios_paciente(request: Request):
    print("🔍 [ROUTE] /api/ejercicios/paciente llamado")
    return await EjercicioPacienteController.obtener_ejercicios_paciente(request)

@app.get("/api/ejercicios/completados")
async def api_obtener_ejercicios_completados(request: Request):
    print("🔍 [ROUTE] /api/ejercicios/completados llamado")
    return await EjercicioPacienteController.obtener_ejercicios_completados(request)

@app.get("/api/ejercicios/pendientes")
async def api_obtener_ejercicios_pendientes(request: Request):
    print("🔍 [ROUTE] /api/ejercicios/pendientes llamado")
    return await EjercicioPacienteController.obtener_ejercicios_pendientes(request)

@app.get("/api/ejercicios/estadisticas")
async def api_obtener_estadisticas_ejercicios(request: Request):
    print("🔍 [ROUTE] /api/ejercicios/estadisticas llamado")
    return await EjercicioPacienteController.obtener_estadisticas(request)

@app.post("/api/ejercicios/completar")
async def api_marcar_ejercicio_completado(request: Request):
    return await EjercicioPacienteController.marcar_como_completado(request)

@app.get("/api/ejercicios/{codigo_ejercicio}")
async def api_obtener_ejercicio_por_codigo(request: Request, codigo_ejercicio: str):
    print(f"🔍 [ROUTE] /api/ejercicios/{codigo_ejercicio} llamado")
    return await EjercicioPacienteController.obtener_ejercicio_por_codigo(request, codigo_ejercicio)



# ─────────────────────────────────────────────────────────────
# PANELES DE USUARIO - PRODUCTOS
# ─────────────────────────────────────────────────────────────


@app.post("/api/carrito/agregar")
async def api_agregar_carrito(request: Request):
    print("✅ RUTA /api/carrito/agregar LLAMADA")
    from controlador.CarritoController import CarritoController
    return await CarritoController.agregar_al_carrito(request)

@app.post("/api/carrito/eliminar")
async def api_eliminar_carrito(request: Request):
    print("✅ RUTA /api/carrito/eliminar LLAMADA")
    from controlador.CarritoController import CarritoController
    return await CarritoController.eliminar_del_carrito(request)

@app.post("/api/carrito/actualizar-cantidad")
async def api_actualizar_cantidad(request: Request):
    print("✅ RUTA /api/carrito/actualizar-cantidad LLAMADA")
    from controlador.CarritoController import CarritoController
    return await CarritoController.actualizar_cantidad_carrito(request)

@app.post("/api/carrito/vaciar")
async def api_vaciar_carrito(request: Request):
    print("✅ RUTA /api/carrito/vaciar LLAMADA")
    from controlador.CarritoController import CarritoController
    return await CarritoController.vaciar_carrito(request)

@app.get("/panel_mercado")
async def panel_mercado(request: Request):
    print("✅ RUTA /panel_mercado LLAMADA")
    from controlador.CarritoController import CarritoController
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="./vista_panel")
    
    try:
        data = await CarritoController.mostrar_panel_productos(request)
        if data["success"]:
            return templates.TemplateResponse("panel_producto.html", {
                "request": request,
                "usuario": data["usuario"],
                "carrito_items": data["carrito_items"],
                "productos_nutricion": data["productos_nutricion"],
                "productos_implementos": data["productos_implementos"],  # ✅ NUEVO
                "total_carrito": data["total_carrito"],
                "items_count": data["items_count"]
            })
    except Exception as e:
        print(f"Error en panel_mercado: {e}")
        return templates.TemplateResponse("panel_producto.html", {
            "request": request,
            "error": "Error al cargar el panel"
        })

# ✅ ENDPOINTS PARA CARGAR DATOS ESPECÍFICOS - AGREGAR ESTOS
@app.get("/api/productos/nutricion")
async def api_productos_nutricion(request: Request):
    from modelo.ServicioNutricionModel import ServicioNutricionModel
    
    usuario = AuthController.verificar_sesion_usuario(request)
    if not usuario:
        return JSONResponse({"success": False, "message": "No autorizado"}, status_code=401)
    
    productos, error = ServicioNutricionModel.obtener_todos_servicios()
    return JSONResponse({
        "success": True if not error else False,
        "productos": productos or [],
        "error": error
    })

@app.get("/api/productos/implementos")
async def api_productos_implementos(request: Request):
    from modelo.ServicioImplementosModel import ServicioImplementosModel
    
    usuario = AuthController.verificar_sesion_usuario(request)
    if not usuario:
        return JSONResponse({"success": False, "message": "No autorizado"}, status_code=401)
    
    productos, error = ServicioImplementosModel.obtener_todos_servicios()
    return JSONResponse({
        "success": True if not error else False,
        "productos": productos or [],
        "error": error
    })

@app.get("/api/carrito/mio")
async def api_carrito_mio(request: Request):
    from modelo.CarritoModel import CarritoModel
    
    usuario = AuthController.verificar_sesion_usuario(request)
    if not usuario:
        return JSONResponse({"success": False, "message": "No autorizado"}, status_code=401)
    
    carrito_items, error = CarritoModel.obtener_carrito_usuario(usuario['id'])
    
    # Calcular totales
    total_carrito = 0
    items_count = 0
    if carrito_items:
        for item in carrito_items:
            precio = float(item.get('precio', 0)) or 0
            cantidad = int(item.get('cantidad', 1)) or 1
            total_carrito += precio * cantidad
            items_count += cantidad
    
    return JSONResponse({
        "success": True if not error else False,
        "carrito": carrito_items or [],
        "total_carrito": total_carrito,
        "items_count": items_count,
        "error": error
    })
@app.post("/api/carrito/confirmar-compra")
async def api_confirmar_compra(request: Request):
    print("✅ RUTA /api/carrito/confirmar-compra LLAMADA")
    from controlador.CarritoController import CarritoController
    return await CarritoController.confirmar_compra(request)

@app.get("/api/carrito/historial")
async def api_historial_compras(request: Request):
    print("✅ RUTA /api/carrito/historial LLAMADA")
    from controlador.CarritoController import CarritoController
    return await CarritoController.obtener_historial_compras(request)
# ─────────────────────────────────────────────────────────────
# PANELES DE FISIOTERAPEUTA - CITA
# ─────────────────────────────────────────────────────────────

# =============================================
# RUTAS DE AUTENTICACIÓN (MANTENER EXISTENTES)
# =============================================

@app.post("/login-fisio")
async def login_fisioterapeuta(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)  
):
    """
    Endpoint para login de fisioterapeutas - CORREGIDO
    """
    try:
        # Usar el AuthFisioController CORRECTO (el que me mostraste)
        resultado = AuthFisioController.login_fisioterapeuta(email, password)
        
        if resultado['success']:
            # Credenciales válidas - crear sesión COMPLETA
            terapeuta = resultado['terapeuta']
            
            request.session['fisioterapeuta'] = {
                'codigo_trabajador': terapeuta['Codigo_trabajador'],
                'nombre_completo': terapeuta['nombre_completo'],  # ← ¡ESTO ES CLAVE!
                'email': terapeuta['fisio_correo'],
                'especializacion': terapeuta.get('especializacion', ''),
                'telefono': terapeuta.get('telefono', ''),
                'logged_in': True
            }
            
            print(f"✅ Login exitoso: {terapeuta['nombre_completo']}")
            print(f"📋 Sesión guardada: {request.session['fisioterapeuta']}")
            
            return RedirectResponse(url="/panel_citas_fisio", status_code=303)
        else:
            # Credenciales inválidas
            return templates_fisio.TemplateResponse("panel_login_fisio.html", {
                "request": request,
                "error": resultado['error']
            })
            
    except Exception as e:
        print(f"❌ Error en endpoint login-fisio: {e}")
        import traceback
        traceback.print_exc()
        return templates_fisio.TemplateResponse("panel_login_fisio.html", {
            "request": request,
            "error": 'Error interno del servidor'
        })

@app.get("/login-fisio-page")
async def login_fisio_page(request: Request):
    """
    Endpoint para mostrar la página de login de fisioterapeutas
    """
    error = request.session.pop('error', None)
    
    return templates_fisio.TemplateResponse("panel_login_fisio.html", {
        "request": request,
        "error": error
    })

def verificar_sesion_fisio(request: Request) -> dict:
    """
    Verifica la sesión del fisioterapeuta
    Retorna los datos del fisioterapeuta o None si no hay sesión
    """
    print("=" * 50)
    print("🔍 [verificar_sesion_fisio] Verificando sesión...")
    print(f"📋 Keys en sesión: {list(request.session.keys())}")
    
    fisioterapeuta = request.session.get('fisioterapeuta')
    
    if not fisioterapeuta:
        print("❌ No existe 'fisioterapeuta' en la sesión")
        request.session['error'] = 'Por favor, inicie sesión primero'
        return None
    
    if not fisioterapeuta.get('logged_in'):
        print(f"❌ logged_in es: {fisioterapeuta.get('logged_in')}")
        request.session['error'] = 'Sesión expirada'
        return None
    
    print(f"✅ Sesión válida para: {fisioterapeuta.get('nombre_completo')}")
    print("=" * 50)
    return fisioterapeuta


@app.get("/logout-fisio")
async def logout_fisioterapeuta(request: Request):
    """
    Endpoint para cerrar sesión de fisioterapeutas
    Limpia la sesión y redirige a la página de inicio
    """
    try:
        fisioterapeuta = request.session.get('fisioterapeuta')
        email = fisioterapeuta.get('email', 'Desconocido') if fisioterapeuta else 'Desconocido'
        
        request.session.clear()
        
        if 'fisioterapeuta' in request.session:
            del request.session['fisioterapeuta']
        
        request.session['success'] = 'Sesión cerrada correctamente'
        
        print(f"✅ Logout exitoso: {email} - {datetime.now()}")
        
        return RedirectResponse(url="/inicio", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        request.session.clear()
        print(f"⚠️ Error durante logout: {e}")
        
        return RedirectResponse(url="/inicio", status_code=status.HTTP_302_FOUND)

# En tu archivo principal de FastAPI (app.py o main.py)
# Agrega estos endpoints junto a los que ya tienes

from controlador.CitaFisioController import CitaFisioController
from controlador.AuthFisioController import AuthFisioController  # Si ya existe

# ============================================
# ENDPOINTS DE CITAS PARA FISIOTERAPEUTAS
# ============================================

@app.get("/panel_citas_fisio")
async def panel_citas_fisio(request: Request):
    """
    Endpoint principal para mostrar el panel de citas del fisioterapeuta
    """
    try:
        # Verificar sesión del fisioterapeuta
        fisioterapeuta = verificar_sesion_fisio(request)
        
        if not fisioterapeuta:
            print("❌ No hay sesión activa, redirigiendo a login")
            request.session['error'] = 'Por favor, inicie sesión primero'
            return RedirectResponse(url="/login-fisio-page", status_code=303)
        
        print(f"✅ Acceso autorizado a panel_citas_fisio para: {fisioterapeuta.get('nombre_completo')}")
        
        # Renderizar template con datos del fisioterapeuta
        return templates_fisio.TemplateResponse("panel_cita_fisio.html", {
            "request": request,
            "fisioterapeuta": fisioterapeuta
        })
        
    except Exception as e:
        print(f"❌ Error en endpoint panel_citas_fisio: {e}")
        import traceback
        traceback.print_exc()
        request.session['error'] = 'Error al cargar el panel de citas'
        return RedirectResponse(url="/login-fisio-page", status_code=303)
    

app.add_api_route("/api/citas-fisio/{cita_id}/cancelar-con-motivo", 
                 CitaFisioController.cancelar_cita_con_motivo, 
                 methods=["POST"])


# ============================================
# API ENDPOINTS (JSON)
# ============================================

@app.get("/api/citas-fisio")
async def api_obtener_citas(request: Request):
    """
    API para obtener todas las citas del fisioterapeuta logueado
    Método: GET
    Retorno: JSON con listado de citas
    """
    return await CitaFisioController.obtener_citas(request)

@app.put("/api/citas-fisio/{cita_id}/estado")
async def api_cambiar_estado_cita(request: Request, cita_id: str):
    """
    API para cambiar el estado de una cita
    Método: PUT
    Body JSON: {"estado": "confirmada"} (o "pendiente", "cancelada")
    Retorno: JSON con resultado
    """
    return await CitaFisioController.cambiar_estado_cita(request, cita_id)

@app.get("/api/citas-fisio/estadisticas")
async def api_obtener_estadisticas(request: Request):
    """
    API para obtener estadísticas de citas
    Método: GET
    Retorno: JSON con conteos para cards
    """
    return await CitaFisioController.obtener_estadisticas(request)

@app.post("/api/citas-fisio/filtrar")
async def api_filtrar_citas(request: Request):
    """
    API para filtrar citas
    Método: POST
    Body JSON: {"fecha": "2024-01-15", "paciente": "Juan", "servicio": "Fisioterapia", "estado": "pendiente"}
    Retorno: JSON con citas filtradas
    """
    return await CitaFisioController.filtrar_citas(request)

@app.get("/api/citas-fisio/{cita_id}/detalle")
async def api_obtener_detalle_cita(request: Request, cita_id: str):
    """
    API para obtener detalle de una cita específica
    Método: GET
    Retorno: JSON con detalle completo
    """
    return await CitaFisioController.obtener_cita_detalle(request, cita_id)

# ============================================
# ENDPOINT DE PRUEBA/STATUS
# ============================================

@app.get("/api/citas-fisio/status")
async def api_status_citas(request: Request):
    """
    Endpoint de estado/health check para citas
    """
    try:
        # Verificar sesión
        fisioterapeuta = request.session.get('fisioterapeuta')
        
        if not fisioterapeuta or not fisioterapeuta.get('logged_in'):
            return JSONResponse(
                status_code=401,
                content={
                    "status": "error",
                    "message": "No autenticado"
                }
            )
        
        terapeuta_actual = fisioterapeuta.get('nombre_completo')
        
        # Obtener estadísticas rápidas
        from modelo.CitaFisioModel import CitaFisioModel
        stats = CitaFisioModel.obtener_estadisticas_citas(terapeuta_actual)
        
        return JSONResponse(content={
            "status": "ok",
            "message": "API de citas funcionando correctamente",
            "terapeuta": terapeuta_actual,
            "estadisticas": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error: {str(e)}"
            }
        )

# ============================================
# MIDDLEWARE O FUNCIONES AUXILIARES (si no existen)
# ============================================

def verificar_sesion_fisio(request: Request) -> Optional[Dict]:
    """
    Verifica la sesión del fisioterapeuta
    (Esta función ya la tienes, pero la pongo por referencia)
    """
    fisioterapeuta = request.session.get('fisioterapeuta')
    
    if not fisioterapeuta:
        print("❌ No existe 'fisioterapeuta' en la sesión")
        return None
    
    if not fisioterapeuta.get('logged_in'):
        print(f"❌ logged_in es: {fisioterapeuta.get('logged_in')}")
        return None
    
    print(f"✅ Sesión válida para: {fisioterapeuta.get('nombre_completo')}")
    return fisioterapeuta

@app.get("/panel_pacientes_fisio")
async def panel_pacientes_fisio(request: Request):
    fisioterapeuta = verificar_sesion_fisio(request)
    if not fisioterapeuta:
        return RedirectResponse(url="/login-fisio-page", status_code=status.HTTP_302_FOUND)
    
    return templates_fisio.TemplateResponse("panel_pacientes_fisio.html", {
        "request": request,
        "fisioterapeuta": fisioterapeuta
    })

@app.get("/panel_progreso_fisio")
async def panel_progreso_fisio(request: Request):
    fisioterapeuta = verificar_sesion_fisio(request)
    if not fisioterapeuta:
        return RedirectResponse(url="/login-fisio-page", status_code=status.HTTP_302_FOUND)
    
    return templates_fisio.TemplateResponse("panel_progreso_fisio.html", {
        "request": request,
        "fisioterapeuta": fisioterapeuta
    })



# ─────────────────────────────────────────────────────────────
# PANELES DE FISIOTERAPEUTA - PACIENTE
# ─────────────────────────────────────────────────────────────

app.add_api_route("/api/pacientes", PacienteFisioController.obtener_pacientes, methods=["GET"])
app.add_api_route("/api/pacientes/estadisticas", PacienteFisioController.obtener_estadisticas_pacientes, methods=["GET"])
app.add_api_route("/api/ejercicios", PacienteFisioController.obtener_ejercicios, methods=["GET"])
app.add_api_route("/api/pacientes/{codigo_cita}/ejercicios", PacienteFisioController.obtener_ejercicios_paciente, methods=["GET"])
app.add_api_route("/api/pacientes/asignar-ejercicios", PacienteFisioController.asignar_ejercicios, methods=["POST"])
app.add_api_route("/api/pacientes/{codigo_cita}", PacienteFisioController.eliminar_paciente, methods=["DELETE"])


# ─────────────────────────────────────────────────────────────
# PANELES DE FISIOTERAPEUTA - PROGRESO
# ─────────────────────────────────────────────────────────────

@app.post("/api/debug/pdf")
async def debug_pdf(request: Request, file: UploadFile = File(...)):
    """Endpoint para debuguear el PDF recibido"""
    content = await file.read()
    
    return JSONResponse({
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
        "first_20_bytes": str(content[:20]),
        "is_pdf": content.startswith(b'%PDF'),
        "hex_first_10": content[:10].hex()
    })

# Endpoints principales del módulo de progreso (NO TOCAR)
app.add_api_route("/api/progreso/pacientes-filtros", ReporteFisioController.obtener_pacientes_para_filtros, methods=["GET"])
app.add_api_route("/api/progreso/estadisticas", ReporteFisioController.obtener_estadisticas_progreso, methods=["GET"])
app.add_api_route("/api/reportes", ReporteFisioController.guardar_reporte, methods=["POST"])
app.add_api_route("/api/reportes", ReporteFisioController.obtener_reportes, methods=["GET"])
app.add_api_route("/api/reportes/{codigo_cita}/descargar", ReporteFisioController.descargar_reporte, methods=["GET"])


# ─────────────────────────────────────────────────────────────
# PANELES DE ADMINISTRADOR 
# ─────────────────────────────────────────────────────────────

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """
    Página de login para administradores
    """
    error = request.session.pop('error', None)
    return templates_admin.TemplateResponse("panel_login_admin.html", {
        "request": request,
        "error": error
    })

@app.post("/admin/login")
async def login_admin(request: Request, correo: str = Form(...), password: str = Form(...)):
    """
    Procesa el login del administrador
    """
    return await AuthAdminController.login_admin(request, correo, password)

@app.get("/admin/logout")
async def logout_admin(request: Request):
    """
    Endpoint para logout de administradores
    """
    return await AuthAdminController.logout_admin(request)


# ─────────────────────────────────────────────────────────────
# PANELES DE ADMINISTRADOR - USUARIOS
# ─────────────────────────────────────────────────────────────

# Estadísticas
app.add_api_route("/api/admin/estadisticas", 
                  AdminUsuariosController.obtener_estadisticas_admin, 
                  methods=["GET"])

# Usuarios - CRUD completo
app.add_api_route("/api/admin/usuarios", 
                  AdminUsuariosController.listar_usuarios, 
                  methods=["GET"])

app.add_api_route("/api/admin/codigos/estado", 
                  AdminUsuariosController.verificar_estado_codigos_admin, 
                  methods=["GET"])

app.add_api_route("/api/admin/usuarios", 
                  AdminUsuariosController.crear_usuario, 
                  methods=["POST"])

app.add_api_route("/api/admin/usuarios/{usuario_id}", 
                  AdminUsuariosController.eliminar_usuario, 
                  methods=["DELETE"])  # NUEVO ENDPOINT

app.add_api_route("/api/admin/usuarios/{usuario_id}/convertir-paciente", 
                  AdminUsuariosController.convertir_a_paciente, 
                  methods=["POST"])  # NUEVO ENDPOINT

# Pacientes
app.add_api_route("/api/admin/pacientes", 
                  AdminUsuariosController.listar_pacientes, 
                  methods=["GET"])

app.add_api_route("/api/admin/pacientes", 
                  AdminUsuariosController.crear_paciente, 
                  methods=["POST"])

app.add_api_route("/api/admin/pacientes/{codigo_cita}", 
                  AdminUsuariosController.eliminar_paciente,  # Si creas esta función
                  methods=["DELETE"])  # OPCIONAL

# Historial médico
app.add_api_route("/api/admin/historial/{usuario_id}", 
                  AdminUsuariosController.obtener_historial_completo, 
                  methods=["GET"])

# Exportación
app.add_api_route("/api/admin/exportar", 
                  AdminUsuariosController.exportar_csv, 
                  methods=["GET"])

# Debug
app.add_api_route("/api/admin/debug", 
                  AdminUsuariosController.debug_archivo, 
                  methods=["POST"])

# RUTAS PARA ESTADOS
app.add_api_route("/api/admin/usuarios/{usuario_id}/estado", 
                  AdminUsuariosController.cambiar_estado_usuario, 
                  methods=["PUT"])

app.add_api_route("/api/admin/citas/{codigo_cita}/estado", 
                  AdminUsuariosController.cambiar_estado_cita, 
                  methods=["PUT"])

@app.get("/admin/panel-usuarios", response_class=HTMLResponse)
async def panel_usuarios(request: Request):
    """
    Panel principal de administración de usuarios
    """
    admin = AuthAdminController.verificar_sesion_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return templates_admin.TemplateResponse("panel_usuarios_admin.html", {
        "request": request,
        "admin": admin
    })


# ─────────────────────────────────────────────────────────────
# PANELES DE ADMINISTRADOR - SERVICIOS
# ─────────────────────────────────────────────────────────────

@app.get("/admin/panel-servicios", response_class=HTMLResponse)
async def panel_usuarios(request: Request):
    """
    Panel principal de administración de usuarios
    """
    admin = AuthAdminController.verificar_sesion_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return templates_admin.TemplateResponse("panel_servicios_admin.html", {
        "request": request,
        "admin": admin
    })




# ===== TERAPIAS =====
#esto dio error
# CORREGIR ESTA LÍNEA (probablemente línea 1069):
app.add_api_route("/api/admin/servicios/estadisticas", 
                  AdminServicioController.obtener_estadisticas_generales,  # CON "s" al final
                  methods=["GET"])

app.add_api_route("/api/admin/servicios/terapias", 
                  AdminServicioController.listar_terapias, 
                  methods=["GET"])

app.add_api_route("/api/admin/servicios/terapias/{codigo}", 
                  AdminServicioController.obtener_terapia, 
                  methods=["GET"])

app.add_api_route("/api/admin/servicios/terapias", 
                  AdminServicioController.crear_terapia, 
                  methods=["POST"])

app.add_api_route("/api/admin/servicios/terapias/{codigo}", 
                  AdminServicioController.actualizar_terapia, 
                  methods=["PUT"])

# ===== NUTRICIÓN =====
app.add_api_route("/api/admin/servicios/nutricion", 
                  AdminServicioController.listar_nutricion, 
                  methods=["GET"])

app.add_api_route("/api/admin/servicios/nutricion/{codigo}", 
                  AdminServicioController.obtener_nutricion, 
                  methods=["GET"])

app.add_api_route("/api/admin/servicios/nutricion", 
                  AdminServicioController.crear_nutricion, 
                  methods=["POST"])

app.add_api_route("/api/admin/servicios/nutricion/{codigo}", 
                  AdminServicioController.actualizar_nutricion, 
                  methods=["PUT"])

# ===== IMPLEMENTOS =====
app.add_api_route("/api/admin/servicios/implementos", 
                  AdminServicioController.listar_implementos, 
                  methods=["GET"])

app.add_api_route("/api/admin/servicios/implementos/{codigo}", 
                  AdminServicioController.obtener_implemento, 
                  methods=["GET"])

app.add_api_route("/api/admin/servicios/implementos", 
                  AdminServicioController.crear_implemento, 
                  methods=["POST"])

app.add_api_route("/api/admin/servicios/implementos/{codigo}", 
                  AdminServicioController.actualizar_implemento, 
                  methods=["PUT"])


# ─────────────────────────────────────────────────────────────
# PANELES DE ADMINISTRADOR - AGENDA
# ────────────────────────────────────────────────────────────────

@app.get("/admin/panel-agenda", response_class=HTMLResponse)
async def panel_usuarios(request: Request):
    """
    Panel principal de administración de usuarios
    """
    admin = AuthAdminController.verificar_sesion_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return templates_admin.TemplateResponse("panel_cita_admin.html", {
        "request": request,
        "admin": admin
    })

app.add_api_route("/api/admin/citas/estadisticas", 
                  AdminCitaController.obtener_estadisticas, 
                  methods=["GET"])

app.add_api_route("/api/admin/citas", 
                  AdminCitaController.listar_citas, 
                  methods=["GET"])

app.add_api_route("/api/admin/citas/{cita_id}", 
                  AdminCitaController.obtener_cita, 
                  methods=["GET"])

app.add_api_route("/api/admin/citas", 
                  AdminCitaController.crear_cita, 
                  methods=["POST"])

app.add_api_route("/api/admin/citas/{cita_id}", 
                  AdminCitaController.actualizar_cita, 
                  methods=["PUT"])

app.add_api_route("/api/admin/citas/{cita_id}/estado", 
                  AdminCitaController.cambiar_estado_cita, 
                  methods=["PATCH"])

app.add_api_route("/api/admin/citas/{cita_id}", 
                  AdminCitaController.eliminar_cita, 
                  methods=["DELETE"])

app.add_api_route("/api/admin/citas/semana", 
                  AdminCitaController.obtener_citas_semana, 
                  methods=["GET"])

# ─────────────────────────────────────────────────────────────
# PANELES DE ADMINISTRADOR - ANALITICAS
# ────────────────────────────────────────────────────────────────





@app.get("/admin/panel-analiticas", response_class=HTMLResponse)
async def panel_analiticas(request: Request):
    """
    Panel principal de analíticas
    """
    admin = AuthAdminController.verificar_sesion_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return templates_admin.TemplateResponse("panel_analiticas_admin.html", {
        "request": request,
        "admin": admin
    })

# En main.py - Asegúrate de tener TODAS estas rutas:

# Rutas de analíticas
app.add_api_route("/api/admin/analiticas/estadisticas", 
                  AdminAnaliticasController.obtener_estadisticas, 
                  methods=["GET"])

app.add_api_route("/api/admin/analiticas/graficos", 
                  AdminAnaliticasController.obtener_datos_graficos, 
                  methods=["POST"])

app.add_api_route("/api/admin/analiticas/servicios-populares", 
                  AdminAnaliticasController.obtener_servicios_populares, 
                  methods=["GET"])

app.add_api_route("/api/admin/analiticas/rendimiento-terapeutas", 
                  AdminAnaliticasController.obtener_rendimiento_terapeutas, 
                  methods=["GET"])

app.add_api_route("/api/admin/analiticas/top-terapeutas", 
                  AdminAnaliticasController.obtener_top_terapeutas, 
                  methods=["GET"])

app.add_api_route("/api/admin/analiticas/datos-financieros", 
                  AdminAnaliticasController.obtener_datos_financieros, 
                  methods=["GET"])

app.add_api_route("/api/admin/analiticas/tendencias", 
                  AdminAnaliticasController.obtener_tendencias, 
                  methods=["GET"])

app.add_api_route("/api/admin/analiticas/generar-reporte", 
                  AdminAnaliticasController.generar_reporte, 
                  methods=["POST"])

# Rutas adicionales para gráficos específicos
app.add_api_route("/api/admin/analiticas/usuarios-pacientes", 
                  AdminAnaliticasController.obtener_datos_usuario_paciente, 
                  methods=["GET"])

app.add_api_route("/api/admin/analiticas/productos-servicios-populares", 
                  AdminAnaliticasController.obtener_productos_servicios_populares, 
                  methods=["GET"])

# ─────────────────────────────────────────────────────────────
# PANELES DE ADMINISTRADOR - CORREOS
# ─────────────────────────────────────────────────────────────


@app.get("/admin/panel-correos", response_class=HTMLResponse)
async def panel_usuarios(request: Request):
    """
    Panel principal de administración de usuarios
    """
    admin = AuthAdminController.verificar_sesion_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return templates_admin.TemplateResponse("panel_correos_admin.html", {
        "request": request,
        "admin": admin
    })

# ─────────────────────────────────────────────────────────────
# PANELES DE ADMINISTRADOR - FISIOTERAPEUTAS
# ─────────────────────────────────────────────────────────────


@app.get("/admin/panel-fisio", response_class=HTMLResponse)
async def panel_usuarios(request: Request):
    """
    Panel principal de administración de usuarios
    """
    admin = AuthAdminController.verificar_sesion_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return templates_admin.TemplateResponse("panel_fisio_admin.html", {
        "request": request,
        "admin": admin
    })

app.add_api_route("/api/admin/fisio/estadisticas", 
                  AdminFisioController.obtener_estadisticas_fisio, 
                  methods=["GET"])

app.add_api_route("/api/admin/fisio/terapeutas", 
                  AdminFisioController.listar_terapeutas, 
                  methods=["GET"])

app.add_api_route("/api/admin/fisio/terapeutas/{codigo}", 
                  AdminFisioController.obtener_terapeuta, 
                  methods=["GET"])

app.add_api_route("/api/admin/fisio/terapeutas", 
                  AdminFisioController.crear_terapeuta, 
                  methods=["POST"])

app.add_api_route("/api/admin/fisio/terapeutas/{codigo}", 
                  AdminFisioController.actualizar_terapeuta, 
                  methods=["PUT"])

app.add_api_route("/api/admin/fisio/terapeutas/{codigo}/estado", 
                  AdminFisioController.cambiar_estado_terapeuta, 
                  methods=["PATCH"])

app.add_api_route("/api/admin/fisio/especializaciones", 
                  AdminFisioController.obtener_especializaciones, 
                  methods=["GET"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/test-db")
async def test_db():
    from bd.conexion_bd import get_db_connection, close_db_connection
    conn = get_db_connection()
    if conn:
        close_db_connection(conn)
        return {"database": "connected", "status": "ok"}
    else:
        return {"database": "disconnected", "status": "error"}

# ============================================
# ESTO YA LO TIENES (MANTENERLO)
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  
        port=PORT,        
        reload=False   
    )