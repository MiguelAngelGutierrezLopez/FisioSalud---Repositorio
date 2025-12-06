from modelo.ServicioImplementosModel import ServicioImplementosModel
from fastapi.templating import Jinja2Templates
from fastapi import Request, Query

templates = Jinja2Templates(directory="./vista")

class ServicioImplementosController:
    
    @staticmethod
    async def detalle_servicio(request: Request, codigo: str):
        """
        Controla la obtención y presentación del detalle de un implemento
        """
        servicio, mensaje_error = ServicioImplementosModel.obtener_servicio_por_codigo(codigo)
        
        if mensaje_error:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": mensaje_error
            })

        return templates.TemplateResponse("detalle_implementos.html", {
            "request": request,
            "servicio_implementos": servicio  # ¡IMPORTANTE! Usar el nombre correcto que espera el HTML
        })

    @staticmethod
    async def listar_servicios_implementos(
        request: Request,
        grupo_muscular: str = Query(None),
        dificultad: str = Query(None),
        precio_min: float = Query(None),
        precio_max: float = Query(None)
    ):
        """
        Controla la presentación de la página de implementos con filtros
        """
        # Obtener todos los servicios
        servicios, error = ServicioImplementosModel.obtener_todos_servicios()
        
        if error:
            return templates.TemplateResponse("serv_implementos.html", {
                "request": request,
                "error": error,
                "servicios": []
            })

        # Aplicar filtros si existen
        servicios_filtrados = servicios
        
        if grupo_muscular:
            servicios_filtrados = [s for s in servicios_filtrados 
                                  if s.get('grupo_muscular') == grupo_muscular]
        
        if dificultad:
            try:
                nivel_dificultad = int(dificultad)
                servicios_filtrados = [s for s in servicios_filtrados 
                                      if s.get('dificultad') == nivel_dificultad]
            except ValueError:
                pass  # Si no es un número válido, ignorar el filtro
        
        if precio_min is not None:
            servicios_filtrados = [s for s in servicios_filtrados 
                                  if s.get('precio', 0) >= precio_min]
        
        if precio_max is not None:
            servicios_filtrados = [s for s in servicios_filtrados 
                                  if s.get('precio', float('inf')) <= precio_max]

        # Obtener opciones para los filtros
        grupos_musculares, _ = ServicioImplementosModel.obtener_grupos_musculares()
        niveles_dificultad, _ = ServicioImplementosModel.obtener_niveles_dificultad()

        return templates.TemplateResponse("serv_implementos.html", {
            "request": request,
            "servicios": servicios_filtrados,
            "grupos_musculares": grupos_musculares,
            "niveles_dificultad": niveles_dificultad,
            "filtro_grupo_muscular": grupo_muscular,
            "filtro_dificultad": dificultad,
            "filtro_precio_min": precio_min,
            "filtro_precio_max": precio_max
        })