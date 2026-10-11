import zmq
import time
import random
import sys
import json
from constPipe_v2 import *

me = str(sys.argv[1]) if len(sys.argv) > 1 else '1'
total_tasks = int(sys.argv[2]) if len(sys.argv) > 2 else 10

context = zmq.Context()
s = context.socket(zmq.PUSH)

src = SRC1 if me == '1' else SRC2
prt = PORT1 if me == '1' else PORT2
p = f"tcp://{src}:{prt}"
s.bind(p)

print(f"[FONTE/VENTILADOR #{me}] Vinculado a {p}")
print(f"[FONTE/VENTILADOR #{me}] Aguardando conexao dos workers...")
time.sleep(1) # Aguarda workers conectarem

print(f"[FONTE/VENTILADOR #{me}] Disparando lote de {total_tasks} tarefas...")

for i in range(1, total_tasks + 1):
    workload = random.randint(10, 50)
    task_data = {
        "source_id": me,
        "task_id": i,
        "workload": workload,
        "timestamp": time.time()
    }
    s.send_string(json.dumps(task_data))
    print(f"  -> [Fonte #{me}] Tarefa #{i} despachada (Carga: {workload})")
    time.sleep(0.15) # Pequeno intervalo entre despachos

print(f"[FONTE/VENTILADOR #{me}] Todas as {total_tasks} tarefas foram despachadas.")
time.sleep(0.5)
s.close()
context.term()
