from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
app = FastAPI()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_routes = [
            "/", "/login_user", "/registro_user", "/validar_acceso", 
            "/registro_usuario", "/olvidar-contrasena", "/solicitar-reset",
            "/resetear-contrasena", "/actualizar-contrasena"
        ]
        if (not any(request.url.path.startswith(route) for route in public_routes) and 
            "usuario" not in request.session):
            return RedirectResponse(url="/login_user")
        
        response = await call_next(request)
        return response

app.add_middleware(AuthMiddleware)