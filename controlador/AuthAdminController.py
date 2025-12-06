from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from modelo.AdministradorModel import AdministradorModel
import traceback

templates_admin = Jinja2Templates(directory="./vista_admin")

class AuthAdminController:
    
    @staticmethod
    async def login_admin(
        request: Request,
        correo: str = Form(...),
        password: str = Form(...)
    ):
        """
        Controla el proceso de login del administrador
        """
        try:
            print("\n" + "="*60)
            print(f"🔐 [CONTROLADOR] Intento de login admin: {correo}")
            
            # Validar credenciales
            admin = AdministradorModel.validar_credenciales_admin(correo, password)
            
            if admin:
                # Crear sesión de administrador
                request.session['admin'] = {
                    'id': admin['id'],
                    'nombre': admin['nombre'],
                    'correo': admin['correo'],
                    'logged_in': True
                }
                
                print(f"✅ [CONTROLADOR] Login admin exitoso: {admin['nombre']}")
                print("="*60 + "\n")
                
                return RedirectResponse(url="/admin/panel-usuarios", status_code=303)
            else:
                # Credenciales inválidas
                print(f"❌ [CONTROLADOR] Login admin fallido: {correo}")
                print("="*60 + "\n")
                return templates_admin.TemplateResponse("panel_login_admin.html", {
                    "request": request,
                    "error": "Credenciales inválidas o usuario no autorizado"
                })
                
        except Exception as e:
            print(f"❌ [CONTROLADOR] Error en login_admin: {e}")
            traceback.print_exc()
            return templates_admin.TemplateResponse("panel_login_admin.html", {
                "request": request,
                "error": "Error interno del servidor"
            })
    
    @staticmethod
    async def logout_admin(request: Request):
        """
        Cierra sesión del administrador
        """
        try:
            admin_nombre = request.session.get('admin', {}).get('nombre', 'Desconocido')
            
            request.session.clear()
            if 'admin' in request.session:
                del request.session['admin']
            
            print(f"✅ Logout admin exitoso: {admin_nombre}")
            
            return RedirectResponse(url="/admin/login", status_code=303)
            
        except Exception as e:
            print(f"⚠️ Error durante logout admin: {e}")
            return RedirectResponse(url="/admin/login", status_code=303)
    
    @staticmethod
    def verificar_sesion_admin(request: Request):
        """
        Verifica la sesión del administrador
        """
        print("=" * 50)
        print("🔍 [verificar_sesion_admin] Verificando sesión...")
        print(f"📋 Keys en sesión: {list(request.session.keys())}")
        
        admin = request.session.get('admin')
        
        if not admin:
            print("❌ No existe 'admin' en la sesión")
            return None
        
        if not admin.get('logged_in'):
            print(f"❌ logged_in es: {admin.get('logged_in')}")
            return None
        
        print(f"✅ Sesión admin válida para: {admin.get('nombre')}")
        print("=" * 50)
        return admin