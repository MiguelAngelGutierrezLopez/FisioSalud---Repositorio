from bd.conexion_bd import get_db_connection, close_db_connection

class ServicioImplementosModel:
    @staticmethod
    def obtener_todos_servicios():
        """
        Obtiene todos los implementos
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM servicio_implementos"
                cursor.execute(query)
                servicios = cursor.fetchall()
                
                # Convertir Decimal a float
                for servicio in servicios:
                    # Campos que SÍ existen según tu tabla
                    campos_decimales = [
                        'precio', 'peso', 'peso_total_set', 'dificultad'
                    ]
                    
                    for campo in campos_decimales:
                        if campo in servicio and servicio[campo] is not None:
                            servicio[campo] = float(servicio[campo])
                
                print(f"✅ Productos implementos obtenidos: {len(servicios)}")
                return servicios, None

        except Exception as e:
            print(f"Error en modelo obtener_todos_servicios (implementos): {e}")
            return None, "Error interno al obtener implementos"
        finally:
            close_db_connection(conn)

    @staticmethod
    def obtener_servicio_por_codigo(codigo):
        """
        Obtiene un implemento por su código desde la base de datos
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM servicio_implementos WHERE codigo = %s"
                cursor.execute(query, (codigo,))
                servicio = cursor.fetchone()

                if not servicio:
                    return None, "Implemento no encontrado"

                # Convertir Decimal a float
                campos_decimales = [
                    'precio', 'peso', 'peso_total_set', 'dificultad'
                ]
                
                for campo in campos_decimales:
                    if campo in servicio and servicio[campo] is not None:
                        servicio[campo] = float(servicio[campo])

                return servicio, None

        except Exception as e:
            print(f"Error en modelo obtener_servicio_por_codigo (implementos): {e}")
            return None, "Error interno al obtener el implemento"
        finally:
            close_db_connection(conn)

    @staticmethod
    def obtener_grupos_musculares():
        """
        Obtiene los grupos musculares únicos de implementos
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = "SELECT DISTINCT grupo_muscular FROM servicio_implementos WHERE grupo_muscular IS NOT NULL AND grupo_muscular != ''"
                cursor.execute(query)
                grupos = cursor.fetchall()
                return [g['grupo_muscular'] for g in grupos], None

        except Exception as e:
            print(f"Error en modelo obtener_grupos_musculares: {e}")
            return None, "Error interno al obtener grupos musculares"
        finally:
            close_db_connection(conn)

    @staticmethod
    def obtener_niveles_dificultad():
        """
        Obtiene los niveles de dificultad únicos
        """
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"

        try:
            with conn.cursor() as cursor:
                query = "SELECT DISTINCT dificultad FROM servicio_implementos WHERE dificultad IS NOT NULL ORDER BY dificultad"
                cursor.execute(query)
                niveles = cursor.fetchall()
                return [n['dificultad'] for n in niveles], None

        except Exception as e:
            print(f"Error en modelo obtener_niveles_dificultad: {e}")
            return None, "Error interno al obtener niveles de dificultad"
        finally:
            close_db_connection(conn)