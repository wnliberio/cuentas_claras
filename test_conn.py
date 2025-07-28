import psycopg2
import traceback

try:
    conn = psycopg2.connect(
        dbname="cuentas_claras",
        user="postgres",
        password="postgres",       # la misma contraseña que pusiste al crear el contenedor
        host="localhost",
        port="5432"
    )


    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("✅ Conectado a PostgreSQL:")
    print(version)
    cur.close()
    conn.close()
except Exception as e:
    print("❌ Error al conectar:")
    traceback.print_exc()
