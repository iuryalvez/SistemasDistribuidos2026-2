import zmq
import json
import time
from constCS_v2 import *

context = zmq.Context()
p1 = f"tcp://{HOST}:{PORT1}"
s = context.socket(zmq.REQ)
s.connect(p1)

client_id = "Cliente-1"
print(f"[{client_id}] Conectado ao servidor em {p1}")

mensagens = [
    "Primeira requisicao de teste",
    "Ola mundo distribuido via ZeroMQ",
    "Mensagem com caracteres especiais: Acao & Reacao"
]

for msg in mensagens:
    payload = {
        "type": "ECHO",
        "client_id": client_id,
        "content": msg
    }
    print(f"\n[{client_id}] Enviando: {msg}")
    s.send_string(json.dumps(payload))

    resposta_raw = s.recv_string()
    resposta = json.loads(resposta_raw)
    print(f"[{client_id}] Resposta recebida:")
    print(f"  -> Eco: {resposta.get('echo')}")
    print(f"  -> Req ID: {resposta.get('request_id')}")
    print(f"  -> Timestamp Servidor: {resposta.get('timestamp')}")
    time.sleep(0.5)

s.close()
context.term()
print(f"\n[{client_id}] Finalizado.")
