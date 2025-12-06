from bd.conexion_bd import get_db_connection, close_db_connection

class ServicioNutricionModel:
    @staticmethod
    def obtener_todos_servicios():
        """
        Obtiene todos los productos de nutrición
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                # SIN filtro disponible (la columna no existe)
                query = "SELECT * FROM servicio_nutricion"
                cursor.execute(query)
                servicios = cursor.fetchall()
                
                # Convertir Decimal a float
                for servicio in servicios:
                    # Campos que SÍ existen según tu tabla
                    campos_decimales = [
                        'precio', 'porciones', 
                        'proteina/porcion', 'valor_energetico',
                        'proteinas', 'carbohidratos', 'grasas'
                    ]
                    
                    for campo in campos_decimales:
                        if campo in servicio and servicio[campo] is not None:
                            servicio[campo] = float(servicio[campo])
                
                print(f"✅ Productos nutrición obtenidos: {len(servicios)}")
                return servicios, None

        except Exception as e:
            print(f"Error en modelo obtener_todos_servicios (nutrición): {e}")
            return None, "Error interno al obtener productos"
        finally:
            close_db_connection(conn)


    @staticmethod
    def obtener_servicio_por_codigo(codigo):
        """
        Obtiene un producto de nutrición por su código desde la base de datos
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM servicio_nutricion WHERE codigo = %s"
                cursor.execute(query, (codigo,))
                servicio = cursor.fetchone()

                if not servicio:
                    return None, "Producto de nutrición no encontrado"

                # Convertir Decimal a float
                campos_decimales = [
                    'precio', 'porciones', 
                    'proteina/porcion', 'valor_energetico',
                    'proteinas', 'carbohidratos', 'grasas'
                ]
                
                for campo in campos_decimales:
                    if campo in servicio and servicio[campo] is not None:
                        servicio[campo] = float(servicio[campo])

                return servicio, None

        except Exception as e:
            print(f"Error en modelo obtener_servicio_por_codigo (nutrición): {e}")
            return None, "Error interno al obtener el producto"
        finally:
            close_db_connection(conn)