import requests
import threading
import random
from datetime import datetime, timezone

# URL base del servidor central
BASE_URL = "http://127.0.0.1:8000"

# ---------------------------------------------------------------------------
# DEFINICION DE SERVICIOS SIMULADOS
# Cada servicio tiene:
# - nombre: el nombre que aparece en el campo "service" del log
# - token: el token unico para autenticarse con el servidor
# - mensajes: lista de tuplas (severity, mensaje) para generar logs realistas
# ---------------------------------------------------------------------------
SERVICIOS = [
    {
        "nombre": "payments-service",
        "token": "svc_abc123",
        "mensajes": [
            ("INFO",    "Pago procesado correctamente para orden #{}"),
            ("ERROR",   "Fallo al procesar pago para orden #{}"),
            ("WARNING", "Tiempo de respuesta alto al procesar orden #{}"),
            ("DEBUG",   "Iniciando procesamiento de pago para orden #{}"),
        ]
    },
    {
        "nombre": "auth-service",
        "token": "svc_def456",
        "mensajes": [
            ("INFO",    "Login exitoso para usuario ID {}"),
            ("ERROR",   "Login fallido para usuario ID {}"),
            ("WARNING", "Demasiados intentos fallidos para usuario ID {}"),
            ("DEBUG",   "Verificando token para usuario ID {}"),
        ]
    },
    {
        "nombre": "orders-service",
        "token": "svc_ghi789",
        "mensajes": [
            ("INFO",    "Orden #{} creada correctamente"),
            ("ERROR",   "Error al crear orden #{}"),
            ("WARNING", "Stock bajo para producto en orden #{}"),
            ("DEBUG",   "Procesando items de orden #{}"),
        ]
    }
]


def enviar_log(servicio: dict, cantidad: int):
    """
    Envia una cantidad determinada de logs falsos para un servicio.
    
    Cada log tiene:
    - timestamp: el momento exacto en que se genera
    - service: el nombre del servicio
    - severity y message: elegidos aleatoriamente de la lista del servicio
    
    El token se envia en el header Authorization para autenticarse.
    """
    # Armamos el header de autenticacion con el token del servicio
    headers = {
        "Authorization": f"Token {servicio['token']}"
    }

    for i in range(cantidad):
        # Elegimos un mensaje aleatorio de la lista del servicio
        severity, mensaje_template = random.choice(servicio["mensajes"])

        # Generamos un numero aleatorio para hacer el mensaje mas realista
        numero = random.randint(1000, 9999)

        # Armamos el log con todos los campos requeridos
        log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": servicio["nombre"],
            "severity": severity,
            "message": mensaje_template.format(numero)
        }

        try:
            # Enviamos el log al servidor con POST /logs
            r = requests.post(f"{BASE_URL}/logs", json=log, headers=headers)
            print(f"[{servicio['nombre']}] {severity} - {r.status_code}")
        except Exception as e:
            # Si el servidor no esta disponible, mostramos el error
            print(f"[{servicio['nombre']}] Error al enviar: {e}")


def simular_servicios(logs_por_servicio: int = 5):
    """
    Corre todos los servicios en paralelo usando threading.
    
    Cada servicio corre en su propio hilo, simulando que son
    procesos independientes enviando logs al mismo tiempo.
    
    logs_por_servicio: cuantos logs envia cada servicio.
    """
    threads = []

    # Creamos un thread por cada servicio
    for servicio in SERVICIOS:
        t = threading.Thread(
            target=enviar_log,
            args=(servicio, logs_por_servicio)
        )
        threads.append(t)

    # Arrancamos todos los threads a la vez
    for t in threads:
        t.start()

    # Esperamos que todos terminen antes de continuar
    for t in threads:
        t.join()

    print("\nTodos los servicios terminaron de enviar logs.")


# Punto de entrada del script
if __name__ == "__main__":
    simular_servicios(logs_por_servicio=5)