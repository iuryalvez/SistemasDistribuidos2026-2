import zmq
import json
import time
from constCS_v2 import *

context = zmq.Context()
p2 = f"tcp://{HOST}:{PORT2}"
s = context.socket(zmq.REQ)
s.connect(p2)

client_id = "Cliente-2"
print(f"[{client_id}] Conectado ao servidor em {p2}")

# 1. Requisicao de ECHO
payload_echo = {
    "type": "ECHO",
    "client_id": client_id,
    "content": "Requisicao vinda da porta 2"
}
print(f"\n[{client_id}] Enviando ECHO...")
s.send_string(json.dumps(payload_echo))
res_echo = json.loads(s.recv_string())
print(f"[{client_id}] Resposta ECHO: {res_echo.get('echo')} (Req #{res_echo.get('request_id')})")

time.sleep(0.5)

# 2. Requisicao de HEALTH CHECK
payload_health = {
    "type": "HEALTH",
    "client_id": client_id
}
print(f"\n[{client_id}] Consultando status de saude (HEALTH)...")
s.send_string(json.dumps(payload_health))
res_health = json.loads(s.recv_string())
print(f"[{client_id}] Status de Saude do Servidor:")
print(f"  -> Status: {res_health.get('status')}")
print(f"  -> Uptime: {res_health.get('uptime_seconds')} segundos")
print(f"  -> Total de requisicoes atendidas: {res_health.get('total_requests')}")
print(f"  -> Endpoints ativos: {res_health.get('server_endpoints')}")
print(f"  -> Timestamp: {res_health.get('timestamp')}")

time.sleep(0.5)

# 3. Envio de comando STOP para encerramento gracioso
payload_stop = {
    "type": "STOP",
    "client_id": client_id
}
print(f"\n[{client_id}] Enviando comando STOP para o servidor...")
s.send_string(json.dumps(payload_stop))
res_stop = json.loads(s.recv_string())
print(f"[{client_id}] Resposta STOP: {res_stop.get('message')}")

s.close()
context.term()
print(f"\n[{client_id}] Finalizado.")
