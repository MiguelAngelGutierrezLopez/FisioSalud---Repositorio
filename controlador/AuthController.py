# controlador/AuthController.py (actualización)
import traceback
from fastapi.params import Form
from modelo.UsuarioModel import UsuarioModel
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, UploadFile

templates = Jinja2Templates(directory="./vista")

class AuthController:
    
    @staticmethod
    async def registrar_usuario(
        request: Request,
        nombre: str,
        apellido: str,
        genero: str,
        email: str,
        telefono: str,
        contraseña: str,
        contraseña_confirmada: str,
        ID: str,
        historial_medico: UploadFile = None
    ):
        """
        Controla el proceso completo de registro
        """
        try:
            print("📝 Iniciando registro de usuario...")
            
            # Validar contraseñas
            if contraseña != contraseña_confirmada:
                return templates.TemplateResponse(
                    "registro.html",
                    {"request": request, "error": "Las contraseñas no coinciden."}
                )

            # Procesar archivo médico si existe
            medical_file_path = None
            if historial_medico and historial_medico.filename:
                medical_file_path = UsuarioModel.guardar_archivo_medico(historial_medico)

            # Preparar datos para el modelo
            datos_usuario = {
                'nombre': nombre,
                'apellido': apellido,
                'genero': genero,
                'email': email,
                'telefono': telefono,
                'contraseña': contraseña,
                'contraseña_confirmada': contraseña_confirmada,
                'ID': ID,
                'medical_file_path': medical_file_path
            }

            print(f"📦 Datos del usuario: {datos_usuario}")

            # Llamar al modelo
            resultado, mensaje = UsuarioModel.crear_usuario(datos_usuario)
            
            if resultado:
                # Obtener el usuario recién creado e iniciar sesión automáticamente
                usuario_db = UsuarioModel.obtener_usuario_por_correo(email)
                
                if usuario_db:
                    # Guardar usuario en sesión
                    request.session['usuario'] = {
                        'id': usuario_db['ID'],
                        'nombre': f"{usuario_db['nombre']} {usuario_db['apellido']}",
                        'email': usuario_db['correo'],
                        'telefono': usuario_db.get('telefono', ''),
                        'genero': usuario_db.get('genero', ''),
                        'logged_in': True
                    }
                    
                    # Redirigir al panel principal
                    return RedirectResponse(url="/panel_citas", status_code=303)
                else:
                    # Si no se puede obtener el usuario, redirigir al login
                    return RedirectResponse(url="/login_user", status_code=303)
            else:
                return templates.TemplateResponse(
                    "registro.html",
                    {"request": request, "error": mensaje}
                )
                
        except Exception as e:
            print(f"❌ Error en controlador registrar_usuario: {e}")
            return templates.TemplateResponse(
                "registro.html",
                {"request": request, "error": "Error interno del servidor"}
            )
                
        
    @staticmethod
    async def validar_acceso(
        request: Request, 
        correo: str = Form(...), 
        contraseña: str = Form(...)
    ):
        usuario, mensaje = UsuarioModel.validar_login(correo, contraseña)
        
        if usuario:
            # Guardar usuario completo en sesión con flag logged_in
            request.session['usuario'] = {
                'id': usuario['ID'],
                'nombre': f"{usuario['nombre']} {usuario['apellido']}",
                'email': usuario['correo'],
                'telefono': usuario.get('telefono', ''),
                'genero': usuario.get('genero', ''),
                'logged_in': True
            }
            
            # VERIFICAR SI HAY REDIRECCIÓN PENDIENTE DESDE SERVICIOS
            redirect_url = request.session.get('redirect_after_login', '/panel_citas')
            
            # Limpiar las variables de redirección
            if 'redirect_after_login' in request.session:
                del request.session['redirect_after_login']
            if 'servicio_para_cita' in request.session:
                del request.session['servicio_para_cita']
            if 'login_message' in request.session:
                del request.session['login_message']
            
            print(f"✅ Login exitoso. Redirigiendo a: {redirect_url}")
            return RedirectResponse(url=redirect_url, status_code=303)

        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error_message": mensaje
            })

    @staticmethod
    def verificar_sesion_usuario(request: Request):
        """
        Verifica si el usuario tiene sesión activa
        """
        usuario = request.session.get('usuario')
        if not usuario or not usuario.get('logged_in'):
            return None
        return usuario

    @staticmethod
    async def cerrar_sesion(request: Request):
        """
        Cierra la sesión del usuario
        """
        try:
            usuario = request.session.get('usuario')
            email = usuario.get('email', 'Desconocido') if usuario else 'Desconocido'
            
            # Limpiar sesión
            request.session.clear()
            if 'usuario' in request.session:
                del request.session['usuario']
            
            request.session['success'] = 'Sesión cerrada correctamente'
            
            print(f"✅ Logout usuario exitoso: {email}")
            
            return RedirectResponse(url="/inicio", status_code=303)
            
        except Exception as e:
            request.session.clear()
            print(f"⚠️ Error durante logout usuario: {e}")
            return RedirectResponse(url="/inicio", status_code=303)
        

    @staticmethod
    def verificar_sesion_usuario(request: Request):
        """
        Verifica si el usuario tiene sesión activa con mejor manejo de errores
        """
        try:
            print("=" * 50)
            print("🔍 VERIFICANDO SESIÓN USUARIO")
            print("=" * 50)
            
            # Verificar si existe la sesión
            if not hasattr(request, 'session'):
                print("❌ No hay objeto session en request")
                return None
            
            # Mostrar todas las keys en la sesión
            session_keys = list(request.session.keys())
            print(f"📋 Keys en sesión: {session_keys}")
            
            usuario = request.session.get('usuario')
            print(f"👤 Datos de usuario en sesión: {usuario}")
            
            if not usuario:
                print("❌ No hay usuario en sesión")
                return None
            
            if not usuario.get('logged_in'):
                print("❌ Usuario no tiene logged_in=True")
                return None
            
            print(f"✅ SESIÓN VÁLIDA para: {usuario.get('email')}")
            print("=" * 50)
            return usuario
            
        except Exception as e:
            print(f"🔥 ERROR en verificar_sesion_usuario: {e}")
            print(traceback.format_exc())
            return None