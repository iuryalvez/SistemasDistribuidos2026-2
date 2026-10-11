import zmq
import time
import sys
import json
from constPipe_v2 import *

me = str(sys.argv[1]) if len(sys.argv) > 1 else 'W1'

context = zmq.Context()

# Socket PULL para receber tarefas das fontes
receiver = context.socket(zmq.PULL)
p1 = f"tcp://{SRC1}:{PORT1}"
p2 = f"tcp://{SRC2}:{PORT2}"
receiver.connect(p1)
receiver.connect(p2)

# Socket PUSH para enviar tarefas concluidas ao Coletor (Sink)
sender = context.socket(zmq.PUSH)
sink_addr = f"tcp://{SINK_HOST}:{SINK_PORT}"
sender.connect(sink_addr)

print(f"[WORKER {me}] Conectado as fontes ({p1}, {p2}) e ao Coletor ({sink_addr}).")
print(f"[WORKER {me}] Aguardando tarefas...\n")

tasks_processed = 0

try:
    while True:
        raw_task = receiver.recv_string()
        tasks_processed += 1
        t_start = time.time()

        task = json.loads(raw_task)
        source_id = task.get("source_id")
        task_id = task.get("task_id")
        workload = task.get("workload", 10)

        # Processamento real + simulado
        # Ex: calculo matematico (soma de quadrados ate workload)
        calc_result = sum(k * k for k in range(workload * 10))
        time.sleep(workload * 0.005) # simula latencia de processamento proporcional
        proc_time = time.time() - t_start

        result_payload = {
            "worker_id": me,
            "source_id": source_id,
            "task_id": task_id,
            "workload": workload,
            "result": calc_result,
            "latency_ms": round(proc_time * 1000, 2),
            "processed_at": time.time()
        }

        # Encaminha resultado ao Coletor (Sink)
        sender.send_string(json.dumps(result_payload))

        print(f"[WORKER {me}] Tarefa #{task_id} (Fonte #{source_id}) concluida em {proc_time*1000:.1f}ms -> Enviado ao Sink")

except KeyboardInterrupt:
    print(f"\n[WORKER {me}] Interrompido. Total processado: {tasks_processed}.")

finally:
    receiver.close()
    sender.close()
    context.term()
    print(f"[WORKER {me}] Finalizado.")
