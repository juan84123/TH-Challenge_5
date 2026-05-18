import sqlite3                          # modulo de Python para trabajar con bases de datos SQLite
from datetime import datetime, timezone # datetime para fechas y horas, timezone para trabajar en UTC

# nombre del archivo donde SQLite guarda todos los datos
# si el archivo no existe, SQLite lo crea automaticamente cuando nos conectamos
DB_NAME = "logs.db"

def get_connection():
    # abre una conexion al archivo de la base de datos
    # una conexion es el canal de comunicacion entre Python y SQLite
    conn = sqlite3.connect(DB_NAME)
    return conn  # devolvemos la conexion para que quien la llame pueda usarla

def crear_tabla():
    # crea la tabla logs en la base de datos si todavia no existe
    # se llama una sola vez cuando arranca el servidor
    conn = get_connection()  # abrimos la conexion

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
    # INTEGER PRIMARY KEY AUTOINCREMENT: el id se genera solo y se incrementa con cada fila nueva
    # TEXT NOT NULL: el campo es texto y no puede estar vacio
    # IF NOT EXISTS: si la tabla ya existe no hace nada, evita errores al reiniciar el servidor

    conn.commit()  # commit confirma y guarda los cambios permanentemente en el archivo
    conn.close()   # cerramos la conexion para liberar recursos

def insertar_log(timestamp, service, severity, message):
    # generamos el momento exacto en que el servidor recibe el log
    # esto es distinto al timestamp que mando el cliente (que puede ser del pasado)
    received_at = datetime.now(timezone.utc).isoformat()
    # datetime.now(timezone.utc) -> fecha y hora actual en UTC
    # .isoformat() -> convierte la fecha a string: "2026-05-16T14:30:00+00:00"

    conn = get_connection()  # abrimos la conexion

    conn.execute("""
        INSERT INTO logs (timestamp, received_at, service, severity, message)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, received_at, service, severity, message))
    # INSERT INTO logs: agrega una fila nueva a la tabla
    # los ? son placeholders que se reemplazan con los valores de la tupla
    # usar ? en vez de poner los valores directo en el string evita SQL injection
    # SQL injection es cuando alguien manda datos maliciosos para romper o hackear la base de datos

    conn.commit()  # guardamos los cambios
    conn.close()   # cerramos la conexion

def obtener_logs(timestamp_start=None, timestamp_end=None,
                 received_at_start=None, received_at_end=None):
    # todos los parametros tienen valor por defecto None
    # eso significa que son opcionales, si no se pasan no se aplica ese filtro

    conn = get_connection()  # abrimos la conexion

    # query base que trae todos los logs
    # WHERE 1=1 siempre es verdadero, lo usamos como base para agregar filtros con AND despues
    # sin el 1=1 tendriamos que manejar si poner WHERE o AND segun el primer filtro
    query = "SELECT id, timestamp, received_at, service, severity, message FROM logs WHERE 1=1"
    params = []  # lista donde acumulamos los valores de los filtros

    # por cada filtro que llegue con valor, agregamos la condicion a la query
    if timestamp_start:
        query += " AND timestamp >= ?"  # solo logs con timestamp mayor o igual al filtro
        params.append(timestamp_start)  # agregamos el valor a la lista de parametros

    if timestamp_end:
        query += " AND timestamp <= ?"  # solo logs con timestamp menor o igual al filtro
        params.append(timestamp_end)

    if received_at_start:
        query += " AND received_at >= ?"  # solo logs recibidos desde esta fecha
        params.append(received_at_start)

    if received_at_end:
        query += " AND received_at <= ?"  # solo logs recibidos hasta esta fecha
        params.append(received_at_end)

    # ordenamos los resultados del mas reciente al mas viejo
    query += " ORDER BY received_at DESC"

    # ejecutamos la query con los parametros acumulados
    cursor = conn.execute(query, params)

    # fetchall trae todas las filas del resultado de la query
    filas = cursor.fetchall()
    conn.close()  # cerramos la conexion antes de procesar los resultados

    # convertimos cada fila a diccionario para poder devolverla como JSON
    # cada fila es una tupla: (id, timestamp, received_at, service, severity, message)
    # fila[0] es id, fila[1] es timestamp, y asi sucesivamente segun el orden del SELECT
    resultado = []
    for fila in filas:
        resultado.append({
            "id":          fila[0],  # el id autoincremental
            "timestamp":   fila[1],  # cuando ocurrio el evento segun el cliente
            "received_at": fila[2],  # cuando llego el log al servidor
            "service":     fila[3],  # que servicio lo genero
            "severity":    fila[4],  # nivel del log
            "message":     fila[5]   # descripcion del evento
        })

    return resultado  # devolvemos la lista de diccionarios