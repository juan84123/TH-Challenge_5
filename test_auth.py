import requests

BASE_URL = "http://127.0.0.1:8000"

log = {
    "timestamp": "2025-05-07T14:30:00Z",
    "service": "auth-service",
    "severity": "ERROR",
    "message": "test"
}

# Caso 1 - Sin token
r = requests.post(f"{BASE_URL}/logs", json=log)
print(f"Sin token: {r.status_code} - {r.json()}")

# Caso 2 - Token valido
r = requests.post(f"{BASE_URL}/logs", json=log, headers={"Authorization": "Token svc_abc123"})
print(f"Token valido: {r.status_code} - {r.json()}")

# Caso 3 - Token invalido
r = requests.post(f"{BASE_URL}/logs", json=log, headers={"Authorization": "Token token_falso"})
print(f"Token invalido: {r.status_code} - {r.json()}")