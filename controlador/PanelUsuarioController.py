# controlador/PanelUsuarioController.py
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import RedirectResponse
from controlador.AuthController import AuthController

templates_panel = Jinja2Templates(directory="./vista_panel")

class PanelUsuarioController:
    
    @staticmethod
    async def verificar_y_redirigir(request: Request):
        """
        Verifica sesión y redirige si no está autenticado
        """
        usuario = AuthController.verificar_sesion_usuario(request)
        if not usuario:
            request.session['error'] = 'Por favor, inicie sesión primero'
            return RedirectResponse(url="/login_user", status_code=302)
        return usuario

    @staticmethod
    async def panel_principal(request: Request):
        """
        Controla la página del panel principal del usuario
        """
        usuario = await PanelUsuarioController.verificar_y_redirigir(request)
        if isinstance(usuario, RedirectResponse):
            return usuario

        return templates_panel.TemplateResponse("panel_principal.html", {
            "request": request,
            "usuario": usuario
        })

    @staticmethod
    async def panel_citas(request: Request):
        """
        Controla la página de citas del usuario
        """
        usuario = await PanelUsuarioController.verificar_y_redirigir(request)
        if isinstance(usuario, RedirectResponse):
            return usuario

        return templates_panel.TemplateResponse("panel_citas.html", {
            "request": request,
            "usuario": usuario
        })

    @staticmethod
    async def panel_progreso(request: Request):
        """
        Controla la página de progreso del usuario
        """
        usuario = await PanelUsuarioController.verificar_y_redirigir(request)
        if isinstance(usuario, RedirectResponse):
            return usuario

        return templates_panel.TemplateResponse("panel_progreso.html", {
            "request": request,
            "usuario": usuario
        })

    @staticmethod
    async def panel_ejercicios(request: Request):
        """
        Controla la página de ejercicios del usuario
        """
        usuario = await PanelUsuarioController.verificar_y_redirigir(request)
        if isinstance(usuario, RedirectResponse):
            return usuario

        return templates_panel.TemplateResponse("panel_ejercicios.html", {
            "request": request,
            "usuario": usuario
        })

    @staticmethod
    async def panel_mercado(request: Request):
        """
        Controla la página de productos/marketplace del usuario
        """
        usuario = await PanelUsuarioController.verificar_y_redirigir(request)
        if isinstance(usuario, RedirectResponse):
            return usuario

        return templates_panel.TemplateResponse("panel_producto.html", {
            "request": request,
            "usuario": usuario
        })