# test_variables.py
import os

print("📋 VARIABLES DE ENTORNO EN RAILWAY:")
print("=" * 50)

variables_mysql = ['MYSQLHOST', 'MYSQLPORT', 'MYSQLDATABASE', 'MYSQLUSER', 'MYSQLPASSWORD']
variables_db = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']

print("\n🔍 Variables MYSQL_ (automáticas de Railway):")
for var in variables_mysql:
    if var in os.environ:
        if 'PASSWORD' in var:
            print(f"   {var}: {'*' * len(os.environ[var])}")
        else:
            print(f"   {var}: {os.environ[var]}")
    else:
        print(f"   {var}: NO DEFINIDA")

print("\n🔍 Variables DB_ (manuales):")
for var in variables_db:
    if var in os.environ:
        if 'PASSWORD' in var:
            print(f"   {var}: {'*' * len(os.environ[var])}")
        else:
            print(f"   {var}: {os.environ[var]}")
    else:
        print(f"   {var}: NO DEFINIDA")

print("\n🎯 Configuración que usará la app:")
print(f"   Host: {os.environ.get('MYSQLHOST') or os.environ.get('DB_HOST', 'NO DEFINIDO')}")
print(f"   Port: {os.environ.get('MYSQLPORT') or os.environ.get('DB_PORT', 'NO DEFINIDO')}")
print(f"   Database: {os.environ.get('MYSQLDATABASE') or os.environ.get('DB_NAME', 'NO DEFINIDO')}")