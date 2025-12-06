from bd.conexion_bd import get_db_connection, close_db_connection
import os
import shutil

class UsuarioModel:
    @staticmethod
    def crear_usuario(datos_usuario):
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Verificar si el correo ya existe
                check_query = "SELECT ID FROM usuario WHERE correo = %s"
                cursor.execute(check_query, (datos_usuario['email'],))
                if cursor.fetchone():
                    return None, "El correo ya está registrado"
                
                # Insertar nuevo usuario
                sql = """
                INSERT INTO usuario (nombre, apellido, genero, correo, telefono, contraseña, 
                                   contraseña_confirmada, ID, historial_medico, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
                """
                cursor.execute(sql, (
                    datos_usuario['nombre'],
                    datos_usuario['apellido'],
                    datos_usuario['genero'],
                    datos_usuario['email'],
                    datos_usuario['telefono'],  # Cambié 'phone' por 'telefono'
                    datos_usuario['contraseña'],
                    datos_usuario['contraseña_confirmada'],
                    datos_usuario['ID'],
                    datos_usuario.get('medical_file_path')
                ))
                conn.commit()
                return True, "Usuario registrado exitosamente"
                
        except Exception as e:
            print(f"Error en modelo crear_usuario: {e}")
            return None, "Error interno al registrar usuario"
        finally:
            close_db_connection(conn)

    @staticmethod
    def validar_login(correo, contraseña):
        """Valida las credenciales de login del usuario"""
        conn = get_db_connection()
        if not conn:
            return None, "Error de conexión con la base de datos"
        
        try:
            with conn.cursor() as cursor:
                # Solo permitir login si el estado es "Activo"
                query = "SELECT * FROM usuario WHERE correo = %s AND estado = 'Activo'"
                cursor.execute(query, (correo,))
                user = cursor.fetchone()

                if not user:
                    return None, "El correo no está registrado o la cuenta está inactiva"

                if user["contraseña"] != contraseña:
                    return None, "Contraseña incorrecta"

                return user, "Login exitoso"
                
        except Exception as e:
            print(f"Error en modelo validar_login: {e}")
            return None, "Error interno del servidor"
        finally:
            close_db_connection(conn)
            
    @staticmethod
    def guardar_archivo_medico(medical_file):
        """Guarda el archivo médico en el sistema de archivos"""
        if not medical_file:
            return None
            
        try:
            upload_dir = "uploads/medical_files"
            os.makedirs(upload_dir, exist_ok=True)
            file_path = f"{upload_dir}/{medical_file.filename}"
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(medical_file.file, buffer)
                
            return file_path
        except Exception as e:
            print(f"Error al guardar archivo médico: {e}")
            return None

    @staticmethod
    def obtener_usuario_por_id(usuario_id):
        """Obtiene un usuario por su ID"""
        conn = get_db_connection()
        if not conn:
            return None
    
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM usuario WHERE ID = %s"
                cursor.execute(query, (usuario_id,))
                user = cursor.fetchone()
                return user
        except Exception as e:
            print(f"Error en modelo obtener_usuario_por_id: {e}")
            return None
        finally:
            close_db_connection(conn)

    @staticmethod
    def obtener_usuario_por_correo(correo):
        """Obtiene un usuario por su correo"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                query = "SELECT * FROM usuario WHERE correo = %s"
                cursor.execute(query, (correo,))
                user = cursor.fetchone()
                return user
        except Exception as e:
            print(f"❌ Error en modelo obtener_usuario_por_correo: {e}")
            return None
        finally:
            close_db_connection(conn)

