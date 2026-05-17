import sqlite3
from datetime import datetime, timezone

# nombre del archivo donde SQLite guarda todos los datos
# si no existe, SQLite lo crea automaticamente
DB_NAME = "logs.db"

def get_connection():
    # abre una conexion al archivo de la base de datos
    # una conexion es el canal entre Python y SQLite
    conn = sqlite3.connect(DB_NAME)
    return conn

def crear_tabla():
    # crea la tabla logs si todavia no existe
    # se llama una sola vez al arrancar el servidor
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            received_at TEXT NOT NULL,
            service     TEXT NOT NULL,
            severity    TEXT NOT NULL,
            message     TEXT NOT NULL
        )
    """)
    # commit guarda los cambios permanentemente
    conn.commit()
    # cerramos la conexion para liberar recursos
    conn.close()

def insertar_log(timestamp, service, severity, message):
    # generamos el momento exacto en que el servidor recibe el log
    # esto es distinto al timestamp que mando el cliente
    received_at = datetime.now(timezone.utc).isoformat()

    conn = get_connection()

    # insertamos el log en la tabla
    # los ? son placeholders que se reemplazan con los valores de la tupla
    # esto evita que alguien mande datos maliciosos para romper la base de datos
    conn.execute("""
        INSERT INTO logs (timestamp, received_at, service, severity, message)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, received_at, service, severity, message))

    conn.commit()
    conn.close()

def obtener_logs(timestamp_start=None, timestamp_end=None,
                 received_at_start=None, received_at_end=None):
    conn = get_connection()

    # empezamos con una query base que trae todos los logs
    # WHERE 1=1 siempre es verdadero, nos permite agregar AND despues sin problemas
    query = "SELECT id, timestamp, received_at, service, severity, message FROM logs WHERE 1=1"
    params = []

    # agregamos cada filtro solo si fue enviado (no es None)
    if timestamp_start:
        query += " AND timestamp >= ?"
        params.append(timestamp_start)

    if timestamp_end:
        query += " AND timestamp <= ?"
        params.append(timestamp_end)

    if received_at_start:
        query += " AND received_at >= ?"
        params.append(received_at_start)

    if received_at_end:
        query += " AND received_at <= ?"
        params.append(received_at_end)

    # ordenamos del log mas reciente al mas viejo
    query += " ORDER BY received_at DESC"

    # ejecutamos la query con los filtros acumulados
    cursor = conn.execute(query, params)

    # fetchall trae todas las filas del resultado
    filas = cursor.fetchall()
    conn.close()

    # convertimos cada fila a diccionario para poder devolverla como JSON
    # fila[0] es id, fila[1] es timestamp, y asi sucesivamente
    resultado = []
    for fila in filas:
        resultado.append({
            "id":          fila[0],
            "timestamp":   fila[1],
            "received_at": fila[2],
            "service":     fila[3],
            "severity":    fila[4],
            "message":     fila[5]
        })

    return resultado