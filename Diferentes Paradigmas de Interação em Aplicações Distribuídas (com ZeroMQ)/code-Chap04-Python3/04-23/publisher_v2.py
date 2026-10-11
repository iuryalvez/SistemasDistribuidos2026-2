import zmq
import time
import random
import sys
from datetime import datetime
from constPS_v2 import *

context = zmq.Context()
s = context.socket(zmq.PUB)
p = f"tcp://{HOST}:{PORT}"
s.bind(p)

print(f"[PUBLISHER v2] Publicador iniciado em {p}")
print("[PUBLISHER v2] Publicando topicos: 'TIME', 'WEATHER', 'ALERTS'...")

# Aguarda 1s para permitir conexao dos subscribers iniciais (evitar problema de Slow Joiner)
time.sleep(1)

cidades = [
    ("Goiania", 28, 55, "Ensolarado"),
    ("Brasilia", 26, 60, "Parcialmente Nublado"),
    ("Sao Paulo", 21, 75, "Chuva Fraca")
]

alertas = [
    ("INFO", "Rotina de backup concluida com sucesso."),
    ("WARN", "Uso de memoria atingiu 78% no no-01."),
    ("CRITICAL", "Alta latencia detectada na interface de rede eth0.")
]

max_cycles = int(sys.argv[1]) if len(sys.argv) > 1 else None
cycle = 0

try:
    while True:
        cycle += 1
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Topico TIME
        msg_time = f"TIME {now_str} (Ciclo #{cycle})"
        s.send_string(msg_time)

        # 2. Topico WEATHER
        cidade, temp_base, umid_base, cond = random.choice(cidades)
        temp = temp_base + random.randint(-2, 3)
        umid = umid_base + random.randint(-5, 5)
        msg_weather = f"WEATHER {cidade} | Temp: {temp}C | Umidade: {umid}% | Condicao: {cond}"
        s.send_string(msg_weather)

        # 3. Topico ALERTS
        nivel, desc = random.choice(alertas)
        msg_alert = f"ALERTS [{nivel}] {desc} (ID: {random.randint(100, 999)})"
        s.send_string(msg_alert)

        print(f"[{now_str}] Ciclo #{cycle} publicado:")
        print(f"   -> {msg_time}")
        print(f"   -> {msg_weather}")
        print(f"   -> {msg_alert}")

        if max_cycles and cycle >= max_cycles:
            print(f"[PUBLISHER v2] Limite de {max_cycles} ciclos atingido. Encerrando.")
            break

        time.sleep(1.5)

except KeyboardInterrupt:
    print("\n[PUBLISHER v2] Encerrando publicador...")

finally:
    s.close()
    context.term()
    print("[PUBLISHER v2] Finalizado.")
