import datetime
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import List, Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailModel:
    """
    Modelo para envío de correos electrónicos usando Mailtrap SMTP
    """
    
    # ==============================================
    # CONFIGURACIÓN MAILTRAP (SANDBOX - SOLO PRUEBAS)
    # ==============================================
    SMTP_SERVER = "sandbox.smtp.mailtrap.io"
    SMTP_PORT = 2525
    SMTP_USERNAME = "931d6e50852e8e"  # Tu username de Mailtrap
    SMTP_PASSWORD = "f65430ecf5e4ae"  # ⚠️ REEMPLAZA CON TU PASSWORD REAL ⚠️
    
    # ==============================================
    # CONFIGURACIÓN DEL REMITENTE
    # ==============================================
    FROM_EMAIL = "no-reply@fisiosalud.com"
    FROM_NAME = "FisioSalud"
    
    # ==============================================
    # PLANTILLAS DE CORREO
    # ==============================================
    
    @staticmethod
    def _plantilla_reset_password(nombre, reset_url):
        """Genera el HTML para el correo de recuperación"""
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Restablecer Contraseña</title>
            <style>
                body {{
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #0F172A;
                    background-color: #F8FAFC;
                    margin: 0;
                    padding: 20px;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #FFFFFF;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .email-header {{
                    background: linear-gradient(135deg, #0A2540 0%, #1E3A5F 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .email-header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 700;
                }}
                .email-header p {{
                    margin: 5px 0 0;
                    opacity: 0.9;
                    font-size: 14px;
                }}
                .email-content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    color: #0A2540;
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #475569;
                    margin-bottom: 30px;
                    font-size: 15px;
                }}
                .reset-button {{
                    display: block;
                    width: fit-content;
                    margin: 30px auto;
                    background-color: #00A3FF;
                    color: white;
                    text-decoration: none;
                    padding: 14px 32px;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 16px;
                    text-align: center;
                    transition: all 0.3s ease;
                }}
                .reset-button:hover {{
                    background-color: #0088D4;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 163, 255, 0.3);
                }}
                .warning-box {{
                    background-color: #FFFBEB;
                    border: 1px solid #FDE68A;
                    border-radius: 6px;
                    padding: 16px;
                    margin: 25px 0;
                }}
                .warning-title {{
                    color: #92400E;
                    font-weight: 600;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .warning-text {{
                    color: #B45309;
                    font-size: 14px;
                }}
                .direct-link {{
                    background-color: #F1F5F9;
                    border-radius: 6px;
                    padding: 15px;
                    margin: 20px 0;
                    word-break: break-all;
                    font-family: monospace;
                    font-size: 13px;
                    color: #0A2540;
                }}
                .email-footer {{
                    background-color: #F8FAFC;
                    padding: 25px 30px;
                    border-top: 1px solid #E2E8F0;
                    text-align: center;
                }}
                .footer-logo {{
                    color: #0A2540;
                    font-weight: 700;
                    font-size: 18px;
                    margin-bottom: 10px;
                }}
                .footer-info {{
                    color: #64748B;
                    font-size: 13px;
                    line-height: 1.5;
                }}
                .footer-copyright {{
                    color: #94A3B8;
                    font-size: 12px;
                    margin-top: 15px;
                }}
                @media (max-width: 600px) {{
                    .email-content {{
                        padding: 25px 20px;
                    }}
                    .reset-button {{
                        width: 100%;
                        text-align: center;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <!-- Header -->
                <div class="email-header">
                    <h1>FisioSalud</h1>
                    <p>Tu centro de bienestar físico</p>
                </div>
                
                <!-- Contenido -->
                <div class="email-content">
                    <div class="greeting">Hola {nombre},</div>
                    
                    <div class="message">
                        Hemos recibido una solicitud para restablecer tu contraseña en FisioSalud.
                        Haz clic en el botón a continuación para crear una nueva contraseña.
                    </div>
                    
                    <a href="{reset_url}" class="reset-button">
                        Restablecer Contraseña
                    </a>
                    
                    <!-- Advertencia -->
                    <div class="warning-box">
                        <div class="warning-title">
                            <span>⚠️</span>
                            <span>Enlace válido por 1 hora</span>
                        </div>
                        <div class="warning-text">
                            Por seguridad, este enlace expirará en 60 minutos. Si no solicitaste este cambio, puedes ignorar este correo.
                        </div>
                    </div>
                    
                    <!-- Enlace directo -->
                    <div class="message">
                        Si el botón no funciona, copia y pega este enlace en tu navegador:
                    </div>
                    <div class="direct-link">
                        {reset_url}
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="email-footer">
                    <div class="footer-logo">FisioSalud</div>
                    <div class="footer-info">
                        Av. Salud 123, Ciudad • Tel: (123) 456-7890<br>
                        Email: info@fisiosalud.com • Horario: Lun-Vie 8am-8pm
                    </div>
                    <div class="footer-copyright">
                        © 2023 FisioSalud. Todos los derechos reservados.<br>
                        Este es un correo automático, por favor no respondas.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _plantilla_texto_plano(nombre, reset_url):
        """Genera la versión en texto plano del correo"""
        return f"""Hola {nombre},

    Hemos recibido una solicitud para restablecer tu contraseña en FisioSalud.

    Para crear una nueva contraseña, visita el siguiente enlace:
    {reset_url}

    Este enlace expirará en 1 hora por seguridad.

    Si no solicitaste este cambio, puedes ignorar este correo.

    ---
    FisioSalud - Centro de Bienestar Físico
    Av. Salud 123, Ciudad
    Tel: (123) 456-7890
    info@fisiosalud.com
    """
    
    # ==============================================
    # MÉTODOS PRINCIPALES
    # ==============================================
    
    @staticmethod
    def enviar_correo_reset_password(destinatario_email, destinatario_nombre, reset_url):
        """
        Envía correo de recuperación de contraseña
        
        Args:
            destinatario_email (str): Email del destinatario
            destinatario_nombre (str): Nombre del destinatario
            reset_url (str): URL para restablecer contraseña
            
        Returns:
            bool: True si se envió correctamente, False si hubo error
        """
        try:
            logger.info(f"📧 Preparando correo para: {destinatario_email}")
            
            # 1. Crear mensaje MIME
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Restablecimiento de contraseña - FisioSalud"
            msg['From'] = f"{EmailModel.FROM_NAME} <{EmailModel.FROM_EMAIL}>"
            msg['To'] = destinatario_email
            msg['X-Priority'] = '1'  # Alta prioridad
            
            # 2. Crear versiones del contenido
            texto_plano = EmailModel._plantilla_texto_plano(destinatario_nombre, reset_url)
            html = EmailModel._plantilla_reset_password(destinatario_nombre, reset_url)
            
            # 3. Adjuntar ambas versiones
            parte_texto = MIMEText(texto_plano, 'plain', 'utf-8')
            parte_html = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(parte_texto)
            msg.attach(parte_html)
            
            # 4. Conectar y enviar vía SMTP
            logger.info(f"🔌 Conectando a {EmailModel.SMTP_SERVER}:{EmailModel.SMTP_PORT}")
            
            server = smtplib.SMTP(EmailModel.SMTP_SERVER, EmailModel.SMTP_PORT)
            server.starttls()  # Habilitar encriptación TLS
            
            logger.info(f"🔑 Autenticando con usuario: {EmailModel.SMTP_USERNAME}")
            server.login(EmailModel.SMTP_USERNAME, EmailModel.SMTP_PASSWORD)
            
            logger.info(f"📤 Enviando correo a: {destinatario_email}")
            server.sendmail(
                EmailModel.FROM_EMAIL,
                destinatario_email,
                msg.as_string()
            )
            
            server.quit()
            
            logger.info(f"✅ Correo enviado exitosamente a: {destinatario_email}")
            logger.info(f"🔗 Enlace: {reset_url}")
            logger.info("📋 Verifica el correo en: https://mailtrap.io → Sandboxes → My Sandbox")
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ Error de autenticación SMTP: {e}")
            logger.error("Verifica tu usuario y contraseña de Mailtrap en EmailModel.py")
            return False
            
        except smtplib.SMTPException as e:
            logger.error(f"❌ Error SMTP: {e}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return False
    
    @staticmethod
    def test_conexion_smtp():
        """
        Prueba la conexión SMTP con Mailtrap
        
        Returns:
            bool: True si la conexión es exitosa, False si hay error
        """
        try:
            logger.info(f"🔍 Probando conexión a {EmailModel.SMTP_SERVER}:{EmailModel.SMTP_PORT}")
            
            server = smtplib.SMTP(EmailModel.SMTP_SERVER, EmailModel.SMTP_PORT)
            server.starttls()
            
            logger.info(f"🔑 Probando autenticación con: {EmailModel.SMTP_USERNAME}")
            server.login(EmailModel.SMTP_USERNAME, EmailModel.SMTP_PASSWORD)
            
            server.quit()
            
            logger.info("✅ Conexión SMTP exitosa con Mailtrap")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Autenticación fallida. Verifica:")
            logger.error(f"   Usuario: {EmailModel.SMTP_USERNAME}")
            logger.error(f"   Password: {'*' * len(EmailModel.SMTP_PASSWORD)}")
            logger.error("   ⚠️ Asegúrate de usar la contraseña REAL (no los asteriscos)")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False
    
    @staticmethod
    def enviar_correo_prueba():
        """
        Envía un correo de prueba a la bandeja de Mailtrap
        """
        test_email = "test@fisiosalud.com"  # Puede ser cualquier email
        test_nombre = "Usuario de Prueba"
        test_url = "http://127.0.0.1:8000/resetear-contrasena/test-token-123"
        
        logger.info("🚀 Enviando correo de prueba...")
        return EmailModel.enviar_correo_reset_password(test_email, test_nombre, test_url)
    # En controlador/CitaController.py, modificar el método agendar_cita:




    @staticmethod
    def enviar_correo_confirmacion_cita(datos_cita: Dict[str, Any], emails_destinatarios: List[str]) -> Dict[str, Any]:
        """
        Envía correos de confirmación de cita con diseño serio y profesional
        """
        resultados = []
        emails_exitosos = 0
        
        # Formatear fecha y hora
        fecha_formateada = ""
        hora_formateada = ""
        if datos_cita.get('fecha_cita'):
            try:
                fecha_obj = datetime.datetime.strptime(datos_cita['fecha_cita'], '%Y-%m-%d')
                fecha_formateada = fecha_obj.strftime('%d de %B de %Y')
            except:
                fecha_formateada = datos_cita.get('fecha_cita', 'Fecha no especificada')
        
        if datos_cita.get('hora_cita'):
            try:
                hora_obj = datetime.datetime.strptime(datos_cita['hora_cita'], '%H:%M')
                hora_formateada = hora_obj.strftime('%I:%M %p').lstrip('0')
            except:
                hora_formateada = datos_cita.get('hora_cita', 'Hora no especificada')
        
        # Plantilla HTML - Estilo serio y profesional
        html_template = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmación de Cita | FisioSalud</title>
            <style>
                :root {{
                    --primary: #0A2540;
                    --primary-dark: #061A2C;
                    --secondary: #00A3FF;
                    --accent: #00D4AA;
                    --light: #FFFFFF;
                    --light-gray: #F8FAFC;
                    --gray: #64748B;
                    --dark: #0F172A;
                    --border-radius: 8px;
                    --border-radius-sm: 4px;
                    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                }}

                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
                    line-height: 1.6;
                    color: var(--dark);
                    background-color: #fafafa;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }}

                .email-container {{
                    max-width: 620px;
                    margin: 0 auto;
                    background: var(--light);
                    border-radius: var(--border-radius);
                    overflow: hidden;
                    box-shadow: var(--shadow);
                }}

                /* Header minimalista */
                .email-header {{
                    background: var(--primary);
                    color: white;
                    padding: 32px;
                    border-bottom: 4px solid var(--secondary);
                }}

                .header-content {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }}

                .logo-section {{
                    display: flex;
                    align-items: center;
                    gap: 16px;
                }}

                .logo-icon {{
                    width: 48px;
                    height: 48px;
                    background: white;
                    border-radius: var(--border-radius-sm);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: var(--primary);
                    font-weight: 700;
                    font-size: 18px;
                }}

                .logo-text {{
                    font-size: 24px;
                    font-weight: 700;
                    color: white;
                }}

                .document-type {{
                    font-size: 12px;
                    font-weight: 600;
                    color: rgba(255, 255, 255, 0.8);
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                /* Contenido principal */
                .email-content {{
                    padding: 40px;
                }}

                .document-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 32px;
                    padding-bottom: 24px;
                    border-bottom: 1px solid var(--light-gray);
                }}

                .document-info {{
                    flex: 1;
                }}

                .document-title {{
                    font-size: 24px;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 8px;
                }}

                .document-subtitle {{
                    color: var(--gray);
                    font-size: 14px;
                    font-weight: 400;
                }}

                .document-code {{
                    text-align: right;
                    min-width: 180px;
                }}

                .code-label {{
                    display: block;
                    color: var(--gray);
                    font-size: 12px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                    margin-bottom: 4px;
                }}

                .code-value {{
                    font-size: 22px;
                    font-weight: 700;
                    color: var(--primary);
                    font-family: 'Courier New', monospace;
                    letter-spacing: 1px;
                }}

                /* Saludo */
                .greeting {{
                    font-size: 16px;
                    color: var(--dark);
                    margin-bottom: 32px;
                    line-height: 1.6;
                }}

                /* Detalles de la cita */
                .appointment-details {{
                    margin-bottom: 40px;
                }}

                .details-title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 20px;
                    padding-bottom: 12px;
                    border-bottom: 1px solid var(--light-gray);
                }}

                .details-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                }}

                .detail-item {{
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                }}

                .detail-label {{
                    color: var(--gray);
                    font-size: 13px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                }}

                .detail-value {{
                    color: var(--dark);
                    font-size: 15px;
                    font-weight: 500;
                }}

                /* Información importante */
                .important-info {{
                    background: var(--light-gray);
                    border-left: 3px solid var(--secondary);
                    padding: 24px;
                    margin: 32px 0;
                    border-radius: 0 var(--border-radius-sm) var(--border-radius-sm) 0;
                }}

                .important-title {{
                    font-size: 16px;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 16px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}

                .important-list {{
                    list-style: none;
                }}

                .important-list li {{
                    margin-bottom: 12px;
                    padding-left: 20px;
                    position: relative;
                    color: var(--dark);
                    font-size: 14px;
                    line-height: 1.5;
                }}

                .important-list li:before {{
                    content: "—";
                    color: var(--secondary);
                    position: absolute;
                    left: 0;
                }}

                /* Instrucciones específicas */
                .specific-instructions {{
                    background: #F9FAFB;
                    border: 1px solid #E5E7EB;
                    border-radius: var(--border-radius-sm);
                    padding: 24px;
                    margin: 32px 0;
                }}

                .instructions-title {{
                    font-size: 16px;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 16px;
                }}

                .instructions-content {{
                    color: var(--dark);
                    font-size: 14px;
                    line-height: 1.6;
                    white-space: pre-line;
                }}

                /* Información del centro */
                .center-info {{
                    border-top: 1px solid var(--light-gray);
                    padding-top: 32px;
                    margin-top: 40px;
                }}

                .center-title {{
                    font-size: 16px;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 24px;
                }}

                .center-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 24px;
                }}

                .center-item {{
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                }}

                .center-icon {{
                    color: var(--secondary);
                    font-size: 16px;
                    width: 24px;
                    text-align: center;
                    flex-shrink: 0;
                }}

                .center-content {{
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }}

                .center-label {{
                    color: var(--gray);
                    font-size: 12px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                }}

                .center-value {{
                    color: var(--dark);
                    font-size: 14px;
                    font-weight: 500;
                }}

                /* Footer */
                .email-footer {{
                    background: var(--primary-dark);
                    color: white;
                    padding: 32px 40px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }}

                .footer-content {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}

                .footer-text {{
                    font-size: 13px;
                    opacity: 0.8;
                }}

                .footer-disclaimer {{
                    font-size: 11px;
                    opacity: 0.6;
                    margin-top: 16px;
                    padding-top: 16px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }}

                /* Responsive */
                @media (max-width: 640px) {{
                    .email-content, .email-footer {{
                        padding: 24px;
                    }}
                    
                    .header-content {{
                        flex-direction: column;
                        align-items: flex-start;
                        gap: 16px;
                    }}
                    
                    .document-header {{
                        flex-direction: column;
                        gap: 16px;
                    }}
                    
                    .document-code {{
                        text-align: left;
                    }}
                    
                    .details-grid, .center-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .footer-content {{
                        flex-direction: column;
                        align-items: flex-start;
                        gap: 16px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <!-- Header minimalista -->
                <div class="email-header">
                    <div class="header-content">
                        <div class="logo-section">
                            <div class="logo-icon">FS</div>
                            <div class="logo-text">FisioSalud</div>
                        </div>
                        <div class="document-type">Confirmación de Cita</div>
                    </div>
                </div>

                <!-- Contenido principal -->
                <div class="email-content">
                    <!-- Encabezado del documento -->
                    <div class="document-header">
                        <div class="document-info">
                            <h1 class="document-title">Confirmación de Cita Terapéutica</h1>
                            <p class="document-subtitle">Documento oficial - Por favor conserve para sus registros</p>
                        </div>
                        <div class="document-code">
                            <span class="code-label">Referencia</span>
                            <div class="code-value">{datos_cita.get('codigo_cita', 'FS-XXXX')}</div>
                        </div>
                    </div>

                    <!-- Saludo formal -->
                    <p class="greeting">
                        Señor(a) {datos_cita.get('nombre_paciente', 'Paciente')},<br>
                        Se confirma la programación de su sesión terapéutica en FisioSalud.
                    </p>

                    <!-- Detalles de la cita -->
                    <div class="appointment-details">
                        <h2 class="details-title">Detalles de la Intervención</h2>
                        <div class="details-grid">
                            <div class="detail-item">
                                <span class="detail-label">Servicio</span>
                                <span class="detail-value">{datos_cita.get('servicio', 'No especificado')}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Terapeuta Asignado</span>
                                <span class="detail-value">{datos_cita.get('terapeuta_designado', 'Por asignar')}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Fecha</span>
                                <span class="detail-value">{fecha_formateada}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Hora</span>
                                <span class="detail-value">{hora_formateada}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Modalidad</span>
                                <span class="detail-value">{datos_cita.get('modalidad', 'Presencial')}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Valor</span>
                                <span class="detail-value">${datos_cita.get('precio', 'Por confirmar')}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Información importante -->
                    <div class="important-info">
                        <h3 class="important-title">Instrucciones Protocolarias</h3>
                        <ul class="important-list">
                            <li>Presentarse 15 minutos antes del horario programado para documentación inicial</li>
                            <li>Traer identificación oficial y documentos médicos relevantes</li>
                            <li>Utilizar vestimenta adecuada para evaluación y tratamiento físico</li>
                            <li>Informar cualquier condición médica o medicación actual previamente</li>
                            <li>Cancelaciones requieren 24 horas de anticipación para reprogramación</li>
                        </ul>
                    </div>

                    <!-- Instrucciones específicas -->
                    <div class="specific-instructions">
                        <h3 class="instructions-title">Indicaciones Específicas</h3>
                        <div class="instructions-content">
                            {datos_cita.get('recomendaciones_precita', 'Proceder según protocolo estándar de preparación.')}
                        </div>
                    </div>

                    <!-- Información del centro -->
                    <div class="center-info">
                        <h3 class="center-title">Información del Centro</h3>
                        <div class="center-grid">
                            <div class="center-item">
                                <div class="center-icon">📍</div>
                                <div class="center-content">
                                    <span class="center-label">Ubicación</span>
                                    <span class="center-value">Av. Salud 123, Ciudad</span>
                                </div>
                            </div>
                            
                            <div class="center-item">
                                <div class="center-icon">📞</div>
                                <div class="center-content">
                                    <span class="center-label">Teléfono</span>
                                    <span class="center-value">(123) 456-7890</span>
                                </div>
                            </div>
                            
                            <div class="center-item">
                                <div class="center-icon">✉️</div>
                                <div class="center-content">
                                    <span class="center-label">Correo Electrónico</span>
                                    <span class="center-value">contacto@fisiosalud.com</span>
                                </div>
                            </div>
                            
                            <div class="center-item">
                                <div class="center-icon">⏰</div>
                                <div class="center-content">
                                    <span class="center-label">Horario de Atención</span>
                                    <span class="center-value">Lun-Vie: 8:00 - 20:00</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Notas adicionales si existen -->
                    {datos_cita.get('notas_adicionales') and datos_cita['notas_adicionales'].strip() != '' and f'''
                    <div style="margin-top: 24px; padding: 20px; background: #F8FAFC; border-radius: var(--border-radius-sm); border: 1px solid #E2E8F0;">
                        <h4 style="font-size: 15px; font-weight: 600; color: var(--primary); margin-bottom: 12px;">
                            Observaciones Adicionales
                        </h4>
                        <p style="color: var(--dark); font-size: 14px; line-height: 1.5;">
                            {datos_cita.get('notas_adicionales')}
                        </p>
                    </div>
                    ''' or ''}
                </div>

                <!-- Footer -->
                <div class="email-footer">
                    <div class="footer-content">
                        <div>
                            <p class="footer-text">FisioSalud - Centro Especializado en Rehabilitación Integral</p>
                            <p class="footer-text">Documento generado automáticamente el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                        </div>
                        <div class="footer-disclaimer">
                            Este es un correo automático. No responda a este mensaje.<br>
                            Para consultas o modificaciones utilice los canales oficiales.
                            © {datetime.datetime.now().year} FisioSalud. Todos los derechos reservados.
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versión de texto plano - Formato serio
        text_template = f"""
        ================================================================================
                                    FISIOSALUD
                            CONFIRMACIÓN DE CITA TERAPÉUTICA
        ================================================================================

        Referencia: {datos_cita.get('codigo_cita', 'FS-XXXX')}
        Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}

        Señor(a) {datos_cita.get('nombre_paciente', 'Paciente')},

        Se confirma la programación de su sesión terapéutica en FisioSalud.

        DETALLES DE LA INTERVENCIÓN
        --------------------------------------------------------------------------------
        Servicio: {datos_cita.get('servicio', 'No especificado')}
        Terapeuta Asignado: {datos_cita.get('terapeuta_designado', 'Por asignar')}
        Fecha: {fecha_formateada}
        Hora: {hora_formateada}
        Modalidad: {datos_cita.get('modalidad', 'Presencial')}
        Valor: ${datos_cita.get('precio', 'Por confirmar')}

        INSTRUCCIONES PROTOCOLARIAS
        --------------------------------------------------------------------------------
        1. Presentarse 15 minutos antes del horario programado
        2. Traer identificación oficial y documentos médicos
        3. Utilizar vestimenta adecuada para evaluación física
        4. Informar condiciones médicas o medicación actual
        5. Cancelaciones requieren 24 horas de anticipación

        INDICACIONES ESPECÍFICAS
        --------------------------------------------------------------------------------
        {datos_cita.get('recomendaciones_precita', 'Proceder según protocolo estándar.')}

        {datos_cita.get('notas_adicionales') and f'OBSERVACIONES ADICIONALES: {datos_cita["notas_adicionales"]}' or ''}

        INFORMACIÓN DEL CENTRO
        --------------------------------------------------------------------------------
        Ubicación: Av. Salud 123, Ciudad
        Teléfono: (123) 456-7890
        Correo: contacto@fisiosalud.com
        Horario: Lun-Vie: 8:00 - 20:00

        --------------------------------------------------------------------------------
        FisioSalud - Centro Especializado en Rehabilitación Integral
        Documento generado automáticamente. No responda a este mensaje.
        Para consultas utilice los canales oficiales.
        © {datetime.datetime.now().year} FisioSalud. Todos los derechos reservados.
        ================================================================================
        """
        
        for email in emails_destinatarios:
            try:
                # Crear mensaje
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f'Confirmación Cita {datos_cita.get("codigo_cita", "")} | FisioSalud'
                msg['From'] = f'{EmailModel.FROM_NAME} <{EmailModel.FROM_EMAIL}>'
                msg['To'] = email
                
                # Adjuntar versiones HTML y texto
                part1 = MIMEText(text_template, 'plain', 'utf-8')
                part2 = MIMEText(html_template, 'html', 'utf-8')
                
                msg.attach(part1)
                msg.attach(part2)
                
                # Enviar correo
                with smtplib.SMTP(EmailModel.SMTP_SERVER, EmailModel.SMTP_PORT) as server:
                    server.starttls()
                    server.login(EmailModel.SMTP_USERNAME, EmailModel.SMTP_PASSWORD)
                    server.send_message(msg)
                
                resultados.append({
                    "email": email,
                    "estado": "enviado",
                    "timestamp": datetime.datetime.now().isoformat()
                })
                emails_exitosos += 1
                logger.info(f"✅ Correo profesional enviado exitosamente a: {email}")
                
            except Exception as e:
                resultados.append({
                    "email": email,
                    "estado": "error",
                    "error": str(e),
                    "timestamp": datetime.datetime.now().isoformat()
                })
                logger.error(f"❌ Error enviando correo profesional a {email}: {e}")
        
        return {
            "total_enviados": len(emails_destinatarios),
            "exitosos": emails_exitosos,
            "fallidos": len(emails_destinatarios) - emails_exitosos,
            "detalles": resultados
        }
    
    @staticmethod
    def enviar_correo_simple(destinatario: str, asunto: str, cuerpo_html: str, cuerpo_texto: str = "") -> bool:
        """
        Envía un correo simple a un destinatario
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = asunto
            msg['From'] = f'{EmailModel.FROM_NAME} <{EmailModel.FROM_EMAIL}>'
            msg['To'] = destinatario
            
            # Adjuntar versiones
            if cuerpo_texto:
                part1 = MIMEText(cuerpo_texto, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(cuerpo_html, 'html')
            msg.attach(part2)
            
            # Enviar
            with smtplib.SMTP(EmailModel.SMTP_SERVER, EmailModel.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailModel.SMTP_USERNAME, EmailModel.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Correo enviado a {destinatario}: {asunto}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando correo a {destinatario}: {e}")
            return False


    @staticmethod
    def _cargar_plantilla_finalizacion(servicio: str) -> Dict:
        """
        Carga la plantilla específica para finalización de terapia desde el JSON único
        """
        try:
            # Ruta al archivo JSON único
            ruta_json = "terapia_codigo.json"
            
            if not os.path.exists(ruta_json):
                print(f"❌ Archivo de terapias no encontrado: {ruta_json}")
                return None
            
            # Cargar el archivo JSON completo
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos_terapias = json.load(f)
            
            # Buscar la plantilla para este servicio
            servicio_lower = servicio.lower().strip()
            
            # Mapeo de nombres de servicio a códigos de terapia
            # Puedes ajustar estos mapeos según cómo se llamen los servicios en tu sistema
            mapeo_nombres = {
                "masaje relajante": "12AB34",
                "masaje_relajante": "12AB34",
                "relajante": "12AB34",
                "terapia de estiramientos": "23WE45",
                "estiramientos": "23WE45",
                "rehabilitación deportiva": "56DF12",
                "deportiva": "56DF12",
                "rehabilitacion deportiva": "56DF12",
                "rehabilitación post-quirúrgica": "65AF31",
                "postquirurgica": "65AF31",
                "post-quirurgica": "65AF31",
                "punción seca": "67HH34",
                "puncion seca": "67HH34",
                "vendaje neuromuscular": "67RE23",
                "kinesiotape": "67RE23",
                "terapia miofascial": "75KE23",
                "miofascial": "75KE23",
                "masaje terapéutico": "76BG11",
                "masaje_terapeutico": "76BG11",
                "terapia craneosacral": "765Q64",
                "craneosacral": "765Q64",
                "drenaje linfático manual": "865F14",
                "linfático": "865F14",
                "electroterapia avanzada": "87FT88",
                "electroterapia": "87FT88",
                "terapia neural": "90AS12",
                "neural": "90AS12"
            }
            
            # Buscar por mapeo de nombres
            codigo_terapia = None
            for nombre_key, codigo in mapeo_nombres.items():
                if nombre_key in servicio_lower:
                    codigo_terapia = codigo
                    break
            
            # Si no se encuentra por mapeo, buscar directamente en el JSON
            if not codigo_terapia:
                for terapia in datos_terapias.get('plantillas_finalizacion', []):
                    # Buscar coincidencias parciales
                    if (terapia['terapia_nombre'].lower() in servicio_lower or 
                        servicio_lower in terapia['terapia_nombre'].lower()):
                        return terapia
            
            # Buscar por código de terapia si se encontró
            if codigo_terapia:
                for terapia in datos_terapias.get('plantillas_finalizacion', []):
                    if terapia['terapia_codigo'] == codigo_terapia:
                        return terapia
            
            # Si no se encuentra ninguna coincidencia, usar la primera como genérica
            print(f"⚠️ No se encontró plantilla específica para: {servicio}")
            print(f"📋 Usando plantilla genérica")
            
            # Puedes retornar una plantilla genérica o la primera disponible
            if datos_terapias.get('plantillas_finalizacion'):
                terapia_generica = datos_terapias['plantillas_finalizacion'][0].copy()
                terapia_generica['terapia_nombre'] = servicio
                terapia_generica['asunto_correo'] = f"¡Felicidades por completar tu terapia en FisioSalud! 🎉"
                terapia_generica['mensaje_cuerpo'] = f"""Estimado/a [NOMBRE_PACIENTE],

¡Enhorabuena! Has completado exitosamente tu tratamiento de **{servicio}** en FisioSalud.

Tu dedicación durante el proceso ha sido ejemplar. Te recomendamos continuar con los ejercicios y recomendaciones proporcionados durante tus sesiones para mantener los beneficios alcanzados.

Recuerda que en FisioSalud siempre estaremos aquí para apoyarte en tu bienestar.

Atentamente,
El Equipo de FisioSalud"""
                return terapia_generica
            
            return None
                
        except Exception as e:
            print(f"❌ Error cargando plantilla de finalización para '{servicio}': {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _plantilla_cancelacion_finalizacion_terapia(datos_cita: Dict, fecha_formateada: str, hora_formateada: str, terapia_info: Dict) -> str:
        """Plantilla HTML para finalización de terapia exitosa - ESTILO FISIOSALUD"""
        
        if terapia_info:
            # Usar plantilla personalizada del JSON
            mensaje_cuerpo = terapia_info['mensaje_cuerpo'].replace('[NOMBRE_PACIENTE]', datos_cita.get('nombre_paciente', 'Paciente'))
            mensaje_cuerpo = mensaje_cuerpo.replace('[NOMBRE_CLINICA]', 'FisioSalud Centro de Terapias Integrales')
            
            # Formatear el mensaje para HTML
            mensaje_cuerpo_html = mensaje_cuerpo.replace('\n', '<br>')
            # Convertir negritas markdown a HTML
            mensaje_cuerpo_html = mensaje_cuerpo_html.replace('**', '</strong>').replace('**', '<strong>')
            # Arreglar el orden (esto es un workaround para el doble reemplazo)
            mensaje_cuerpo_html = mensaje_cuerpo_html.replace('</strong><strong>', '')
            
            # Agregar estilos a los títulos dentro del mensaje
            mensaje_cuerpo_html = mensaje_cuerpo_html.replace('🧘 Ejercicio para Continuar en Casa:', '<div style="color: #0A2540; font-weight: 600; margin: 20px 0 10px 0; font-size: 16px;">🧘 Ejercicio para Continuar en Casa:</div>')
            mensaje_cuerpo_html = mensaje_cuerpo_html.replace('💆 Implemento Recomendado:', '<div style="color: #0A2540; font-weight: 600; margin: 20px 0 10px 0; font-size: 16px;">💆 Implemento Recomendado:</div>')
            mensaje_cuerpo_html = mensaje_cuerpo_html.replace('🌱 Suplemento de Apoyo:', '<div style="color: #0A2540; font-weight: 600; margin: 20px 0 10px 0; font-size: 16px;">🌱 Suplemento de Apoyo:</div>')
            
            asunto = terapia_info['asunto_correo'].replace('[NOMBRE_CLINICA]', 'FisioSalud')
        else:
            # Plantilla genérica si no hay info específica
            mensaje_cuerpo_html = f"""
            <p>Nos complace informarle que ha completado exitosamente su tratamiento de <strong>{datos_cita.get('servicio', 'terapia')}</strong> en FisioSalud.</p>
            
            <p>Su dedicación y compromiso durante el proceso han sido ejemplares. Recuerde seguir las recomendaciones proporcionadas durante sus sesiones para mantener los beneficios alcanzados.</p>
            
            <p>Recuerde que en FisioSalud siempre estaremos aquí para apoyarle en su bienestar.</p>
            """
            asunto = "¡Felicitaciones por Completar tu Terapia! | FisioSalud"
        
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{asunto}</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --primary: #0A2540;
                    --primary-dark: #061A2C;
                    --secondary: #00A3FF;
                    --accent: #00D4AA;
                    --success: #10B981;
                    --light: #FFFFFF;
                    --light-gray: #F8FAFC;
                    --gray: #64748B;
                    --dark: #0F172A;
                    --border-radius: 12px;
                    --border-radius-sm: 8px;
                    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                }}

                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
                    line-height: 1.6;
                    color: var(--dark);
                    background-color: #fafafa;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }}

                .email-container {{
                    max-width: 640px;
                    margin: 0 auto;
                    background: var(--light);
                    border-radius: var(--border-radius);
                    overflow: hidden;
                    box-shadow: var(--shadow-lg);
                }}

                /* Header elegante */
                .email-header {{
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                    color: white;
                    padding: 48px 40px 32px;
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                }}

                .email-header::before {{
                    content: '';
                    position: absolute;
                    top: -50px;
                    right: -50px;
                    width: 200px;
                    height: 200px;
                    background: radial-gradient(circle, rgba(0, 212, 170, 0.15) 0%, transparent 70%);
                    border-radius: 50%;
                }}

                .email-header::after {{
                    content: '';
                    position: absolute;
                    bottom: -30px;
                    left: -30px;
                    width: 150px;
                    height: 150px;
                    background: radial-gradient(circle, rgba(0, 163, 255, 0.1) 0%, transparent 70%);
                    border-radius: 50%;
                }}

                .logo-section {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 16px;
                    margin-bottom: 24px;
                    position: relative;
                    z-index: 2;
                }}

                .logo-icon {{
                    width: 56px;
                    height: 56px;
                    background: var(--light);
                    border-radius: var(--border-radius-sm);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: var(--primary);
                    font-weight: 700;
                    font-size: 22px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}

                .logo-text {{
                    font-size: 28px;
                    font-weight: 700;
                    color: white;
                }}

                .header-badge {{
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: rgba(255, 255, 255, 0.15);
                    backdrop-filter: blur(10px);
                    padding: 12px 24px;
                    border-radius: 50px;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 24px;
                    position: relative;
                    z-index: 2;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .header-title {{
                    font-size: 32px;
                    font-weight: 700;
                    line-height: 1.2;
                    margin-bottom: 16px;
                    position: relative;
                    z-index: 2;
                }}

                .header-subtitle {{
                    font-size: 18px;
                    opacity: 0.9;
                    font-weight: 400;
                    max-width: 500px;
                    margin: 0 auto;
                    position: relative;
                    z-index: 2;
                }}

                /* Contenido principal */
                .email-content {{
                    padding: 48px 40px;
                }}

                /* Sección de saludo */
                .greeting-section {{
                    background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin-bottom: 32px;
                    border-left: 4px solid var(--secondary);
                }}

                .greeting {{
                    font-size: 18px;
                    color: var(--primary);
                    line-height: 1.6;
                }}

                .greeting strong {{
                    color: var(--primary-dark);
                    font-weight: 700;
                }}

                /* Mensaje principal */
                .main-message {{
                    color: var(--dark);
                    font-size: 16px;
                    line-height: 1.7;
                    margin-bottom: 40px;
                }}

                .main-message p {{
                    margin-bottom: 20px;
                }}

                /* Sección de resumen */
                .summary-section {{
                    background: var(--light-gray);
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin: 40px 0;
                    border: 1px solid #E2E8F0;
                }}

                .summary-title {{
                    font-size: 20px;
                    font-weight: 700;
                    color: var(--primary);
                    margin-bottom: 24px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}

                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 24px;
                }}

                .summary-item {{
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }}

                .summary-label {{
                    color: var(--gray);
                    font-size: 14px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .summary-value {{
                    color: var(--dark);
                    font-size: 16px;
                    font-weight: 500;
                }}

                .completion-badge {{
                    background: linear-gradient(135deg, var(--success), #0D9C6D);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 50px;
                    font-weight: 700;
                    font-size: 14px;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    margin-top: 4px;
                }}

                /* Mensaje de felicitación */
                .celebration-section {{
                    text-align: center;
                    padding: 40px;
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(0, 212, 170, 0.05) 100%);
                    border-radius: var(--border-radius);
                    margin: 40px 0;
                    border: 1px solid rgba(16, 185, 129, 0.1);
                }}

                .celebration-icon {{
                    font-size: 64px;
                    margin-bottom: 20px;
                    color: var(--success);
                }}

                .celebration-text {{
                    font-size: 20px;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 12px;
                }}

                .celebration-subtext {{
                    color: var(--gray);
                    font-size: 16px;
                    max-width: 400px;
                    margin: 0 auto;
                }}

                /* Información de contacto */
                .contact-section {{
                    background: var(--primary);
                    color: white;
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin-top: 40px;
                    text-align: center;
                }}

                .contact-title {{
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 20px;
                }}

                .contact-info {{
                    display: flex;
                    justify-content: center;
                    gap: 32px;
                    flex-wrap: wrap;
                }}

                .contact-item {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 8px;
                }}

                .contact-icon {{
                    width: 40px;
                    height: 40px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                }}

                .contact-label {{
                    font-size: 12px;
                    opacity: 0.8;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .contact-value {{
                    font-size: 14px;
                    font-weight: 500;
                }}

                /* Footer */
                .email-footer {{
                    background: var(--primary-dark);
                    color: white;
                    padding: 40px;
                    text-align: center;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }}

                .footer-text {{
                    font-size: 14px;
                    opacity: 0.8;
                    margin-bottom: 20px;
                    line-height: 1.6;
                }}

                .footer-links {{
                    display: flex;
                    justify-content: center;
                    gap: 24px;
                    margin-bottom: 24px;
                    flex-wrap: wrap;
                }}

                .footer-link {{
                    color: rgba(255, 255, 255, 0.7);
                    text-decoration: none;
                    font-size: 14px;
                    transition: color 0.2s;
                }}

                .footer-link:hover {{
                    color: white;
                }}

                .footer-disclaimer {{
                    font-size: 12px;
                    opacity: 0.6;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }}

                /* Responsive */
                @media (max-width: 640px) {{
                    .email-header {{
                        padding: 32px 24px 24px;
                    }}
                    
                    .email-content {{
                        padding: 32px 24px;
                    }}
                    
                    .summary-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .header-title {{
                        font-size: 24px;
                    }}
                    
                    .header-subtitle {{
                        font-size: 16px;
                    }}
                    
                    .contact-info {{
                        flex-direction: column;
                        gap: 20px;
                    }}
                    
                    .footer-links {{
                        flex-direction: column;
                        gap: 12px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <!-- Header -->
                <div class="email-header">
                    <div class="logo-section">
                        <div class="logo-icon">FS</div>
                        <div class="logo-text">FisioSalud</div>
                    </div>
                    
                    <div class="header-badge">
                        <i class="fas fa-trophy"></i>
                        <span>TERAPIA COMPLETADA CON ÉXITO</span>
                    </div>
                    
                    <h1 class="header-title">¡Logro Alcanzado!</h1>
                    <p class="header-subtitle">
                        Celebrando la culminación exitosa de su proceso terapéutico en FisioSalud
                    </p>
                </div>

                <!-- Contenido principal -->
                <div class="email-content">
                    <!-- Saludo personalizado -->
                    <div class="greeting-section">
                        <p class="greeting">
                            Estimado/a <strong>{datos_cita.get('nombre_paciente', 'Paciente')}</strong>,<br><br>
                            Es para nosotros un honor comunicarle que ha completado exitosamente su ciclo de 
                            <strong>{datos_cita.get('servicio', 'Terapia')}</strong> en FisioSalud. 
                            Su dedicación durante este proceso ha sido excepcional.
                        </p>
                    </div>

                    <!-- Mensaje personalizado de la terapia -->
                    <div class="main-message">
                        {mensaje_cuerpo_html}
                    </div>

                    <!-- Resumen de la terapia -->
                    <div class="summary-section">
                        <h2 class="summary-title">
                            <i class="fas fa-clipboard-check"></i>
                            <span>Resumen de su Progreso</span>
                        </h2>
                        
                        <div class="summary-grid">
                            <div class="summary-item">
                                <span class="summary-label">Terapia Completada</span>
                                <span class="summary-value">{datos_cita.get('servicio', 'Terapia')}</span>
                            </div>
                            
                            <div class="summary-item">
                                <span class="summary-label">Terapeuta Responsable</span>
                                <span class="summary-value">{datos_cita.get('terapeuta_designado', 'Nuestro Equipo Especializado')}</span>
                            </div>
                            
                            <div class="summary-item">
                                <span class="summary-label">Última Sesión</span>
                                <span class="summary-value">{fecha_formateada}</span>
                            </div>
                            
                            <div class="summary-item">
                                <span class="summary-label">Estado del Tratamiento</span>
                                <div class="completion-badge">
                                    <i class="fas fa-check-circle"></i>
                                    <span>COMPLETADO EXITOSAMENTE</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Sección de felicitación -->
                    <div class="celebration-section">
                        <div class="celebration-icon">
                            <i class="fas fa-medal"></i>
                        </div>
                        <h3 class="celebration-text">¡Su dedicación ha dado frutos!</h3>
                        <p class="celebration-subtext">
                            Este logro representa no solo la culminación de un tratamiento, 
                            sino el inicio de una nueva etapa de bienestar y calidad de vida.
                        </p>
                    </div>

                    <!-- Información de contacto -->
                    <div class="contact-section">
                        <h3 class="contact-title">¿Necesita más apoyo?</h3>
                        <div class="contact-info">
                            <div class="contact-item">
                                <div class="contact-icon">
                                    <i class="fas fa-phone-alt"></i>
                                </div>
                                <span class="contact-label">Teléfono</span>
                                <span class="contact-value">(320) 291-4521</span>
                            </div>
                            
                            <div class="contact-item">
                                <div class="contact-icon">
                                    <i class="fas fa-envelope"></i>
                                </div>
                                <span class="contact-label">Correo Electrónico</span>
                                <span class="contact-value">info@fisiosalud.com</span>
                            </div>
                            
                            <div class="contact-item">
                                <div class="contact-icon">
                                    <i class="fas fa-map-marker-alt"></i>
                                </div>
                                <span class="contact-label">Ubicación</span>
                                <span class="contact-value">Av. Salud #123, Bogotá</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="email-footer">
                    <p class="footer-text">
                        FisioSalud - Centro de Terapias Integrales<br>
                        Líderes en rehabilitación digital con más de 15 años transformando vidas
                    </p>
                    
                    <div class="footer-links">
                        <a href="https://fisiosalud.com" class="footer-link">Visite nuestro sitio web</a>
                        <a href="https://fisiosalud.com/nosotros" class="footer-link">Conozca más sobre nosotros</a>
                        <a href="https://fisiosalud.com/servicios" class="footer-link">Nuestros servicios</a>
                        <a href="https://fisiosalud.com/contacto" class="footer-link">Contáctenos</a>
                    </div>
                    
                    <div class="footer-disclaimer">
                        Este es un correo automático generado el {datetime.datetime.now().strftime('%d/%m/%Y')} a las {datetime.datetime.now().strftime('%H:%M')}.<br>
                        Por favor, no responda a este mensaje. Para consultas utilice los canales oficiales.<br>
                        © {datetime.datetime.now().year} FisioSalud. Todos los derechos reservados.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def _plantilla_cancelacion_solapamiento(datos_cita: Dict, fecha_formateada: str, hora_formateada: str) -> str:
        """Plantilla HTML para cancelación por solapamiento de citas - ESTILO FISIOSALUD"""
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reagendamiento de Cita | FisioSalud</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --primary: #0A2540;
                    --primary-dark: #061A2C;
                    --secondary: #00A3FF;
                    --warning: #F59E0B;
                    --light: #FFFFFF;
                    --light-gray: #F8FAFC;
                    --gray: #64748B;
                    --dark: #0F172A;
                    --border-radius: 12px;
                    --border-radius-sm: 8px;
                    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                }}

                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
                    line-height: 1.6;
                    color: var(--dark);
                    background-color: #fafafa;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }}

                .email-container {{
                    max-width: 640px;
                    margin: 0 auto;
                    background: var(--light);
                    border-radius: var(--border-radius);
                    overflow: hidden;
                    box-shadow: var(--shadow-lg);
                }}

                /* Header */
                .email-header {{
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                    color: white;
                    padding: 48px 40px 32px;
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                }}

                .email-header::before {{
                    content: '';
                    position: absolute;
                    top: -50px;
                    right: -50px;
                    width: 200px;
                    height: 200px;
                    background: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, transparent 70%);
                    border-radius: 50%;
                }}

                .logo-section {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 16px;
                    margin-bottom: 24px;
                    position: relative;
                    z-index: 2;
                }}

                .logo-icon {{
                    width: 56px;
                    height: 56px;
                    background: var(--light);
                    border-radius: var(--border-radius-sm);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: var(--primary);
                    font-weight: 700;
                    font-size: 22px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}

                .logo-text {{
                    font-size: 28px;
                    font-weight: 700;
                    color: white;
                }}

                .header-badge {{
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: rgba(255, 255, 255, 0.15);
                    backdrop-filter: blur(10px);
                    padding: 12px 24px;
                    border-radius: 50px;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 24px;
                    position: relative;
                    z-index: 2;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .header-title {{
                    font-size: 32px;
                    font-weight: 700;
                    line-height: 1.2;
                    margin-bottom: 16px;
                    position: relative;
                    z-index: 2;
                }}

                .header-subtitle {{
                    font-size: 18px;
                    opacity: 0.9;
                    font-weight: 400;
                    max-width: 500px;
                    margin: 0 auto;
                    position: relative;
                    z-index: 2;
                }}

                /* Contenido principal */
                .email-content {{
                    padding: 48px 40px;
                }}

                /* Sección de explicación */
                .explanation-section {{
                    background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin-bottom: 32px;
                    border-left: 4px solid var(--warning);
                }}

                .greeting {{
                    font-size: 18px;
                    color: var(--primary);
                    line-height: 1.6;
                    margin-bottom: 20px;
                }}

                .greeting strong {{
                    color: var(--primary-dark);
                    font-weight: 700;
                }}

                .explanation-text {{
                    color: #92400E;
                    font-size: 16px;
                    line-height: 1.6;
                    margin-bottom: 20px;
                }}

                /* Detalles de la cita original */
                .original-appointment {{
                    background: var(--light-gray);
                    border-radius: var(--border-radius-sm);
                    padding: 24px;
                    margin: 32px 0;
                    border: 1px solid #E2E8F0;
                }}

                .original-title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}

                .details-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                }}

                .detail-item {{
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                }}

                .detail-label {{
                    color: var(--gray);
                    font-size: 14px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .detail-value {{
                    color: var(--dark);
                    font-size: 16px;
                    font-weight: 500;
                }}

                /* Sección de compensación */
                .compensation-section {{
                    background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin: 40px 0;
                    text-align: center;
                    border: 1px solid #A7F3D0;
                }}

                .compensation-icon {{
                    font-size: 48px;
                    color: #10B981;
                    margin-bottom: 20px;
                }}

                .compensation-title {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #065F46;
                    margin-bottom: 16px;
                }}

                .compensation-text {{
                    color: #047857;
                    font-size: 18px;
                    line-height: 1.6;
                    margin-bottom: 24px;
                }}

                .discount-badge {{
                    background: linear-gradient(135deg, #10B981, #059669);
                    color: white;
                    padding: 12px 32px;
                    border-radius: 50px;
                    font-weight: 700;
                    font-size: 20px;
                    display: inline-block;
                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                }}

                .compensation-note {{
                    color: #065F46;
                    font-size: 14px;
                    margin-top: 16px;
                    opacity: 0.8;
                }}

                /* Sección de acción */
                .action-section {{
                    background: linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%);
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin: 40px 0;
                    text-align: center;
                }}

                .action-title {{
                    font-size: 20px;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 20px;
                }}

                .action-text {{
                    color: var(--dark);
                    font-size: 16px;
                    line-height: 1.6;
                    margin-bottom: 24px;
                }}

                .action-button {{
                    display: inline-block;
                    background: var(--secondary);
                    color: white;
                    text-decoration: none;
                    padding: 16px 40px;
                    border-radius: var(--border-radius-sm);
                    font-weight: 600;
                    font-size: 16px;
                    transition: all 0.3s ease;
                    border: none;
                    cursor: pointer;
                }}

                .action-button:hover {{
                    background: #0088D4;
                    transform: translateY(-2px);
                    box-shadow: 0 8px 16px rgba(0, 163, 255, 0.3);
                }}

                /* Información de contacto */
                .contact-section {{
                    background: var(--primary);
                    color: white;
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin-top: 40px;
                    text-align: center;
                }}

                .contact-title {{
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 20px;
                }}

                .contact-info {{
                    display: flex;
                    justify-content: center;
                    gap: 32px;
                    flex-wrap: wrap;
                }}

                .contact-item {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 8px;
                }}

                .contact-icon {{
                    width: 40px;
                    height: 40px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                }}

                .contact-label {{
                    font-size: 12px;
                    opacity: 0.8;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .contact-value {{
                    font-size: 14px;
                    font-weight: 500;
                }}

                /* Footer */
                .email-footer {{
                    background: var(--primary-dark);
                    color: white;
                    padding: 40px;
                    text-align: center;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }}

                .footer-text {{
                    font-size: 14px;
                    opacity: 0.8;
                    margin-bottom: 20px;
                    line-height: 1.6;
                }}

                .footer-disclaimer {{
                    font-size: 12px;
                    opacity: 0.6;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }}

                @media (max-width: 640px) {{
                    .email-header {{
                        padding: 32px 24px 24px;
                    }}
                    
                    .email-content {{
                        padding: 32px 24px;
                    }}
                    
                    .details-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .header-title {{
                        font-size: 24px;
                    }}
                    
                    .header-subtitle {{
                        font-size: 16px;
                    }}
                    
                    .contact-info {{
                        flex-direction: column;
                        gap: 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <!-- Header -->
                <div class="email-header">
                    <div class="logo-section">
                        <div class="logo-icon">FS</div>
                        <div class="logo-text">FisioSalud</div>
                    </div>
                    
                    <div class="header-badge">
                        <i class="fas fa-calendar-alt"></i>
                        <span>REAGENDAMIENTO DE CITA</span>
                    </div>
                    
                    <h1 class="header-title">Importante: Solapamiento de Agenda</h1>
                    <p class="header-subtitle">
                        Necesitamos reagendar su cita - Ofrecemos compensación especial
                    </p>
                </div>

                <!-- Contenido principal -->
                <div class="email-content">
                    <!-- Sección de explicación -->
                    <div class="explanation-section">
                        <p class="greeting">
                            Estimado/a <strong>{datos_cita.get('nombre_paciente', 'Paciente')}</strong>,
                        </p>
                        
                        <p class="explanation-text">
                            <i class="fas fa-exclamation-circle"></i> Debido a un solapamiento inesperado en nuestra agenda de atención,
                            necesitamos reagendar su cita programada. Nos disculpamos sinceramente por este inconveniente.
                        </p>
                    </div>

                    <!-- Detalles de la cita original -->
                    <div class="original-appointment">
                        <h2 class="original-title">
                            <i class="far fa-calendar-times"></i>
                            <span>Cita Original Programada</span>
                        </h2>
                        
                        <div class="details-grid">
                            <div class="detail-item">
                                <span class="detail-label">Servicio</span>
                                <span class="detail-value">{datos_cita.get('servicio', 'Servicio no especificado')}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Terapeuta</span>
                                <span class="detail-value">{datos_cita.get('terapeuta_designado', 'Terapeuta asignado')}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Fecha</span>
                                <span class="detail-value">{fecha_formateada}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Hora</span>
                                <span class="detail-value">{hora_formateada}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Sección de compensación -->
                    <div class="compensation-section">
                        <div class="compensation-icon">
                            <i class="fas fa-gift"></i>
                        </div>
                        
                        <h3 class="compensation-title">Compensación por el Inconveniente</h3>
                        
                        <p class="compensation-text">
                            Como gesto de disculpa y agradecimiento por su comprensión,
                            le ofrecemos un <strong>descuento especial del 20%</strong> en su próxima sesión.
                        </p>
                        
                        <div class="discount-badge">
                            20% DE DESCUENTO
                        </div>
                        
                        <p class="compensation-note">
                            *Válido para reprogramación en los próximos 30 días
                        </p>
                    </div>

                    <!-- Sección de acción -->
                    <div class="action-section">
                        <h3 class="action-title">¿Cómo Proceder?</h3>
                        
                        <p class="action-text">
                            Para reagendar su cita con el descuento aplicado, por favor contáctenos
                            a través de cualquiera de nuestros canales de atención:
                        </p>
                        
                        <div style="display: flex; justify-content: center; gap: 16px; margin-top: 24px;">
                            <a href="https://fisiosalud.com/reagendar" class="action-button">
                                <i class="fas fa-calendar-plus"></i> Reagendar en Línea
                            </a>
                            
                            <a href="tel:3202914521" class="action-button" style="background: var(--primary);">
                                <i class="fas fa-phone-alt"></i> Llamarnos
                            </a>
                        </div>
                    </div>

                    <!-- Información de contacto -->
                    <div class="contact-section">
                        <h3 class="contact-title">Nuestros Canales de Atención</h3>
                        <div class="contact-info">
                            <div class="contact-item">
                                <div class="contact-icon">
                                    <i class="fas fa-phone-alt"></i>
                                </div>
                                <span class="contact-label">Teléfono</span>
                                <span class="contact-value">(320) 291-4521</span>
                            </div>
                            
                            <div class="contact-item">
                                <div class="contact-icon">
                                    <i class="fas fa-whatsapp"></i>
                                </div>
                                <span class="contact-label">WhatsApp</span>
                                <span class="contact-value">+57 320 291 4521</span>
                            </div>
                            
                            <div class="contact-item">
                                <div class="contact-icon">
                                    <i class="fas fa-envelope"></i>
                                </div>
                                <span class="contact-label">Correo</span>
                                <span class="contact-value">info@fisiosalud.com</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="email-footer">
                    <p class="footer-text">
                        FisioSalud - Centro de Terapias Integrales<br>
                        Comprometidos con su bienestar y atención de calidad
                    </p>
                    
                    <div class="footer-disclaimer">
                        Este es un correo automático generado el {datetime.datetime.now().strftime('%d/%m/%Y')} a las {datetime.datetime.now().strftime('%H:%M')}.<br>
                        Agradecemos su comprensión y colaboración.<br>
                        © {datetime.datetime.now().year} FisioSalud. Todos los derechos reservados.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def _plantilla_cancelacion_razon_peso(datos_cita: Dict, fecha_formateada: str, hora_formateada: str, detalles: str = "") -> str:
        """Plantilla HTML para cancelación por razón de mayor peso - ESTILO FISIOSALUD"""
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Aviso Importante | FisioSalud</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --primary: #0A2540;
                    --primary-dark: #061A2C;
                    --secondary: #00A3FF;
                    --danger: #EF4444;
                    --light: #FFFFFF;
                    --light-gray: #F8FAFC;
                    --gray: #64748B;
                    --dark: #0F172A;
                    --border-radius: 12px;
                    --border-radius-sm: 8px;
                    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                }}

                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
                    line-height: 1.6;
                    color: var(--dark);
                    background-color: #fafafa;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }}

                .email-container {{
                    max-width: 640px;
                    margin: 0 auto;
                    background: var(--light);
                    border-radius: var(--border-radius);
                    overflow: hidden;
                    box-shadow: var(--shadow-lg);
                }}

                /* Header */
                .email-header {{
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
                    color: white;
                    padding: 48px 40px 32px;
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                }}

                .email-header::before {{
                    content: '';
                    position: absolute;
                    top: -50px;
                    right: -50px;
                    width: 200px;
                    height: 200px;
                    background: radial-gradient(circle, rgba(239, 68, 68, 0.15) 0%, transparent 70%);
                    border-radius: 50%;
                }}

                .logo-section {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 16px;
                    margin-bottom: 24px;
                    position: relative;
                    z-index: 2;
                }}

                .logo-icon {{
                    width: 56px;
                    height: 56px;
                    background: var(--light);
                    border-radius: var(--border-radius-sm);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: var(--primary);
                    font-weight: 700;
                    font-size: 22px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}

                .logo-text {{
                    font-size: 28px;
                    font-weight: 700;
                    color: white;
                }}

                .header-badge {{
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    background: rgba(255, 255, 255, 0.15);
                    backdrop-filter: blur(10px);
                    padding: 12px 24px;
                    border-radius: 50px;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 24px;
                    position: relative;
                    z-index: 2;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .header-title {{
                    font-size: 32px;
                    font-weight: 700;
                    line-height: 1.2;
                    margin-bottom: 16px;
                    position: relative;
                    z-index: 2;
                }}

                .header-subtitle {{
                    font-size: 18px;
                    opacity: 0.9;
                    font-weight: 400;
                    max-width: 500px;
                    margin: 0 auto;
                    position: relative;
                    z-index: 2;
                }}

                /* Contenido principal */
                .email-content {{
                    padding: 48px 40px;
                }}

                /* Mensaje importante */
                .important-message {{
                    background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin-bottom: 32px;
                    border-left: 4px solid var(--danger);
                }}

                .greeting {{
                    font-size: 18px;
                    color: var(--primary);
                    line-height: 1.6;
                    margin-bottom: 20px;
                }}

                .important-text {{
                    color: #991B1B;
                    font-size: 16px;
                    line-height: 1.6;
                    margin-bottom: 20px;
                }}

                .reason-box {{
                    background: white;
                    border-radius: var(--border-radius-sm);
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid #FCA5A5;
                }}

                .reason-title {{
                    color: #DC2626;
                    font-weight: 600;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}

                .reason-content {{
                    color: #7F1D1D;
                    font-size: 15px;
                    line-height: 1.6;
                    white-space: pre-line;
                }}

                /* Detalles de la cita cancelada */
                .cancelled-appointment {{
                    background: var(--light-gray);
                    border-radius: var(--border-radius-sm);
                    padding: 24px;
                    margin: 32px 0;
                    border: 1px solid #E2E8F0;
                }}

                .cancelled-title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}

                .details-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                }}

                .detail-item {{
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                }}

                .detail-label {{
                    color: var(--gray);
                    font-size: 14px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .detail-value {{
                    color: var(--dark);
                    font-size: 16px;
                    font-weight: 500;
                }}

                /* Sección de compromiso */
                .commitment-section {{
                    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin: 40px 0;
                    text-align: center;
                }}

                .commitment-icon {{
                    font-size: 48px;
                    color: var(--secondary);
                    margin-bottom: 20px;
                }}

                .commitment-title {{
                    font-size: 22px;
                    font-weight: 700;
                    color: var(--primary);
                    margin-bottom: 16px;
                }}

                .commitment-text {{
                    color: var(--dark);
                    font-size: 16px;
                    line-height: 1.6;
                    margin-bottom: 24px;
                }}

                .assurance-box {{
                    background: white;
                    border-radius: var(--border-radius-sm);
                    padding: 16px;
                    margin-top: 20px;
                    border: 1px solid #93C5FD;
                    text-align: left;
                }}

                .assurance-title {{
                    color: var(--primary);
                    font-weight: 600;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}

                .assurance-list {{
                    list-style: none;
                    padding-left: 0;
                }}

                .assurance-list li {{
                    padding: 8px 0;
                    color: var(--dark);
                    font-size: 14px;
                    display: flex;
                    align-items: flex-start;
                    gap: 8px;
                    border-bottom: 1px solid #E5E7EB;
                }}

                .assurance-list li:last-child {{
                    border-bottom: none;
                }}

                .assurance-list li i {{
                    color: var(--secondary);
                    font-size: 12px;
                    margin-top: 4px;
                }}

                /* Sección de próximos pasos */
                .next-steps {{
                    background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin: 40px 0;
                }}

                .steps-title {{
                    font-size: 20px;
                    font-weight: 600;
                    color: #065F46;
                    margin-bottom: 24px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}

                .steps-container {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                }}

                .step-item {{
                    text-align: center;
                    padding: 20px;
                    background: white;
                    border-radius: var(--border-radius-sm);
                    box-shadow: var(--shadow);
                }}

                .step-number {{
                    width: 36px;
                    height: 36px;
                    background: var(--secondary);
                    color: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 700;
                    margin: 0 auto 12px;
                }}

                .step-text {{
                    color: var(--dark);
                    font-size: 14px;
                    line-height: 1.5;
                }}

                /* Información de contacto */
                .contact-section {{
                    background: var(--primary);
                    color: white;
                    border-radius: var(--border-radius);
                    padding: 32px;
                    margin-top: 40px;
                    text-align: center;
                }}

                .contact-title {{
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 20px;
                }}

                .contact-info {{
                    display: flex;
                    justify-content: center;
                    gap: 32px;
                    flex-wrap: wrap;
                }}

                .contact-item {{
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 8px;
                }}

                .contact-icon {{
                    width: 40px;
                    height: 40px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                }}

                .contact-label {{
                    font-size: 12px;
                    opacity: 0.8;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}

                .contact-value {{
                    font-size: 14px;
                    font-weight: 500;
                }}

                /* Footer */
                .email-footer {{
                    background: var(--primary-dark);
                    color: white;
                    padding: 40px;
                    text-align: center;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }}

                .footer-text {{
                    font-size: 14px;
                    opacity: 0.8;
                    margin-bottom: 20px;
                    line-height: 1.6;
                }}

                .footer-disclaimer {{
                    font-size: 12px;
                    opacity: 0.6;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                }}

                @media (max-width: 768px) {{
                    .steps-container {{
                        grid-template-columns: 1fr;
                        gap: 16px;
                    }}
                }}

                @media (max-width: 640px) {{
                    .email-header {{
                        padding: 32px 24px 24px;
                    }}
                    
                    .email-content {{
                        padding: 32px 24px;
                    }}
                    
                    .details-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .header-title {{
                        font-size: 24px;
                    }}
                    
                    .header-subtitle {{
                        font-size: 16px;
                    }}
                    
                    .contact-info {{
                        flex-direction: column;
                        gap: 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <!-- Header -->
                <div class="email-header">
                    <div class="logo-section">
                        <div class="logo-icon">FS</div>
                        <div class="logo-text">FisioSalud</div>
                    </div>
                    
                    <div class="header-badge">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>AVISO IMPORTANTE</span>
                    </div>
                    
                    <h1 class="header-title">Cancelación por Fuerza Mayor</h1>
                    <p class="header-subtitle">
                        Necesitamos cancelar su cita por razones excepcionales
                    </p>
                </div>

                <!-- Contenido principal -->
                <div class="email-content">
                    <!-- Mensaje importante -->
                    <div class="important-message">
                        <p class="greeting">
                            Estimado/a <strong>{datos_cita.get('nombre_paciente', 'Paciente')}</strong>,
                        </p>
                        
                        <p class="important-text">
                            <i class="fas fa-info-circle"></i> Lamentamos informarle que debido a circunstancias excepcionales de fuerza mayor,
                            debemos cancelar su cita programada. Entendemos que esto puede causar inconvenientes
                            y nos disculpamos sinceramente.
                        </p>
                        
                        <div class="reason-box">
                            <div class="reason-title">
                                <i class="fas fa-clipboard-list"></i>
                                <span>Detalles de la Situación:</span>
                            </div>
                            <div class="reason-content">
                                {detalles if detalles else "Circunstancias excepcionales que requieren la cancelación inmediata de la agenda."}
                            </div>
                        </div>
                    </div>

                    <!-- Detalles de la cita cancelada -->
                    <div class="cancelled-appointment">
                        <h2 class="cancelled-title">
                            <i class="far fa-calendar-times"></i>
                            <span>Cita Cancelada</span>
                        </h2>
                        
                        <div class="details-grid">
                            <div class="detail-item">
                                <span class="detail-label">Servicio</span>
                                <span class="detail-value">{datos_cita.get('servicio', 'Servicio no especificado')}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Terapeuta</span>
                                <span class="detail-value">{datos_cita.get('terapeuta_designado', 'Terapeuta asignado')}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Fecha Programada</span>
                                <span class="detail-value">{fecha_formateada}</span>
                            </div>
                            
                            <div class="detail-item">
                                <span class="detail-label">Hora Programada</span>
                                <span class="detail-value">{hora_formateada}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Sección de compromiso -->
                    <div class="commitment-section">
                        <div class="commitment-icon">
                            <i class="fas fa-handshake"></i>
                        </div>
                        
                        <h3 class="commitment-title">Nuestro Compromiso con Usted</h3>
                        
                        <p class="commitment-text">
                            Valoramos enormemente su confianza en FisioSalud. Como muestra de nuestro compromiso
                            con su bienestar, le ofrecemos las siguientes garantías:
                        </p>
                        
                        <div class="assurance-box">
                            <div class="assurance-title">
                                <i class="fas fa-shield-alt"></i>
                                <span>Garantías que Ofrecemos</span>
                            </div>
                            <ul class="assurance-list">
                                <li>
                                    <i class="fas fa-check"></i>
                                    <span>Prioridad en reprogramación sin costos adicionales</span>
                                </li>
                                <li>
                                    <i class="fas fa-check"></i>
                                    <span>Seguimiento personalizado para reprogramación</span>
                                </li>
                                <li>
                                    <i class="fas fa-check"></i>
                                    <span>Atención especial en nuestro sistema de citas</span>
                                </li>
                                <li>
                                    <i class="fas fa-check"></i>
                                    <span>Apoyo continuo durante este periodo</span>
                                </li>
                            </ul>
                        </div>
                    </div>

                    <!-- Próximos pasos -->
                    <div class="next-steps">
                        <h3 class="steps-title">
                            <i class="fas fa-directions"></i>
                            <span>Próximos Pasos Sugeridos</span>
                        </h3>
                        
                        <div class="steps-container">
                            <div class="step-item">
                                <div class="step-number">1</div>
                                <div class="step-text">
                                    <strong>Contactarnos</strong> cuando la situación se normalice
                                </div>
                            </div>
                            
                            <div class="step-item">
                                <div class="step-number">2</div>
                                <div class="step-text">
                                    <strong>Recibir</strong> nuestra llamada para reprogramar
                                </div>
                            </div>
                            
                            <div class="step-item">
                                <div class="step-number">3</div>
                                <div class="step-text">
                                    <strong>Retomar</strong> su tratamiento con prioridad garantizada
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Información de contacto -->
                    <div class="contact-section">
                        <h3 class="contact-title">Para Más Información</h3>
                        <div class="contact-info">
                            <div class="contact-item">
                                <div class="contact-icon">
                                    <i class="fas fa-headset"></i>
                                </div>
                                <span class="contact-label">Soporte</span>
                                <span class="contact-value">(320) 291-4521</span>
                            </div>
                            
                            <div class="contact-item">
                                <div class="contact-icon">
                                    <i class="fas fa-envelope"></i>
                                </div>
                                <span class="contact-label">Correo</span>
                                <span class="contact-value">soporte@fisiosalud.com</span>
                            </div>
                            
                            <div class="contact-item">
                                <div class="contact-icon">
                                    <i class="fas fa-globe"></i>
                                </div>
                                <span class="contact-label">Sitio Web</span>
                                <span class="contact-value">www.fisiosalud.com</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer -->
                <div class="email-footer">
                    <p class="footer-text">
                        FisioSalud - Centro de Terapias Integrales<br>
                        Agradecemos su comprensión durante esta situación excepcional
                    </p>
                    
                    <div class="footer-disclaimer">
                        Este es un correo automático generado el {datetime.datetime.now().strftime('%d/%m/%Y')} a las {datetime.datetime.now().strftime('%H:%M')}.<br>
                        Su salud y bienestar son nuestra prioridad máxima.<br>
                        © {datetime.datetime.now().year} FisioSalud. Todos los derechos reservados.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def enviar_correo_cancelacion_cita(datos_cita: Dict[str, Any], 
                                    emails_destinatarios: List[str],
                                    motivo_cancelacion: str = "razon_general",
                                    detalles_adicionales: str = "") -> Dict[str, Any]:
        """
        Envía correos de cancelación de cita según el motivo
        """
        resultados = []
        emails_exitosos = 0
        
        # Formatear fecha y hora
        fecha_formateada = ""
        hora_formateada = ""
        
        if datos_cita.get('fecha_cita'):
            try:
                fecha_obj = datetime.datetime.strptime(datos_cita['fecha_cita'], '%Y-%m-%d')
                fecha_formateada = fecha_obj.strftime('%d de %B de %Y')
            except:
                fecha_formateada = datos_cita.get('fecha_cita', 'Fecha no especificada')
        
        if datos_cita.get('hora_cita'):
            try:
                hora_obj = datetime.datetime.strptime(datos_cita['hora_cita'], '%H:%M:%S')
                hora_formateada = hora_obj.strftime('%I:%M %p').lstrip('0')
            except:
                try:
                    hora_obj = datetime.datetime.strptime(datos_cita['hora_cita'], '%H:%M')
                    hora_formateada = hora_obj.strftime('%I:%M %p').lstrip('0')
                except:
                    hora_formateada = datos_cita.get('hora_cita', 'Hora no especificada')
        
        # Seleccionar plantilla según motivo
        if motivo_cancelacion == "finalizacion_terapia":
            # Cargar plantilla específica de finalización
            try:
                terapia_info = EmailModel._cargar_plantilla_finalizacion(datos_cita.get('servicio', ''))
                html_template = EmailModel._plantilla_cancelacion_finalizacion_terapia(
                    datos_cita, fecha_formateada, hora_formateada, terapia_info
                )
                asunto = terapia_info['asunto_correo'] if terapia_info else f"¡Felicitaciones por Completar tu Terapia! 🎉 | FisioSalud"
            except Exception as e:
                print(f"Error cargando plantilla de finalización: {e}")
                # Usar plantilla genérica
                html_template = EmailModel._plantilla_cancelacion_finalizacion_terapia(
                    datos_cita, fecha_formateada, hora_formateada, None
                )
                asunto = f"Finalización de Terapia | FisioSalud"
        
        elif motivo_cancelacion == "solapamiento":
            # Usar plantilla de solapamiento
            html_template = EmailModel._plantilla_cancelacion_solapamiento(
                datos_cita, fecha_formateada, hora_formateada
            )
            asunto = f"Reagendamiento de Cita - Solapamiento de Agenda | FisioSalud"
        
        elif motivo_cancelacion == "razon_peso":
            # Usar plantilla de razón de peso
            html_template = EmailModel._plantilla_cancelacion_razon_peso(
                datos_cita, fecha_formateada, hora_formateada, detalles_adicionales
            )
            asunto = f"Aviso Importante - Cancelación por Fuerza Mayor | FisioSalud"
        
        else:
            # Para otros motivos, usar plantilla básica
            html_template = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8"><style>body {{ font-family: Arial; line-height: 1.6; }}</style></head>
            <body>
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; background: #f8f9fa; padding: 20px;">
                        <h2>FisioSalud</h2>
                    </div>
                    <div style="padding: 20px;">
                        <p>Estimado/a {datos_cita.get('nombre_paciente', 'Paciente')},</p>
                        <p>Su cita del {fecha_formateada} a las {hora_formateada} ha sido cancelada.</p>
                        <p>Motivo: {motivo_cancelacion}</p>
                        {detalles_adicionales and f'<p>Detalles: {detalles_adicionales}</p>' or ''}
                        <p>Para más información, contáctenos.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            asunto = f"Cancelación de Cita | FisioSalud"
        
        for email in emails_destinatarios:
            try:
                # Crear mensaje
                msg = MIMEMultipart('alternative')
                msg['Subject'] = asunto
                msg['From'] = f'{EmailModel.FROM_NAME} <{EmailModel.FROM_EMAIL}>'
                msg['To'] = email
                
                # Para simplificar, solo HTML
                part2 = MIMEText(html_template, 'html', 'utf-8')
                msg.attach(part2)
                
                # Enviar correo
                with smtplib.SMTP(EmailModel.SMTP_SERVER, EmailModel.SMTP_PORT) as server:
                    server.starttls()
                    server.login(EmailModel.SMTP_USERNAME, EmailModel.SMTP_PASSWORD)
                    server.send_message(msg)
                
                resultados.append({
                    "email": email,
                    "estado": "enviado",
                    "timestamp": datetime.datetime.now().isoformat()
                })
                emails_exitosos += 1
                logger.info(f"✅ Correo de cancelación enviado exitosamente a: {email}")
                
            except Exception as e:
                resultados.append({
                    "email": email,
                    "estado": "error",
                    "error": str(e),
                    "timestamp": datetime.datetime.now().isoformat()
                })
                logger.error(f"❌ Error enviando correo de cancelación a {email}: {e}")
        
        return {
            "total_enviados": len(emails_destinatarios),
            "exitosos": emails_exitosos,
            "fallidos": len(emails_destinatarios) - emails_exitosos,
            "detalles": resultados,
            "motivo": motivo_cancelacion
        }

# ==============================================
# EJECUCIÓN DIRECTA PARA PRUEBAS
# ==============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO PRUEBA DE CORREO ELECTRÓNICO")
    print("=" * 60)
    
    # Primero probar conexión
    if EmailModel.test_conexion_smtp():
        print("\n" + "=" * 60)
        print("📧 ENVIANDO CORREO DE PRUEBA")
        print("=" * 60)
        
        if EmailModel.enviar_correo_prueba():
            print("\n✅ ¡PRUEBA EXITOSA!")
            print("\n📋 Instrucciones para ver el correo:")
            print("1. Ve a https://mailtrap.io")
            print("2. Haz clic en 'Sandboxes'")
            print("3. Haz clic en 'My Sandbox'")
            print("4. Verás el correo de prueba en la bandeja")
        else:
            print("\n❌ Falló el envío del correo")
    else:
        print("\n❌ No se puede continuar. Soluciona el error de conexión primero.")

    