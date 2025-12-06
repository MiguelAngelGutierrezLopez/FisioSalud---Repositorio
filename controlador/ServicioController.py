from modelo.ServicioModel import ServicioModel
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="./vista")

class ServicioController:
    
    @staticmethod
    async def detalle_servicio(request, codigo: str):
        """
        Controla la obtención y presentación del detalle de un servicio
        """
        # Obtener servicio a través del modelo
        servicio, mensaje_error = ServicioModel.obtener_servicio_por_codigo(codigo)
        
        if mensaje_error:
            # Si hay un error, mostramos la página de error
            return templates.TemplateResponse("error.html", {
                "request": request,
                "mensaje": mensaje_error
            })

        # Si encontramos el servicio, mostramos el detalle
        return templates.TemplateResponse("detalle_servicio.html", {
            "request": request,
            "servicio": servicio
        })

    @staticmethod
    async def listar_servicios_terapeuticos(request):
        """
        Controla la obtención y presentación de todos los servicios
        """
        servicios, mensaje_error = ServicioModel.obtener_todos_servicios()
        
        if mensaje_error:
            return templates.TemplateResponse("serv_terapia.html", {
                "request": request,
                "error_message": mensaje_error
            })

        return templates.TemplateResponse("serv_terapia.html", {
            "request": request,
            "servicios": servicios  # Por si quieres mostrar dinámicamente
        })

    @staticmethod
    async def filtrar_servicios(request, categoria: str):
        """
        Controla el filtrado de servicios por categoría
        """
        servicios, mensaje_error = ServicioModel.obtener_servicios_por_categoria(categoria)
        
        if mensaje_error:
            return templates.TemplateResponse("serv_terapia.html", {
                "request": request,
                "error_message": mensaje_error
            })

        return templates.TemplateResponse("serv_terapia.html", {
            "request": request,
            "servicios": servicios,
            "categoria_activa": categoria
        })

    @staticmethod
    async def listar_servicios_terapeuticos(request):
        """
        Controla la obtención y presentación de todos los servicios
        """
        servicios, mensaje_error = ServicioModel.obtener_todos_servicios()
        terapeutas, _ = ServicioModel.obtener_lista_terapeutas()  # Obtener lista de terapeutas
        
        if mensaje_error:
            return templates.TemplateResponse("serv_terapia.html", {
                "request": request,
                "error_message": mensaje_error,
                "terapeutas": terapeutas or []
            })

        return templates.TemplateResponse("serv_terapia.html", {
            "request": request,
            "servicios": servicios,
            "terapeutas": terapeutas or []  # Pasar lista de terapeutas al template
        })

    @staticmethod
    async def filtrar_servicios_terapeuta(request, terapeuta_busqueda: str):
        """
        Controla el filtrado de servicios por terapeuta
        """
        servicios, mensaje_error = ServicioModel.obtener_servicios_por_terapeuta(terapeuta_busqueda)
        terapeutas, _ = ServicioModel.obtener_lista_terapeutas()
        
        if mensaje_error:
            return templates.TemplateResponse("serv_terapia.html", {
                "request": request,
                "error_message": mensaje_error,
                "terapeutas": terapeutas or [],
                "terapeuta_busqueda": terapeuta_busqueda
            })

        return templates.TemplateResponse("serv_terapia.html", {
            "request": request,
            "servicios": servicios,
            "terapeutas": terapeutas or [],
            "terapeuta_busqueda": terapeuta_busqueda,
            "filtro_terapeuta": True
        })