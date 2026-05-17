import requests   # para hacer los POST al servidor
import threading  # para correr los servicios en paralelo
import random     # para elegir mensajes aleatorios
from datetime import datetime, timezone  # para generar el timestamp

# direccion del servidor al que mandamos los logs
BASE_URL = "http://127.0.0.1:8000"

# lista de servicios simulados
# cada servicio tiene su nombre, token y lista de mensajes posibles
SERVICIOS = [
    {
        "nombre": "payments-service",
        "token": "svc_abc123",  # token unico para este servicio
        "mensajes": [
            # cada mensaje es una tupla (severity, texto)
            # el {} se reemplaza con un numero aleatorio despues
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

def enviar_logs(servicio, cantidad):
    # armamos el header con el token del servicio
    # el servidor lo usa para verificar que el servicio es valido
    headers = {"Authorization": f"Token {servicio['token']}"}

    # enviamos la cantidad de logs indicada
    for i in range(cantidad):
        # elegimos un mensaje aleatorio de la lista del servicio
        severity, mensaje_template = random.choice(servicio["mensajes"])

        # generamos un numero aleatorio para hacer el mensaje mas realista
        numero = random.randint(1000, 9999)

        # armamos el log con todos los campos requeridos
        log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),  # hora actual en UTC
            "service":   servicio["nombre"],
            "severity":  severity,
            "message":   mensaje_template.format(numero)  # reemplazamos {} con el numero
        }

        try:
            # mandamos el log al servidor con POST
            r = requests.post(f"{BASE_URL}/logs", json=log, headers=headers)
            # mostramos en consola el resultado de cada envio
            print(f"[{servicio['nombre']}] {severity} - {r.status_code}")
        except Exception as e:
            # si el servidor no esta corriendo, mostramos el error
            print(f"[{servicio['nombre']}] Error al enviar: {e}")

def simular_servicios():
    threads = []

    # creamos un thread por cada servicio
    # un thread es una tarea que corre en paralelo con las demas
    for servicio in SERVICIOS:
        t = threading.Thread(target=enviar_logs, args=(servicio, 5))
        threads.append(t)

    # arrancamos todos los threads a la vez
    # asi los tres servicios envian logs al mismo tiempo
    for t in threads:
        t.start()

    # esperamos que todos los threads terminen antes de continuar
    for t in threads:
        t.join()

    print("Todos los servicios terminaron.")

# este bloque solo se ejecuta cuando corres el archivo directamente
# si otro archivo importa clientes.py, este bloque no se ejecuta
if __name__ == "__main__":
    simular_servicios()