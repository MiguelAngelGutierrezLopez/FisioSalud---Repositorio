from modelo.ServicioNutricionModel import ServicioNutricionModel
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="./vista")

class ServicioNutricionController:
    
    @staticmethod
    async def detalle_servicio(request, codigo: str):
        """
        Controla la obtención y presentación del detalle de un producto de nutrición
        """
        servicio, mensaje_error = ServicioNutricionModel.obtener_servicio_por_codigo(codigo)
        
        if mensaje_error:
            return templates.TemplateResponse("serv_alimentos.html", {
                "request": request,
                "mensaje": mensaje_error
            })

        return templates.TemplateResponse("detalle_nutricion.html", {
            "request": request,
            "servicio_nutricion": servicio
        })

    @staticmethod
    async def listar_servicios_nutricion(request):
        """
        Controla la presentación de la página de nutrición
        """
        # Podemos usar esto si queremos hacer la página dinámica en el futuro
        return templates.TemplateResponse("serv_nutricion.html", {
            "request": request
        })