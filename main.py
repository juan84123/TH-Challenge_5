from fastapi import FastAPI, Query, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import database

# creamos la aplicacion, es el punto de entrada de todo el servidor
app = FastAPI()

# lista de tokens validos
# la clave es el token, el valor es el nombre del servicio
# si el token que manda el cliente no esta aca, lo rechazamos
TOKENS_VALIDOS = {
    "svc_abc123": "payments-service",
    "svc_def456": "auth-service",
    "svc_ghi789": "orders-service"
}

# cuando arranca el servidor, creamos la tabla en la base de datos
# si ya existe, no hace nada
database.crear_tabla()

# esto le dice a FastAPI como tiene que ser el JSON que recibe
# si falta un campo o el tipo es incorrecto, FastAPI rechaza el request solo
class Log(BaseModel):
    timestamp: str  # cuando ocurrio el evento
    service: str    # que servicio lo mando
    severity: str   # nivel del log (INFO, ERROR, etc)
    message: str    # descripcion del evento

# endpoint de prueba para verificar que el servidor esta corriendo
@app.get("/")
def home():
    return {"mensaje": "Servidor de logging funcionando"}

# endpoint para recibir logs
# status_code=201 significa que si todo sale bien, respondemos con 201 Created
@app.post("/logs", status_code=201)
def recibir_log(log: Log, authorization: str = Header(default="")):
    # Header(default="") le dice a FastAPI que lea el header Authorization del request
    # si el cliente no manda el header, el valor es un string vacio

    # verificamos que el header empiece con "Token "
    # si no empiece asi, el formato es incorrecto y lo rechazamos
    if not authorization.startswith("Token "):
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    # sacamos el token del header
    # "Token svc_abc123" -> "svc_abc123"
    token = authorization.replace("Token ", "")

    # verificamos que el token exista en nuestra lista de tokens validos
    if token not in TOKENS_VALIDOS:
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    # si llegamos aca, el token es valido
    # guardamos el log en la base de datos
    database.insertar_log(
        timestamp=log.timestamp,
        service=log.service,
        severity=log.severity,
        message=log.message
    )

    # respondemos que todo salio bien
    return {"mensaje": "Log recibido correctamente"}

# endpoint para consultar logs guardados
# todos los filtros son opcionales, si no se mandan devuelve todos los logs
@app.get("/logs")
def consultar_logs(
    timestamp_start: str = Query(default=None),   # logs desde esta fecha
    timestamp_end: str = Query(default=None),      # logs hasta esta fecha
    received_at_start: str = Query(default=None),  # logs recibidos desde esta fecha
    received_at_end: str = Query(default=None)     # logs recibidos hasta esta fecha
):
    # Query(default=None) le dice a FastAPI que este parametro viene de la URL
    # por ejemplo: /logs?timestamp_start=2025-01-01
    logs = database.obtener_logs(
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        received_at_start=received_at_start,
        received_at_end=received_at_end
    )

    # devolvemos el total de logs y la lista
    return {"total": len(logs), "logs": logs}