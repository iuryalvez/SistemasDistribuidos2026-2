import zmq
import sys
from datetime import datetime
from constPS_v2 import *

topic_arg = sys.argv[1].upper() if len(sys.argv) > 1 else "WEATHER"
max_msgs = int(sys.argv[2]) if len(sys.argv) > 2 else 5

# Em ZeroMQ, string vazia "" assina todos os tópicos
topic_filter = "" if topic_arg == "ALL" else topic_arg

context = zmq.Context()
s = context.socket(zmq.SUB)
p = f"tcp://{HOST}:{PORT}"
s.connect(p)
s.setsockopt_string(zmq.SUBSCRIBE, topic_filter)

print(f"[SUBSCRIBER v2] Conectado a {p}")
print(f"[SUBSCRIBER v2] Filtro de topico configurado: '{topic_arg}' (string: '{topic_filter}')")
print(f"[SUBSCRIBER v2] Aguardando ate {max_msgs} mensagem(ns)...\n")

received = 0
try:
    while True:
        raw_msg = s.recv_string()
        received += 1
        now_str = datetime.now().strftime("%H:%M:%S")
        print(f"[{now_str}] Mensagem #{received} recebida -> {raw_msg}")

        if max_msgs > 0 and received >= max_msgs:
            print(f"\n[SUBSCRIBER v2] Limite de {max_msgs} mensagem(ns) atingido. Encerrando.")
            break

except KeyboardInterrupt:
    print("\n[SUBSCRIBER v2] Interrompido pelo usuario.")

finally:
    s.close()
    context.term()
    print("[SUBSCRIBER v2] Finalizado.")
