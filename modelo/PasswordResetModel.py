# modelo/PasswordResetModel.py
from datetime import datetime, timedelta
import secrets
from bd.conexion_bd import get_db_connection, close_db_connection

class PasswordResetModel:
    @staticmethod
    def generar_token():
        """Genera un token seguro de 32 caracteres"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def guardar_token(usuario_id, token):
        """Guarda el token en la base de datos"""
        conn = get_db_connection()
        if not conn:
            return False
            
        try:
            expiracion = datetime.now() + timedelta(hours=1)
            with conn.cursor() as cursor:
                # Invalidar tokens previos
                cursor.execute(
                    "UPDATE password_reset_tokens SET usado = 1 WHERE usuario_id = %s",
                    (usuario_id,)
                )
                # Insertar nuevo token
                cursor.execute(
                    """INSERT INTO password_reset_tokens 
                       (usuario_id, token, expiracion, usado) 
                       VALUES (%s, %s, %s, 0)""",
                    (usuario_id, token, expiracion)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error guardando token: {e}")
            return False
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def validar_token(token):
        """Valida si el token existe y es válido"""
        conn = get_db_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT pr.*, u.correo, u.nombre 
                       FROM password_reset_tokens pr
                       JOIN usuario u ON pr.usuario_id = u.ID
                       WHERE pr.token = %s 
                       AND pr.usado = 0 
                       AND pr.expiracion > NOW()""",
                    (token,)
                )
                return cursor.fetchone()
        except Exception as e:
            print(f"❌ Error validando token: {e}")
            return None
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def marcar_token_usado(token_id):
        """Marca un token como utilizado"""
        conn = get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE password_reset_tokens SET usado = 1 WHERE id = %s",
                    (token_id,)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error marcando token usado: {e}")
            return False
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def actualizar_contrasena(usuario_id, nueva_contrasena):
        """Actualiza la contraseña del usuario (sin hash)"""
        conn = get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE usuario 
                       SET contraseña = %s, contraseña_confirmada = %s 
                       WHERE ID = %s""",
                    (nueva_contrasena, nueva_contrasena, usuario_id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error actualizando contraseña: {e}")
            return False
        finally:
            close_db_connection(conn)
    
    @staticmethod
    def limpiar_tokens_expirados():
        """Limpia tokens expirados automáticamente"""
        conn = get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM password_reset_tokens WHERE expiracion <= NOW()"
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error limpiando tokens expirados: {e}")
            return False
        finally:
            close_db_connection(conn)
