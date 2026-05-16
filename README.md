🎬 1. Escenario & Desafío
Después del caos de los sockets, la consulta mortal, y un sistema colapsado por memes mal rankeados… el equipo de Penguin Academy reconstruyó la civilización.
Pero olvidaron algo. Algo crítico. Algo… que nadie había logueado.

Y así, nace tu nueva misión:
🧠 Diseñar un Servicio de Logging Distribuido, porque si nadie registró el error, técnicamente no pasó.
    "Los sistemas caen. Los logs sobreviven." — proverbio DevOps

Tu objetivo es que múltiples servicios simulados (a.k.a. scripts random que tiran errores falsos) envíen sus logs a un servidor central, que todo lo guarda, todo lo analiza, y —con suerte— no explota.
🧩 2. Objetivo Técnico
Construí un sistema de logging distribuido con:
    ✅ Servicios simulados que generan logs y los envían por HTTP.
    ✅ Un servidor central de logging que recibe, valida, guarda y devuelve logs.
    ✅ Autenticación con tokens para que no se cuele ningún log anónimo.
    ✅ Endpoint /logs para recibir y consultar logs, con filtros por fecha.
    ✅ Todo guardado en base de datos, no en tus sueños.

🛠️ 3. ¿Qué vas a construir?
🔹 Servicios Simulados (Clientes de Logging)
    Simulá varios "servicios" que:
        Generan logs falsos (pero convincentes).
        Envían estos logs en formato JSON a tu servidor central con método POST.p
        Incluyen en el header un token válido con el formato:

        Authorization: Token TU_TOKEN_AQUÍ
    Cada log debe contener:
        timestamp: fecha y hora exacta del evento.
        service: nombre del servicio que lo generó.
        severity: nivel (INFO, DEBUG, ERROR, etc).
        message: descripción de lo que pasó (o no pasó).

🔹 Servidor Central (Tu joyita backend)
    Recibe los logs enviados a: POST /logs
    Verifica el token de autenticación.
    Guarda los logs en una base de datos.
    Soporta múltiples logs enviados a la vez (sin morirse).
    Crea también un endpoint para consultar los logs: GET /logs

Debe aceptar filtros opcionales como:
    timestamp_start y timestamp_end
    received_at_start y received_at_end
    Debe devolver los resultados de forma clara, legible y ordenada, como si alguien lo fuera a presentar en una reunión que nadie pidió.

🔐 4. Autenticación
    Crea una lista manual de tokens válidos para los servicios.
    Cada servicio debe enviar su token en el Authorization Header.
    Si el token es inválido, el servidor responde con error y un mensaje seco pero honesto: {"error": "Quién sos, bro?"}

🧠 5. Consideraciones Técnicas
    📦 No te preocupes por lo técnico al inicio. Primero entendé la arquitectura.
    🧪 Podés testear con Postman o curl antes de automatizar.
    🧹 Asegurate de que los logs estén bien formateados y se guarden sin drama.
    🔁 Pensá en la optimización: si tirás 1000 logs seguidos, no debería explotar nada (en teoría).
    🗂️ Usá la base de datos que quieras, pero usala bien.

✅ 6. Checklist de Entrega
    Múltiples servicios simulados generando logs
    Logs enviados en JSON con POST /logs
    Logs guardados correctamente en base de datos
    Endpoint GET /logs con filtros funcionales
    Tokens únicos por servicio y verificación en el servidor
    Respuestas HTTP claras y funcionales
    Código comentado como si tu yo del futuro fuera a leerlo

🧃 7. Bonus (si querés el respeto eterno de los pingüinos)
    📊 Endpoint /stats con métricas:
    Cantidad de logs por servicio
    Logs por nivel de severidad
    Último log recibido por servicio
    🧼 Limpieza automática de logs viejos (DELETE /logs?before=...)
    📤 Simulación de que los servicios envíen logs cada X segundos con cron o threading
    🔒 JWT en vez de tokens estáticos (si querés vivir al límite)

🚀 8. Epílogo
No es solo un servidor.
Es el confesor de los sistemas,
el chismoso oficial de la red,
el testigo silencioso de todos los bugs que nadie quiso ver.

Y vos...
vos sos el arquitecto del silencio digital.

¡Buena suerte, log hero!
Y recordá:
logueá o explotá. 💣📡🐧