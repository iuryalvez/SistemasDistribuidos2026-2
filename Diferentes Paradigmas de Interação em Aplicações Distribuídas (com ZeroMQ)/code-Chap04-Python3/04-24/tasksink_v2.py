import zmq
import time
import sys
import json
from collections import defaultdict
from constPipe_v2 import *

expected_tasks = int(sys.argv[1]) if len(sys.argv) > 1 else 20

context = zmq.Context()
receiver = context.socket(zmq.PULL)
sink_addr = f"tcp://{SINK_HOST}:{SINK_PORT}"
receiver.bind(sink_addr)

print(f"[COLETOR / SINK v2] Vinculado a {sink_addr}")
if expected_tasks > 0:
    print(f"[COLETOR / SINK v2] Aguardando lote de {expected_tasks} tarefas concluidas...\n")
else:
    print(f"[COLETOR / SINK v2] Modo continuo ativado. Pressione Ctrl+C para finalizar.\n")

worker_stats = defaultdict(int)
source_stats = defaultdict(int)
total_latency = 0.0
count = 0
start_time = None

try:
    while True:
        raw_msg = receiver.recv_string()
        if start_time is None:
            start_time = time.time() # Inicia cronometro no recebimento da primeira tarefa

        count += 1
        res = json.loads(raw_msg)
        w_id = res.get("worker_id", "Desconhecido")
        s_id = res.get("source_id", "Desconhecido")
        t_id = res.get("task_id", 0)
        lat = res.get("latency_ms", 0.0)

        worker_stats[w_id] += 1
        source_stats[s_id] += 1
        total_latency += lat

        print(f"[{count:02d}] Resultado da Tarefa #{t_id} (Fonte #{s_id}) recebido de {w_id} | Latencia: {lat:.1f}ms")

        if expected_tasks > 0 and count >= expected_tasks:
            total_elapsed = time.time() - start_time
            print("\n" + "="*50)
            print("         RELATORIO CONSOLIDADO DO LOTE")
            print("="*50)
            print(f"Total de tarefas coletadas : {count}")
            print(f"Tempo total decorrido      : {total_elapsed:.2f} s")
            print(f"Vazao media (Throughput)   : {count / total_elapsed:.2f} tarefas/s")
            print(f"Latencia media por tarefa  : {total_latency / count:.2f} ms")
            print("\nDistribuicao por Trabalhador (Worker):")
            for w, qtd in sorted(worker_stats.items()):
                pct = (qtd / count) * 100
                print(f"  -> {w}: {qtd} tarefas ({pct:.1f}%)")
            print("\nDistribuicao por Fonte (Source):")
            for s, qtd in sorted(source_stats.items()):
                pct = (qtd / count) * 100
                print(f"  -> Fonte #{s}: {qtd} tarefas ({pct:.1f}%)")
            print("="*50 + "\n")
            break

except KeyboardInterrupt:
    print(f"\n[COLETOR / SINK v2] Interrompido. Total coletado: {count}.")

finally:
    receiver.close()
    context.term()
    print("[COLETOR / SINK v2] Finalizado.")
