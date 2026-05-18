from fastapi import FastAPI, Query, Header  # FastAPI para crear el servidor, Query para los filtros de la URL, Header para leer headers
from fastapi.responses import JSONResponse  # para poder devolver respuestas con status code personalizado (el 401)
from pydantic import BaseModel              # para definir la estructura del log que esperamos recibir
import database                             # importamos nuestro archivo database.py para usar sus funciones

# creamos la aplicacion, todo el servidor vive aca
app = FastAPI()

# diccionario con los tokens validos
# la clave es el token, el valor es el nombre del servicio al que pertenece
# si el token que manda el cliente no esta aca, lo rechazamos con 401
TOKENS_VALIDOS = {
    "svc_abc123": "payments-service",
    "svc_def456": "auth-service",
    "svc_ghi789": "orders-service"
}

# cuando arranca el servidor, creamos la tabla en la base de datos
# si la tabla ya existe, no hace nada
database.crear_tabla()

# definimos la estructura que debe tener el JSON que recibimos
# si el cliente manda un campo de mas, de menos, o con tipo incorrecto
# FastAPI lo rechaza automaticamente con error 422
class Log(BaseModel):
    timestamp: str  # cuando ocurrio el evento (viene del cliente)
    service: str    # nombre del servicio que genero el log
    severity: str   # nivel del log: INFO, DEBUG, WARNING, ERROR, CRITICAL
    message: str    # descripcion de lo que paso

# endpoint de verificacion
# sirve para confirmar que el servidor esta corriendo
@app.get("/")
def home():
    # devolvemos un mensaje simple, FastAPI lo convierte a JSON automaticamente
    return {"mensaje": "Servidor de logging funcionando"}

# endpoint para recibir UN solo log
# status_code=201 significa que si todo sale bien respondemos con 201 Created
@app.post("/logs", status_code=201)
def recibir_log(log: Log, authorization: str = Header(default="")):
    # Header(default="") le dice a FastAPI que lea el header Authorization del request
    # si el cliente no manda el header, el valor es un string vacio

    # verificamos que el header empiece con "Token "
    # si no empieza asi, el formato es incorrecto y lo rechazamos
    if not authorization.startswith("Token "):
        # JSONResponse nos permite devolver un status code distinto al del endpoint (201)
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    # sacamos solo el token del header
    # "Token svc_abc123" -> "svc_abc123"
    token = authorization.replace("Token ", "")

    # verificamos que el token exista en nuestra lista de tokens validos
    if token not in TOKENS_VALIDOS:
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    # si llegamos aca el token es valido, guardamos el log en la base de datos
    database.insertar_log(
        timestamp=log.timestamp,
        service=log.service,
        severity=log.severity,
        message=log.message
    )

    # respondemos que todo salio bien
    return {"mensaje": "Log recibido correctamente"}

# endpoint para recibir VARIOS logs a la vez en un solo request
# list[Log] significa que esperamos una lista de objetos Log en el body
@app.post("/logs/batch", status_code=201)
def recibir_varios_logs(logs: list[Log], authorization: str = Header(default="")):
    # misma verificacion de token que el endpoint anterior
    if not authorization.startswith("Token "):
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    # sacamos el token del header
    token = authorization.replace("Token ", "")

    # verificamos que el token sea valido
    if token not in TOKENS_VALIDOS:
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    # recorremos la lista y guardamos cada log en la base de datos
    for log in logs:
        database.insertar_log(
            timestamp=log.timestamp,
            service=log.service,
            severity=log.severity,
            message=log.message
        )

    # avisamos cuantos logs se guardaron en total
    return {"mensaje": f"Se recibieron {len(logs)} logs correctamente"}

# endpoint para consultar los logs guardados
# todos los filtros son opcionales, si no se mandan devuelve todos los logs
@app.get("/logs")
def consultar_logs(
    timestamp_start: str = Query(default=None),   # logs con timestamp mayor o igual a esta fecha
    timestamp_end: str = Query(default=None),      # logs con timestamp menor o igual a esta fecha
    received_at_start: str = Query(default=None),  # logs recibidos por el servidor desde esta fecha
    received_at_end: str = Query(default=None)     # logs recibidos por el servidor hasta esta fecha
):
    # Query(default=None) le dice a FastAPI que este parametro viene de la URL
    # ejemplo: /logs?timestamp_start=2025-01-01
    # si no se manda, el valor es None y no se aplica ese filtro
    logs = database.obtener_logs(
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        received_at_start=received_at_start,
        received_at_end=received_at_end
    )

    # devolvemos el total de logs encontrados y la lista completa
    return {"total": len(logs), "logs": logs}