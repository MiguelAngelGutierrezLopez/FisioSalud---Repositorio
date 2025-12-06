# modelo/CarritoModel.py
import json
import uuid
from bd.conexion_bd import get_db_connection, close_db_connection
from datetime import datetime

class CarritoModel:
    
    @staticmethod
    def agregar_al_carrito(usuario_id, producto_id, producto_tipo, cantidad=1):
        """
        Agrega un producto al carrito especificando el tipo
        producto_tipo: 'nutricion' o 'implemento'
        """
        conn = get_db_connection()
        if not conn:
            return False, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                # Verificar si el producto ya está en el carrito
                query = """
                SELECT id, cantidad FROM carrito 
                WHERE usuario_id = %s AND producto_id = %s AND producto_tipo = %s
                """
                cursor.execute(query, (usuario_id, producto_id, producto_tipo))
                item_existente = cursor.fetchone()

                if item_existente:
                    # Actualizar cantidad si ya existe
                    nueva_cantidad = item_existente['cantidad'] + cantidad
                    query = "UPDATE carrito SET cantidad = %s, actualizado_en = %s WHERE id = %s"
                    cursor.execute(query, (nueva_cantidad, datetime.now(), item_existente['id']))
                else:
                    # Insertar nuevo item
                    query = """
                    INSERT INTO carrito (usuario_id, producto_id, producto_tipo, cantidad, creado_en, actualizado_en)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (usuario_id, producto_id, producto_tipo, cantidad, datetime.now(), datetime.now()))
                
                conn.commit()
                return True, "Producto agregado al carrito"

        except Exception as e:
            print(f"Error en modelo agregar_al_carrito: {e}")
            return False, "Error interno al agregar al carrito"
        finally:
            close_db_connection(conn)


    # modelo/CarritoModel.py - VERIFICA que tenga esto
    @staticmethod
    def obtener_carrito_usuario(usuario_id):
        """
        Obtiene todos los items del carrito con información completa de ambos tipos de productos
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                # UNION de ambos tipos de productos - CORREGIDO
                query = """
                -- Productos de nutrición (SIN columna peso)
                SELECT 
                    c.id as carrito_id,
                    c.cantidad,
                    c.producto_tipo,
                    c.creado_en,
                    sn.codigo,
                    sn.nombre,
                    sn.descripcion,
                    sn.precio,
                    sn.porciones,
                    NULL as peso,  -- ✅ Agregar NULL para peso
                    'nutricion' as tipo
                FROM carrito c
                JOIN servicio_nutricion sn ON c.producto_id = sn.codigo
                WHERE c.usuario_id = %s AND c.producto_tipo = 'nutricion'
                
                UNION ALL
                
                -- Productos de implementos (CON columna peso)
                SELECT 
                    c.id as carrito_id,
                    c.cantidad,
                    c.producto_tipo,
                    c.creado_en,
                    si.codigo,
                    si.nombre,
                    si.descripcion,
                    si.precio,
                    NULL as porciones,  -- ✅ NULL para porciones
                    si.peso,            -- ✅ Incluir peso
                    'implemento' as tipo
                FROM carrito c
                JOIN servicio_implementos si ON c.producto_id = si.codigo
                WHERE c.usuario_id = %s AND c.producto_tipo = 'implemento'
                
                ORDER BY creado_en DESC
                """
                cursor.execute(query, (usuario_id, usuario_id))
                items = cursor.fetchall()
                
                # Convertir tipos no serializables
                for item in items:
                    # Convertir Decimal a float
                    if 'precio' in item and item['precio'] is not None:
                        item['precio'] = float(item['precio'])
                    
                    # Convertir peso si existe
                    if 'peso' in item and item['peso'] is not None:
                        item['peso'] = float(item['peso'])
                    
                    # ✅ CONVERTIR datetime a string ISO format
                    if 'creado_en' in item and item['creado_en'] is not None:
                        item['creado_en'] = item['creado_en'].isoformat() if hasattr(item['creado_en'], 'isoformat') else str(item['creado_en'])
                    
                    # Si hay otros campos datetime, convertirlos también
                    if 'actualizado_en' in item and item['actualizado_en'] is not None:
                        item['actualizado_en'] = item['actualizado_en'].isoformat() if hasattr(item['actualizado_en'], 'isoformat') else str(item['actualizado_en'])
                
                print(f"✅ Carrito obtenido: {len(items)} items")
                return items, None

        except Exception as e:
            print(f"Error en modelo obtener_carrito_usuario: {e}")
            return None, "Error interno al obtener carrito"
        finally:
            close_db_connection(conn)

    @staticmethod
    def eliminar_del_carrito(carrito_id, usuario_id):
        """
        Elimina un item del carrito
        """
        conn = get_db_connection()
        if not conn:
            return False, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = "DELETE FROM carrito WHERE id = %s AND usuario_id = %s"
                cursor.execute(query, (carrito_id, usuario_id))
                conn.commit()
                return True, "Producto eliminado del carrito"

        except Exception as e:
            print(f"Error en modelo eliminar_del_carrito: {e}")
            return False, "Error interno al eliminar del carrito"
        finally:
            close_db_connection(conn)

    @staticmethod
    def actualizar_cantidad_carrito(carrito_id, usuario_id, cantidad):
        """
        Actualiza la cantidad de un producto en el carrito
        """
        conn = get_db_connection()
        if not conn:
            return False, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                if cantidad <= 0:
                    # Si la cantidad es 0 o negativa, eliminar el item
                    return CarritoModel.eliminar_del_carrito(carrito_id, usuario_id)
                
                query = "UPDATE carrito SET cantidad = %s, actualizado_en = %s WHERE id = %s AND usuario_id = %s"
                cursor.execute(query, (cantidad, datetime.now(), carrito_id, usuario_id))
                conn.commit()
                return True, "Cantidad actualizada"

        except Exception as e:
            print(f"Error en modelo actualizar_cantidad_carrito: {e}")
            return False, "Error interno al actualizar cantidad"
        finally:
            close_db_connection(conn)

    @staticmethod
    def vaciar_carrito(usuario_id):
        """
        Vacía todo el carrito del usuario
        """
        conn = get_db_connection()
        if not conn:
            return False, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = "DELETE FROM carrito WHERE usuario_id = %s"
                cursor.execute(query, (usuario_id,))
                conn.commit()
                return True, "Carrito vaciado"

        except Exception as e:
            print(f"Error en modelo vaciar_carrito: {e}")
            return False, "Error interno al vaciar carrito"
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def confirmar_compra(usuario_id, direccion_envio, ciudad, codigo_postal, metodo_pago):
        """
        Confirma la compra y guarda toda la información en una sola tabla
        """
        conn = get_db_connection()
        if not conn:
            return False, "Error de conexión con la base de datos", None

        try:
            with conn.cursor() as cursor:
                # 1. Obtener todos los items del carrito del usuario con información completa
                cursor.execute("""
                    SELECT c.id as carrito_id, c.producto_id, c.producto_tipo, c.cantidad,
                           COALESCE(sn.nombre, si.nombre) as nombre_producto,
                           COALESCE(sn.descripcion, si.descripcion) as descripcion,
                           COALESCE(sn.precio, si.precio) as precio_unitario
                    FROM carrito c
                    LEFT JOIN servicio_nutricion sn 
                        ON c.producto_id = sn.codigo AND c.producto_tipo = 'nutricion'
                    LEFT JOIN servicio_implementos si 
                        ON c.producto_id = si.codigo AND c.producto_tipo = 'implemento'
                    WHERE c.usuario_id = %s
                """, (usuario_id,))
                
                items_carrito = cursor.fetchall()
                
                if not items_carrito:
                    return False, "El carrito está vacío", None
                
                # 2. Calcular total y preparar datos
                total = 0
                cantidad_total = 0
                items_detalle = []
                
                for item in items_carrito:
                    precio = float(item['precio_unitario']) if item['precio_unitario'] else 0
                    cantidad = int(item['cantidad'])
                    subtotal = precio * cantidad
                    
                    total += subtotal
                    cantidad_total += cantidad
                    
                    # Agregar a items_detalle en formato JSON
                    items_detalle.append({
                        'producto_id': item['producto_id'],
                        'producto_tipo': item['producto_tipo'],
                        'nombre': item['nombre_producto'],
                        'descripcion': item['descripcion'],
                        'precio_unitario': precio,
                        'cantidad': cantidad,
                        'subtotal': subtotal
                    })
                
                # 3. Generar ID de orden único
                orden_id = "ORD" + str(uuid.uuid4().hex)[:12].upper()
                
                # 4. Tomar el primer producto como referencia principal
                primer_producto = items_carrito[0]
                
                # 5. Crear compra en compras_confirmadas (una sola tabla)
                query = """
                INSERT INTO compras_confirmadas 
                (usuario_id, orden_id, fecha_compra, total, estado, 
                 direccion_envio, ciudad, codigo_postal, metodo_pago,
                 producto_id, producto_tipo, producto_nombre, 
                 cantidad_total, items_detalle, creado_en)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                fecha_actual = datetime.now()
                direccion_completa = f"{direccion_envio}, {ciudad}, CP: {codigo_postal}"
                
                cursor.execute(query, (
                    usuario_id, 
                    orden_id, 
                    fecha_actual, 
                    total, 
                    'confirmada',
                    direccion_completa,
                    ciudad,
                    codigo_postal,
                    metodo_pago,
                    primer_producto['producto_id'],
                    primer_producto['producto_tipo'],
                    primer_producto['nombre_producto'],
                    cantidad_total,
                    json.dumps(items_detalle),  # Guardar todos los items como JSON
                    fecha_actual
                ))
                
                # 6. Vaciar el carrito
                cursor.execute("DELETE FROM carrito WHERE usuario_id = %s", (usuario_id,))
                
                # 7. Confirmar transacción
                conn.commit()
                
                return True, "Compra confirmada exitosamente", {
                    "orden_id": orden_id,
                    "fecha": fecha_actual.strftime("%d/%m/%Y %H:%M"),
                    "total": total,
                    "items": cantidad_total,
                    "productos": len(items_carrito)
                }

        except Exception as e:
            print(f"Error en modelo confirmar_compra: {e}")
            conn.rollback()
            return False, "Error interno al confirmar la compra", None
        finally:
            close_db_connection(conn)

    @staticmethod
    def obtener_historial_compras(usuario_id):
        """
        Obtiene el historial de compras del usuario
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = """
                SELECT id, orden_id, fecha_compra, total, estado, 
                       direccion_envio, ciudad, metodo_pago,
                       producto_nombre, cantidad_total,
                       items_detalle
                FROM compras_confirmadas 
                WHERE usuario_id = %s 
                ORDER BY fecha_compra DESC
                """
                cursor.execute(query, (usuario_id,))
                compras = cursor.fetchall()
                
                # Procesar el JSON de items_detalle
                for compra in compras:
                    if compra['items_detalle']:
                        try:
                            compra['items_detalle'] = json.loads(compra['items_detalle'])
                        except:
                            compra['items_detalle'] = []
                    
                    # Convertir fechas a string
                    if compra['fecha_compra']:
                        compra['fecha_compra_str'] = compra['fecha_compra'].strftime("%d/%m/%Y %H:%M")
                    
                    # Convertir Decimal a float
                    if 'total' in compra and compra['total'] is not None:
                        compra['total'] = float(compra['total'])
                
                return compras, None

        except Exception as e:
            print(f"Error en modelo obtener_historial_compras: {e}")
            return None, "Error interno al obtener historial"
        finally:
            close_db_connection(conn)