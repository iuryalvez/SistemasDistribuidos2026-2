import zmq
import json
import time
from datetime import datetime
from constCS_v2 import *

context = zmq.Context()

p1 = f"tcp://{HOST}:{PORT1}"
p2 = f"tcp://{HOST}:{PORT2}"

s = context.socket(zmq.REP)
s.bind(p1)
s.bind(p2)

start_time = time.time()
request_count = 0

print(f"[SERVIDOR v2] Inicializado e escutando em {p1} e {p2}...")

while True:
    raw_msg = s.recv()
    decoded = raw_msg.decode("utf-8")
    request_count += 1
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Tenta decodificar como JSON para comandos estruturados
    try:
        data = json.loads(decoded)
    except Exception:
        data = None

    if isinstance(data, dict):
        cmd = data.get("type", "UNKNOWN").upper()
        client_id = data.get("client_id", "anonimo")
        print(f"[{now_str}] Req #{request_count} de '{client_id}' -> Comando: {cmd}")

        if cmd == "HEALTH":
            uptime = time.time() - start_time
            response = {
                "status": "HEALTHY",
                "uptime_seconds": round(uptime, 2),
                "total_requests": request_count,
                "timestamp": now_str,
                "server_endpoints": [p1, p2]
            }
            s.send_string(json.dumps(response))

        elif cmd == "ECHO":
            content = data.get("content", "")
            response = {
                "status": "OK",
                "echo": f"{content}*",
                "request_id": request_count,
                "client_id": client_id,
                "timestamp": now_str
            }
            s.send_string(json.dumps(response))

        elif cmd == "STOP":
            response = {
                "status": "STOPPING",
                "message": "Servidor encerrando a pedido do cliente.",
                "total_requests": request_count,
                "timestamp": now_str
            }
            s.send_string(json.dumps(response))
            print(f"[{now_str}] Comando STOP recebido. Encerrando servidor...")
            break

        else:
            response = {
                "status": "ERROR",
                "message": f"Comando desconhecido: {cmd}",
                "timestamp": now_str
            }
            s.send_string(json.dumps(response))

    else:
        # Tratamento de mensagem de texto simples legado
        print(f"[{now_str}] Req #{request_count} (Texto Puro): {decoded}")
        if "STOP" in decoded:
            s.send_string(f"[{now_str}] Servidor encerrando...")
            break
        else:
            sent_msg = f"[{now_str} | Req #{request_count}] {decoded}*"
            s.send_string(sent_msg)

s.close()
context.term()
print("[SERVIDOR v2] Finalizado com sucesso.")
