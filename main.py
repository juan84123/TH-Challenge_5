from fastapi import FastAPI, Query, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional
import database

# Creamos la aplicacion FastAPI
app = FastAPI()

# ---------------------------------------------------------------------------
# TOKENS VALIDOS
# Cada token corresponde a un servicio especifico.
# En produccion esto estaria en una base de datos o variable de entorno,
# pero para este challenge una lista manual es suficiente.
# ---------------------------------------------------------------------------
TOKENS_VALIDOS = {
    "svc_abc123": "payments-service",
    "svc_def456": "auth-service",
    "svc_ghi789": "orders-service"
}

# Creamos la tabla en la base de datos al arrancar el servidor
# Si ya existe, no hace nada (CREATE TABLE IF NOT EXISTS)
database.crear_tabla()


# ---------------------------------------------------------------------------
# MODELO DE DATOS
# Pydantic valida automaticamente que el JSON recibido
# tenga todos estos campos con los tipos correctos.
# Si falta un campo o el tipo es incorrecto, FastAPI devuelve 422.
# ---------------------------------------------------------------------------
class Log(BaseModel):
    timestamp: datetime                                          # Fecha y hora del evento
    service: str                                                 # Nombre del servicio
    severity: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]  # Nivel del log
    message: str                                                 # Descripcion del evento


# ---------------------------------------------------------------------------
# AUTENTICACION
# ---------------------------------------------------------------------------
def verificar_token(authorization: Optional[str]) -> bool:
    """
    Verifica que el token del header Authorization sea valido.
    
    El header debe venir en el formato: Token svc_abc123
    Si el header no existe, viene mal formateado, o el token
    no esta en la lista, retorna False.
    """
    # Si no viene el header, rechazamos
    if not authorization:
        return False

    # Separamos "Token svc_abc123" en ["Token", "svc_abc123"]
    partes = authorization.split(" ")

    # Verificamos que tenga exactamente dos partes y empiece con "Token"
    if len(partes) != 2 or partes[0] != "Token":
        return False

    # Verificamos que el token exista en la lista de tokens validos
    token = partes[1]
    return token in TOKENS_VALIDOS


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------
@app.get("/")
def home():
    """Endpoint de verificacion. Confirma que el servidor esta corriendo."""
    return {"mensaje": "Servidor de logging funcionando"}


@app.post("/logs", status_code=201)
def recibir_log(log: Log, authorization: Optional[str] = Header(default=None)):
    """
    Recibe un log de un servicio y lo guarda en la base de datos.
    
    Requiere un token valido en el header Authorization.
    Formato: Authorization: Token svc_abc123
    
    Si el token es invalido o no existe, devuelve 401.
    Si el JSON es invalido, FastAPI devuelve 422 automaticamente.
    Si todo esta bien, guarda el log y devuelve 201.
    """
    # Verificamos el token antes de procesar nada
    if not verificar_token(authorization):
        return JSONResponse(
            status_code=401,
            content={"error": "Quién sos, bro?"}
        )

    # Guardamos el log en la base de datos
    database.insertar_log(
        timestamp=log.timestamp.isoformat(),
        service=log.service,
        severity=log.severity,
        message=log.message
    )

    return {"mensaje": "Log recibido correctamente"}


@app.get("/logs")
def consultar_logs(
    timestamp_start: str = Query(default=None),
    timestamp_end: str = Query(default=None),
    received_at_start: str = Query(default=None),
    received_at_end: str = Query(default=None)
):
    """
    Devuelve los logs guardados con filtros opcionales por fecha.
    
    Filtros disponibles:
    - timestamp_start: logs con timestamp >= este valor
    - timestamp_end: logs con timestamp <= este valor
    - received_at_start: logs recibidos por el servidor desde esta fecha
    - received_at_end: logs recibidos por el servidor hasta esta fecha
    
    Si no se pasa ningun filtro, devuelve todos los logs.
    Los resultados vienen ordenados del mas reciente al mas viejo.
    """
    logs = database.obtener_logs(
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        received_at_start=received_at_start,
        received_at_end=received_at_end
    )

    return {"total": len(logs), "logs": logs}