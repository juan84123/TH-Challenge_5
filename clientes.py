import requests   # libreria para hacer requests HTTP, la usamos para enviar los logs al servidor
import threading  # libreria para correr varias tareas al mismo tiempo (en paralelo)
import random     # libreria para elegir cosas al azar, la usamos para los mensajes y numeros
from datetime import datetime, timezone  # datetime para la fecha/hora, timezone para usar UTC

# direccion del servidor donde vamos a mandar los logs
BASE_URL = "http://127.0.0.1:8000"

# lista con los tres servicios simulados
# cada servicio es un diccionario con su nombre, token y mensajes posibles
SERVICIOS = [
    {
        "nombre": "payments-service",  # nombre del servicio, va en el campo "service" del log
        "token": "svc_abc123",         # token unico para autenticarse con el servidor
        "mensajes": [
            # cada mensaje es una tupla con dos elementos: (severity, texto del mensaje)
            # el {} dentro del texto se reemplaza con un numero aleatorio mas adelante
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
    # armamos el header de autenticacion con el token del servicio
    # el servidor lee este header para saber si el servicio tiene permiso
    headers = {"Authorization": f"Token {servicio['token']}"}

    # lista vacia donde vamos a guardar los logs antes de mandarlos
    logs = []

    # creamos tantos logs como indica "cantidad" (en este caso 5)
    for i in range(cantidad):

        # elegimos un mensaje al azar de la lista del servicio
        # random.choice devuelve un elemento aleatorio de una lista
        # como cada elemento es una tupla, lo desempaquetamos en dos variables
        severity, mensaje_template = random.choice(servicio["mensajes"])

        # generamos un numero aleatorio entre 1000 y 9999
        # lo usamos para que los mensajes parezcan mas reales
        numero = random.randint(1000, 9999)

        # armamos el diccionario del log con los cuatro campos requeridos
        logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(), # fecha y hora actual en UTC como string
            "service":   servicio["nombre"],                      # nombre del servicio
            "severity":  severity,                                # nivel del log (INFO, ERROR, etc)
            "message":   mensaje_template.format(numero)          # reemplazamos {} con el numero generado
        })

    try:
        # mandamos todos los logs juntos en un solo POST al endpoint /logs/batch
        # json=logs convierte la lista de diccionarios a JSON automaticamente
        r = requests.post(f"{BASE_URL}/logs/batch", json=logs, headers=headers)

        # mostramos en consola cuantos logs se mandaron y el codigo de respuesta del servidor
        print(f"[{servicio['nombre']}] {len(logs)} logs enviados - {r.status_code}")

    except Exception as e:
        # si el servidor no esta corriendo o hay un error de red, mostramos el error
        # sin esto el programa crashearia y los otros servicios no terminarian
        print(f"[{servicio['nombre']}] Error al enviar: {e}")

def simular_servicios():
    # lista vacia donde guardamos los threads antes de arrancarlos
    threads = []

    # creamos un thread por cada servicio de la lista
    for servicio in SERVICIOS:
        # threading.Thread crea un thread que va a ejecutar la funcion enviar_logs
        # target es la funcion que va a correr, args son los argumentos que recibe
        # esto NO arranca el thread todavia, solo lo prepara
        t = threading.Thread(target=enviar_logs, args=(servicio, 5))

        # agregamos el thread a la lista para poder arrancarlo despues
        threads.append(t)

    # arrancamos todos los threads juntos
    # asi los tres servicios envian logs al mismo tiempo en vez de uno por uno
    for t in threads:
        t.start()  # start() arranca el thread, enviar_logs empieza a ejecutarse

    # esperamos que todos los threads terminen antes de seguir
    # sin join() el programa podria terminar antes de que los threads terminen
    for t in threads:
        t.join()  # join() pausa el programa hasta que ese thread termine

    # cuando todos los threads terminaron, mostramos el mensaje final
    print("Todos los servicios terminaron.")

# este bloque solo se ejecuta cuando corres el archivo directamente con "python clientes.py"
# si otro archivo hace "import clientes", este bloque NO se ejecuta
if __name__ == "__main__":
    simular_servicios()