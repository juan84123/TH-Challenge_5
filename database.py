import sqlite3
from datetime import datetime, timezone

# Nombre del archivo de la base de datos
# SQLite guarda todo en un solo archivo en la carpeta del proyecto
DB_NAME = "logs.db"


def get_connection():
    """
    Crea y retorna una conexion a la base de datos.
    row_factory permite que los resultados vengan como
    diccionarios en vez de tuplas, mas facil de trabajar.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def crear_tabla():
    """
    Crea la tabla logs si no existe.
    Se ejecuta automaticamente al arrancar el servidor.
    
    Campos:
    - id: identificador unico autoincremental
    - timestamp: momento del evento segun el cliente (puede ser del pasado)
    - received_at: momento en que el servidor recibio el log (generado por el servidor)
    - service: nombre del servicio que genero el log
    - severity: nivel del log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - message: descripcion del evento
    """
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
    conn.commit()
    conn.close()


def insertar_log(timestamp: str, service: str, severity: str, message: str):
    """
    Inserta un log en la base de datos.
    
    El campo received_at lo genera el servidor en este momento,
    independientemente del timestamp que mando el cliente.
    Se usan queries parametrizadas (?) para evitar SQL injection.
    """
    # Generamos el momento exacto en que el servidor recibe el log
    received_at = datetime.now(timezone.utc).isoformat()

    conn = get_connection()
    conn.execute("""
        INSERT INTO logs (timestamp, received_at, service, severity, message)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, received_at, service, severity, message))
    conn.commit()
    conn.close()


def obtener_logs(
    timestamp_start: str = None,
    timestamp_end: str = None,
    received_at_start: str = None,
    received_at_end: str = None
):
    """
    Consulta logs con filtros opcionales por fecha.
    
    Todos los filtros son opcionales. Si no se pasa ninguno,
    devuelve todos los logs ordenados del mas reciente al mas viejo.
    
    La query se construye dinamicamente agregando clausulas WHERE
    solo para los filtros que llegaron con valor.
    """
    conn = get_connection()

    # Base de la query. WHERE 1=1 permite agregar AND despues sin problemas
    query = "SELECT * FROM logs WHERE 1=1"
    params = []

    # Agregamos cada filtro solo si fue proporcionado
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

    # Ordenamos del mas reciente al mas viejo
    query += " ORDER BY received_at DESC"

    cursor = conn.execute(query, params)
    columnas = [d[0] for d in cursor.description]
    rows = cursor.fetchall()

    # Convertimos a diccionario antes de cerrar la conexion
    resultado = [dict(zip(columnas, row)) for row in rows]
    conn.close()

    return resultado