from fastapi import FastAPI, Query, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import database

app = FastAPI()

# tokens validos, cada uno pertenece a un servicio
TOKENS_VALIDOS = {
    "svc_abc123": "payments-service",
    "svc_def456": "auth-service",
    "svc_ghi789": "orders-service"
}

# cuando arranca el servidor, creamos la tabla en la base de datos
database.crear_tabla()

# estructura del log que esperamos recibir
class Log(BaseModel):
    timestamp: str
    service: str
    severity: str
    message: str

# endpoint de prueba para verificar que el servidor esta corriendo
@app.get("/")
def home():
    return {"mensaje": "Servidor de logging funcionando"}

# endpoint para recibir UN solo log
@app.post("/logs", status_code=201)
def recibir_log(log: Log, authorization: str = Header(default="")):
    # verificamos que el header empiece con "Token "
    if not authorization.startswith("Token "):
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    # sacamos el token del header
    token = authorization.replace("Token ", "")

    # verificamos que el token exista en nuestra lista
    if token not in TOKENS_VALIDOS:
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    # guardamos el log en la base de datos
    database.insertar_log(
        timestamp=log.timestamp,
        service=log.service,
        severity=log.severity,
        message=log.message
    )
    return {"mensaje": "Log recibido correctamente"}

# endpoint para recibir VARIOS logs a la vez
# recibe una lista de logs en vez de uno solo
@app.post("/logs/batch", status_code=201)
def recibir_varios_logs(logs: list[Log], authorization: str = Header(default="")):
    # misma verificacion de token que el endpoint anterior
    if not authorization.startswith("Token "):
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    token = authorization.replace("Token ", "")
    if token not in TOKENS_VALIDOS:
        return JSONResponse(status_code=401, content={"error": "Quién sos, bro?"})

    # guardamos cada log de la lista uno por uno
    for log in logs:
        database.insertar_log(
            timestamp=log.timestamp,
            service=log.service,
            severity=log.severity,
            message=log.message
        )

    # avisamos cuantos logs se guardaron
    return {"mensaje": f"Se recibieron {len(logs)} logs correctamente"}

# endpoint para consultar logs guardados
@app.get("/logs")
def consultar_logs(
    timestamp_start: str = Query(default=None),
    timestamp_end: str = Query(default=None),
    received_at_start: str = Query(default=None),
    received_at_end: str = Query(default=None)
):
    logs = database.obtener_logs(
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        received_at_start=received_at_start,
        received_at_end=received_at_end
    )
    return {"total": len(logs), "logs": logs}