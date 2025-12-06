# controlador/PasswordResetController.py
from modelo.EmailModel import EmailModel
from modelo.PasswordResetModel import PasswordResetModel
from modelo.UsuarioModel import UsuarioModel
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import RedirectResponse
import os

templates = Jinja2Templates(directory="./vista")

class PasswordResetController:
    
    @staticmethod
    async def solicitar_reset(request: Request, correo: str):
        """Procesa la solicitud de recuperación"""
        try:
            print(f"📧 Solicitud de reset para: {correo}")
            
            # Limpiar tokens expirados primero
            PasswordResetModel.limpiar_tokens_expirados()
            
            # Buscar usuario
            usuario = UsuarioModel.obtener_usuario_por_correo(correo)
            
            # Por seguridad, siempre damos misma respuesta
            mensaje_html = """
            <div class="mensaje-exito">
                <p>Si el correo existe en nuestro sistema, recibirás un enlace para restablecer tu contraseña.</p>
                <p>Revisa tu bandeja de entrada y también la carpeta de spam.</p>
            </div>
            """
            
            if not usuario:
                print(f"⚠️  Correo no encontrado: {correo}")
                return templates.TemplateResponse(
                    "olvidar_contraseña.html", {
                        "request": request,
                        "mensaje_html": mensaje_html
                    }
                )
            
            print(f"✅ Usuario encontrado: {usuario['nombre']}")
            
            # Generar y guardar token
            token = PasswordResetModel.generar_token()
            guardado = PasswordResetModel.guardar_token(usuario['ID'], token)
            
            if guardado:
                # Construir URL de reset
                base_url = str(request.base_url).rstrip('/')
                reset_url = f"{base_url}/resetear-contrasena/{token}"
                
                # Simular envío de correo (en producción integrar servicio real)
                enviado = EmailModel.enviar_correo_reset_password(
                    usuario['correo'], 
                    usuario['nombre'], 
                    reset_url
                )

                # Y puedes agregar logging:
                if enviado:
                    print(f"📧 Correo enviado a {usuario['correo']}")
                else:
                    print(f"⚠️  No se pudo enviar correo a {usuario['correo']} (pero el token fue creado)")
                
            
            return templates.TemplateResponse(
                "olvidar_contraseña.html", {
                    "request": request,
                    "mensaje_html": mensaje_html
                }
            )
            
        except Exception as e:
            print(f"❌ Error en solicitar_reset: {e}")
            return templates.TemplateResponse(
                "olvidar_contraseña.html", {
                    "request": request,
                    "error": "Error procesando la solicitud. Por favor, intenta nuevamente."
                }
            )
    
    @staticmethod
    async def validar_token_reset(request: Request, token: str):
        """Valida el token y muestra formulario de nueva contraseña"""
        try:
            token_data = PasswordResetModel.validar_token(token)
            
            if not token_data:
                error_html = """
                <div class="error-message">
                    <h4><i class="fas fa-exclamation-triangle"></i> Enlace Inválido</h4>
                    <p>Este enlace ha expirado o ya fue utilizado.</p>
                    <p><a href="/olvidar-contrasena" class="btn btn-outline">Solicitar nuevo enlace</a></p>
                </div>
                """
                return templates.TemplateResponse(
                    "reset_contraseña.html", {
                        "request": request,
                        "error_html": error_html,
                        "token_valido": False
                    }
                )
            
            print(f"✅ Token válido para: {token_data['correo']}")
            
            return templates.TemplateResponse(
                "reset_contraseña.html", {
                    "request": request,
                    "token_valido": True,
                    "token": token,
                    "email": token_data['correo'],
                    "nombre": token_data['nombre']
                }
            )
            
        except Exception as e:
            print(f"❌ Error validando token: {e}")
            error_html = """
            <div class="error-message">
                <h4><i class="fas fa-exclamation-triangle"></i> Error de Validación</h4>
                <p>Ha ocurrido un error al validar el enlace.</p>
                <p><a href="/olvidar-contrasena" class="btn btn-outline">Intentar nuevamente</a></p>
            </div>
            """
            return templates.TemplateResponse(
                "reset_contraseña.html", {
                    "request": request,
                    "error_html": error_html,
                    "token_valido": False
                }
            )
    
    @staticmethod
    async def actualizar_contrasena(
        request: Request, 
        token: str, 
        nueva_contrasena: str, 
        confirmar_contrasena: str
    ):
        """Actualiza la contraseña con el token"""
        try:
            # Validar que las contraseñas coincidan
            if nueva_contrasena != confirmar_contrasena:
                error_html = """
                <div class="error-message">
                    <h4><i class="fas fa-exclamation-circle"></i> Contraseñas no coinciden</h4>
                    <p>Las contraseñas ingresadas no son iguales. Por favor, inténtalo de nuevo.</p>
                </div>
                """
                return templates.TemplateResponse(
                    "reset_contraseña.html", {
                        "request": request,
                        "error_html": error_html,
                        "token_valido": True,
                        "token": token
                    }
                )
            
            # Validar longitud mínima de contraseña
            if len(nueva_contrasena) < 6:
                error_html = """
                <div class="error-message">
                    <h4><i class="fas fa-exclamation-circle"></i> Contraseña muy corta</h4>
                    <p>La contraseña debe tener al menos 6 caracteres.</p>
                </div>
                """
                return templates.TemplateResponse(
                    "reset_contraseña.html", {
                        "request": request,
                        "error_html": error_html,
                        "token_valido": True,
                        "token": token
                    }
                )
            
            # Validar token
            token_data = PasswordResetModel.validar_token(token)
            if not token_data:
                error_html = """
                <div class="error-message">
                    <h4><i class="fas fa-exclamation-triangle"></i> Enlace Expirado</h4>
                    <p>Este enlace ha expirado. Solicita uno nuevo.</p>
                </div>
                """
                return templates.TemplateResponse(
                    "reset_contraseña.html", {
                        "request": request,
                        "error_html": error_html,
                        "token_valido": False
                    }
                )
            
            # Actualizar contraseña
            actualizado = PasswordResetModel.actualizar_contrasena(
                token_data['usuario_id'], 
                nueva_contrasena
            )
            
            if actualizado:
                # Marcar token como usado
                PasswordResetModel.marcar_token_usado(token_data['id'])
                
                print(f"✅ Contraseña actualizada para: {token_data['correo']}")
                
                # Guardar mensaje de éxito en sesión
                request.session['success_message'] = "¡Contraseña actualizada exitosamente! Ya puedes iniciar sesión con tu nueva contraseña."
                
                # Redirigir al login
                return RedirectResponse(url="/login_user", status_code=303)
            else:
                raise Exception("Error al actualizar contraseña en BD")
                
        except Exception as e:
            print(f"❌ Error actualizando contraseña: {e}")
            error_html = """
            <div class="error-message">
                <h4><i class="fas fa-exclamation-triangle"></i> Error del Sistema</h4>
                <p>No pudimos actualizar tu contraseña. Por favor, intenta nuevamente.</p>
                <p><a href="/olvidar-contrasena" class="btn btn-outline">Solicitar nuevo enlace</a></p>
            </div>
            """
            return templates.TemplateResponse(
                "reset_contraseña.html", {
                    "request": request,
                    "error_html": error_html,
                    "token_valido": False
                }
            )
    
    @staticmethod
    async def simular_envio_correo(email, nombre, reset_url):
        """Simula el envío de correo (en producción reemplazar con servicio real)"""
        print("="*60)
        print("📧 [SIMULACIÓN] CORREO DE RECUPERACIÓN ENVIADO")
        print("="*60)
        print(f"Destinatario: {nombre} <{email}>")
        print(f"Asunto: Restablecimiento de contraseña - FisioSalud")
        print("-"*60)
        print(f"Enlace de restablecimiento: {reset_url}")
        print("="*60)
    
        return True
    
    @staticmethod
    async def enviar_correo_real(email, nombre, reset_url):
        """Envía correo real usando SMTP"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Configuración (ajustar con tus credenciales)
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SMTP_USER = "tu_email@gmail.com"
        SMTP_PASSWORD = "tu_contraseña_app"
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Restablecimiento de contraseña - FisioSalud"
        msg['From'] = SMTP_USER
        msg['To'] = email
        
        # Contenido HTML del correo
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd;">
                <h2 style="color: #0A2540;">Restablecer contraseña</h2>
                <p>Hola {nombre},</p>
                <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
                <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #0A2540; color: white; 
                    padding: 12px 24px; text-decoration: none; border-radius: 4px;">
                    Restablecer Contraseña
                    </a>
                </p>
                <p>Este enlace expirará en 1 hora.</p>
                <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    FisioSalud - Centro de Bienestar Físico
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"✅ Correo enviado a {email}")
            return True
        except Exception as e:
            print(f"❌ Error enviando correo: {e}")
            return False