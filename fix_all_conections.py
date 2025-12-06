import os
import re

def fix_model_file(filepath):
    """Corrige un archivo de modelo que tiene conexión directa"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si tiene conexión directa
        if 'pymysql.connect(' in content and 'get_db_connection' not in content:
            print(f"🔧 Corrigiendo: {filepath}")
            
            # Reemplazar import
            if 'import pymysql' in content:
                content = content.replace('import pymysql', 'from bd.conexion_bd import get_db_connection, close_db_connection')
            
            # Reemplazar método get_db_connection
            if 'def get_db_connection' in content or 'get_db_connection():' in content:
                # Encontrar el método get_db_connection
                lines = content.split('\n')
                new_lines = []
                in_method = False
                method_replaced = False
                
                for line in lines:
                    if 'def get_db_connection' in line or 'get_db_connection():' in line:
                        in_method = True
                        method_replaced = True
                        # Mantener la definición pero cambiar contenido
                        new_lines.append(line)
                        new_lines.append('        """Obtiene conexión a la base de datos usando la conexión centralizada"""')
                        new_lines.append('        try:')
                        new_lines.append('            connection = get_db_connection()')
                        new_lines.append('            if connection:')
                        new_lines.append('                return connection')
                        new_lines.append('            else:')
                        new_lines.append('                print(f"❌ No se pudo obtener conexión a la BD")')
                        new_lines.append('                return None')
                        new_lines.append('        except Exception as e:')
                        new_lines.append('            print(f"❌ Error al conectar a MySQL: {e}")')
                        new_lines.append('            return None')
                    
                    elif in_method:
                        # Saltar líneas del método antiguo hasta encontrar una línea no indentada
                        if line.strip() == '' or line.startswith('    '):
                            continue
                        else:
                            in_method = False
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                
                content = '\n'.join(new_lines)
            
            # Guardar cambios
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        return False
        
    except Exception as e:
        print(f"❌ Error procesando {filepath}: {e}")
        return False

# Buscar en todas las carpetas
print("🔍 Buscando conexiones directas a BD...")
print("=" * 60)

carpetas = ["modelo", "controlador"]
archivos_corregidos = []

for carpeta in carpetas:
    if os.path.exists(carpeta):
        for root, dirs, files in os.walk(carpeta):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    if fix_model_file(filepath):
                        archivos_corregidos.append(filepath)

print("\n" + "=" * 60)
if archivos_corregidos:
    print(f"✅ Corregidos {len(archivos_corregidos)} archivos:")
    for archivo in archivos_corregidos:
        print(f"   - {archivo}")
else:
    print("✅ ¡No se encontraron conexiones directas para corregir!")

print("\n🎯 Verificación manual recomendada:")
print("1. Revisa que los imports sean: 'from bd.conexion_bd import get_db_connection'")
print("2. Revisa que usen 'get_db_connection()' en lugar de 'pymysql.connect()'")