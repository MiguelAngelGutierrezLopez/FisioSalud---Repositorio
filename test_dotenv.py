# test_dotenv.py
import sys
print(f"Python path: {sys.executable}")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv importado correctamente")
    
    import os
    load_dotenv()
    
    # Mostrar variables cargadas
    print(f"\n📋 Variables cargadas:")
    print(f"DB_HOST: {os.getenv('DB_HOST', 'No encontrado')}")
    print(f"DB_NAME: {os.getenv('DB_NAME', 'No encontrado')}")
    
except ImportError as e:
    print(f"❌ Error importando: {e}")
    print("\n📝 Solución:")
    print("1. Asegúrate de tener el entorno virtual activado")
    print("2. Ejecuta: pip install python-dotenv")
    print("3. Reinicia VS Code")