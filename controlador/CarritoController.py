from modelo.CarritoModel import CarritoModel
from modelo.ServicioNutricionModel import ServicioNutricionModel
from modelo.ServicioImplementosModel import ServicioImplementosModel
from controlador.AuthController import AuthController
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import traceback

class CarritoController:
    
    @staticmethod
    async def mostrar_panel_productos(request: Request):
        """
        Muestra el panel principal de productos DEL USUARIO LOGUEADO
        """
        print("🔍 Accediendo a /panel_mercado...")
        usuario = AuthController.verificar_sesion_usuario(request)
        
        if not usuario:
            print("❌ No hay sesión en /panel_mercado, redirigiendo...")
            raise HTTPException(status_code=401, detail="No autorizado - sesión inválida")
        
        print(f"✅ Sesión válida para: {usuario['email']} (ID: {usuario['id']})")
        
        try:
            # 🔒 Obtener SOLO los productos del carrito DEL USUARIO ACTUAL
            carrito_items, error_carrito = CarritoModel.obtener_carrito_usuario(usuario['id'])
            print(f"🛒 Carrito del usuario: {len(carrito_items or [])} items")
            
            # 🔒 Obtener productos disponibles de AMBOS tipos
            productos_nutricion, error_nutricion = ServicioNutricionModel.obtener_todos_servicios()
            productos_implementos, error_implementos = ServicioImplementosModel.obtener_todos_servicios()
            
            print(f"📦 Productos de nutrición disponibles: {len(productos_nutricion or [])}")
            print(f"🏋️ Productos de implementos disponibles: {len(productos_implementos or [])}")
            
            # Calcular totales del carrito
            total_carrito = 0
            items_count = 0
            if carrito_items:
                for item in carrito_items:
                    precio = float(item.get('precio', 0)) or 0
                    cantidad = int(item.get('cantidad', 1)) or 1
                    total_carrito += precio * cantidad
                    items_count += cantidad

            print(f"💰 Total carrito: ${total_carrito}, Items: {items_count}")
            
            # Retornar datos para que la ruta maneje el template
            return {
                "success": True,
                "usuario": usuario,
                "carrito_items": carrito_items or [],
                "productos_nutricion": productos_nutricion or [],
                "productos_implementos": productos_implementos or [],
                "total_carrito": float(total_carrito),
                "items_count": items_count
            }
            
        except Exception as e:
            print(f"🔥 Error en mostrar_panel_productos: {e}")
            print(traceback.format_exc())
            return {
                "success": False,
                "usuario": None,
                "carrito_items": [],
                "productos_nutricion": [],
                "productos_implementos": [],
                "total_carrito": 0,
                "items_count": 0
            }

    # 🔒 MÉTODO DE VERIFICACIÓN DE PROPIEDAD
    @staticmethod
    def verificar_propiedad_carrito(usuario_id, carrito_id):
        """
        Verifica que el item del carrito pertenece al usuario
        """
        try:
            carrito_items, error = CarritoModel.obtener_carrito_usuario(usuario_id)
            if error or not carrito_items:
                print(f"❌ No se pudo obtener carrito para usuario {usuario_id}")
                return False
            
            # Buscar el item específico
            for item in carrito_items:
                if str(item.get('id')) == str(carrito_id) or str(item.get('carrito_id')) == str(carrito_id):
                    print(f"✅ Item {carrito_id} pertenece al usuario {usuario_id}")
                    return True
            
            print(f"❌ Item {carrito_id} NO pertenece al usuario {usuario_id}")
            return False
            
        except Exception as e:
            print(f"🔥 Error en verificar_propiedad_carrito: {e}")
            return False

    @staticmethod
    async def agregar_al_carrito(request: Request):
        """
        Endpoint para agregar producto al carrito CON VERIFICACIÓN
        """
        print("🛒 Agregando producto al carrito...")
        usuario = AuthController.verificar_sesion_usuario(request)
        
        if not usuario:
            return JSONResponse({
                "success": False, 
                "message": "No autorizado - sesión inválida"
            }, status_code=401)

        try:
            data = await request.json()
            producto_id = data.get('producto_id')
            producto_tipo = data.get('producto_tipo', 'nutricion')
            cantidad = data.get('cantidad', 1)
            
            print(f"📦 Datos recibidos: usuario_id={usuario['id']}, producto_id={producto_id}, tipo={producto_tipo}, cantidad={cantidad}")
            
            if not producto_id:
                return JSONResponse({
                    "success": False, 
                    "message": "ID de producto requerido"
                })
            
            # 🔒 VERIFICAR que el producto existe y está disponible
            if producto_tipo == 'nutricion':
                productos, error = ServicioNutricionModel.obtener_servicio_por_codigo(producto_id)
                if error or not productos:
                    return JSONResponse({
                        "success": False, 
                        "message": "Producto no encontrado o no disponible"
                    })
            
            success, message = CarritoModel.agregar_al_carrito(
                usuario['id'], producto_id, producto_tipo, cantidad
            )
            
            # Obtener el carrito actualizado para calcular el nuevo total
            carrito_actualizado, _ = CarritoModel.obtener_carrito_usuario(usuario['id'])
            total_actualizado = 0
            items_count = 0
            if carrito_actualizado:
                for item in carrito_actualizado:
                    precio = item.get('precio', 0) or 0
                    cantidad_item = item.get('cantidad', 1) or 1
                    total_actualizado += precio * cantidad_item
                    items_count += cantidad_item
            
            return JSONResponse({
                "success": success, 
                "message": message,
                "total_carrito": total_actualizado,
                "items_count": items_count
            })
            
        except Exception as e:
            print(f"🔥 Error en controlador agregar_al_carrito: {e}")
            print(traceback.format_exc())
            return JSONResponse({
                "success": False, 
                "message": "Error interno del servidor"
            }, status_code=500)

    @staticmethod
    async def eliminar_del_carrito(request: Request):
        """
        Endpoint para eliminar producto del carrito CON VERIFICACIÓN DE PROPIEDAD
        """
        print("🗑️ Eliminando producto del carrito...")
        usuario = AuthController.verificar_sesion_usuario(request)
        
        if not usuario:
            return JSONResponse({
                "success": False, 
                "message": "No autorizado - sesión inválida"
            }, status_code=401)

        try:
            data = await request.json()
            carrito_id = data.get('carrito_id')
            
            print(f"📦 Usuario {usuario['id']} intenta eliminar item: {carrito_id}")
            
            if not carrito_id:
                return JSONResponse({
                    "success": False, 
                    "message": "ID de carrito requerido"
                })
            
            # 🔒 VERIFICAR QUE EL ITEM PERTENECE AL USUARIO
            if not CarritoController.verificar_propiedad_carrito(usuario['id'], carrito_id):
                print(f"🚫 Intento de eliminar item no propio: usuario={usuario['id']}, item={carrito_id}")
                return JSONResponse({
                    "success": False, 
                    "message": "No tienes permisos para eliminar este item"
                }, status_code=403)
            
            success, message = CarritoModel.eliminar_del_carrito(carrito_id, usuario['id'])
            
            # Obtener el carrito actualizado
            carrito_actualizado, _ = CarritoModel.obtener_carrito_usuario(usuario['id'])
            total_actualizado = 0
            items_count = 0
            if carrito_actualizado:
                for item in carrito_actualizado:
                    precio = item.get('precio', 0) or 0
                    cantidad_item = item.get('cantidad', 1) or 1
                    total_actualizado += precio * cantidad_item
                    items_count += cantidad_item
            
            return JSONResponse({
                "success": success, 
                "message": message,
                "total_carrito": total_actualizado,
                "items_count": items_count
            })
            
        except Exception as e:
            print(f"🔥 Error en controlador eliminar_del_carrito: {e}")
            print(traceback.format_exc())
            return JSONResponse({
                "success": False, 
                "message": "Error interno del servidor"
            }, status_code=500)

    @staticmethod
    async def actualizar_cantidad_carrito(request: Request):
        """
        Endpoint para actualizar cantidad en el carrito CON VERIFICACIÓN
        """
        print("📊 Actualizando cantidad en carrito...")
        usuario = AuthController.verificar_sesion_usuario(request)
        
        if not usuario:
            return JSONResponse({
                "success": False, 
                "message": "No autorizado - sesión inválida"
            }, status_code=401)

        try:
            data = await request.json()
            carrito_id = data.get('carrito_id')
            cantidad = data.get('cantidad', 1)
            
            print(f"📦 Usuario {usuario['id']} actualizando: carrito_id={carrito_id}, cantidad={cantidad}")
            
            if not carrito_id:
                return JSONResponse({
                    "success": False, 
                    "message": "ID de carrito requerido"
                })
            
            # 🔒 VERIFICAR PROPIEDAD
            if not CarritoController.verificar_propiedad_carrito(usuario['id'], carrito_id):
                return JSONResponse({
                    "success": False, 
                    "message": "No tienes permisos para modificar este item"
                }, status_code=403)
            
            success, message = CarritoModel.actualizar_cantidad_carrito(carrito_id, usuario['id'], cantidad)
            
            # Obtener el carrito actualizado
            carrito_actualizado, _ = CarritoModel.obtener_carrito_usuario(usuario['id'])
            total_actualizado = 0
            items_count = 0
            if carrito_actualizado:
                for item in carrito_actualizado:
                    precio = item.get('precio', 0) or 0
                    cantidad_item = item.get('cantidad', 1) or 1
                    total_actualizado += precio * cantidad_item
                    items_count += cantidad_item
            
            return JSONResponse({
                "success": success, 
                "message": message,
                "total_carrito": total_actualizado,
                "items_count": items_count
            })
            
        except Exception as e:
            print(f"🔥 Error en controlador actualizar_cantidad_carrito: {e}")
            print(traceback.format_exc())
            return JSONResponse({
                "success": False, 
                "message": "Error interno del servidor"
            }, status_code=500)

    @staticmethod
    async def vaciar_carrito(request: Request):
        """
        Endpoint para vaciar todo el carrito
        """
        print("🧹 Vaciando carrito...")
        usuario = AuthController.verificar_sesion_usuario(request)
        
        if not usuario:
            return JSONResponse({
                "success": False, 
                "message": "No autorizado - sesión inválida"
            }, status_code=401)

        try:
            success, message = CarritoModel.vaciar_carrito(usuario['id'])
            
            return JSONResponse({
                "success": success, 
                "message": message,
                "total_carrito": 0,
                "items_count": 0
            })
            
        except Exception as e:
            print(f"🔥 Error en controlador vaciar_carrito: {e}")
            print(traceback.format_exc())
            return JSONResponse({
                "success": False, 
                "message": "Error interno del servidor"
            }, status_code=500)
    @staticmethod
    async def confirmar_compra(request: Request):
        """
        Endpoint para confirmar compra y guardar en compras_confirmadas
        """
        print("💳 Confirmando compra...")
        usuario = AuthController.verificar_sesion_usuario(request)
        
        if not usuario:
            return JSONResponse({
                "success": False, 
                "message": "No autorizado - sesión inválida"
            }, status_code=401)

        try:
            data = await request.json()
            direccion_envio = data.get('direccion_envio')
            ciudad = data.get('ciudad')
            codigo_postal = data.get('codigo_postal')
            metodo_pago = data.get('metodo_pago')
            
            print(f"📦 Datos de compra: usuario_id={usuario['id']}")
            
            if not all([direccion_envio, ciudad, codigo_postal, metodo_pago]):
                return JSONResponse({
                    "success": False, 
                    "message": "Todos los campos son requeridos"
                })
            
            # Confirmar la compra
            success, message, datos_compra = CarritoModel.confirmar_compra(
                usuario['id'], direccion_envio, ciudad, codigo_postal, metodo_pago
            )
            
            if success:
                print(f"✅ Compra confirmada: {datos_compra['orden_id']}")
                
                return JSONResponse({
                    "success": True, 
                    "message": message,
                    "compra": datos_compra
                })
            else:
                return JSONResponse({
                    "success": False, 
                    "message": message
                })
            
        except Exception as e:
            print(f"🔥 Error en controlador confirmar_compra: {e}")
            print(traceback.format_exc())
            return JSONResponse({
                "success": False, 
                "message": "Error interno del servidor"
            }, status_code=500)
        
    @staticmethod
    async def obtener_historial_compras(request: Request):
        """
        Endpoint para obtener historial de compras del usuario
        """
        print("📜 Obteniendo historial de compras...")
        usuario = AuthController.verificar_sesion_usuario(request)
        
        if not usuario:
            return JSONResponse({
                "success": False, 
                "message": "No autorizado - sesión inválida"
            }, status_code=401)

        try:
            compras, error = CarritoModel.obtener_historial_compras(usuario['id'])
            
            if error:
                return JSONResponse({
                    "success": False, 
                    "message": error
                })
            
            return JSONResponse({
                "success": True, 
                "compras": compras or []
            })
            
        except Exception as e:
            print(f"🔥 Error en controlador obtener_historial_compras: {e}")
            print(traceback.format_exc())
            return JSONResponse({
                "success": False, 
                "message": "Error interno del servidor"
            }, status_code=500)