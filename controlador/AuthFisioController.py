from modelo.FisioterapeutaModel import FisioterapeutaModel  
from typing import Dict, Any

class AuthFisioController:
    
    @staticmethod
    def login_fisioterapeuta(correo: str, codigo_trabajador: str) -> Dict[str, Any]:
        """Controla el proceso de login del fisioterapeuta"""
        try:
            # Validar que los campos no estén vacíos
            if not correo or not codigo_trabajador:
                return {
                    'success': False,
                    'error': 'Todos los campos son obligatorios'
                }
            
            # Validar credenciales en la base de datos
            terapeuta = FisioterapeutaModel.validar_credenciales(correo, codigo_trabajador)
            
            if terapeuta:
                # Preparar datos para la sesión
                datos_sesion = {
                    'Codigo_trabajador': terapeuta['Codigo_trabajador'],
                    'nombre_completo': terapeuta['nombre_completo'],
                    'fisio_correo': terapeuta['fisio_correo'],
                    'telefono': terapeuta['telefono'],
                    'especializacion': terapeuta['especializacion'],
                    'estado': terapeuta['estado']
                }
                
                return {
                    'success': True,
                    'terapeuta': datos_sesion,
                    'message': 'Login exitoso'
                }
            else:
                return {
                    'success': False,
                    'error': 'Credenciales inválidas o usuario inactivo'
                }
                
        except Exception as e:
            print(f"Error en controlador de auth: {e}")
            return {
                'success': False,
                'error': 'Error interno del servidor'
            }