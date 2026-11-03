"""Mede o tempo de resposta e o tamanho das mensagens do serviço Employee
em REST (Flask) e em gRPC, fazendo as mesmas operações nos dois.

Os dois servidores precisam estar rodando:
  RESTful-WS-Example-main/EmployeeService.py   (porta 5678)
  gRPC-WS-Example-main/python/EmployeeService.py (porta 50051)
"""
import argparse
import os
import statistics
import sys
import time

import grpc
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gRPC-WS-Example-main', 'python'))
import EmployeeService_pb2 as pb
import EmployeeService_pb2_grpc as pb_grpc


def medir(funcao, n, aquecimento):
    for _ in range(aquecimento):
        funcao()
    tempos = []
    for _ in range(n):
        inicio = time.perf_counter()
        funcao()
        tempos.append((time.perf_counter() - inicio) * 1000)
    tempos.sort()
    return {
        'media': statistics.mean(tempos),
        'mediana': statistics.median(tempos),
        'p95': tempos[int(len(tempos) * 0.95) - 1],
        'por_seg': 1000 / statistics.mean(tempos),
    }


def linha(nome, r, req_bytes, resp_bytes):
    print(f"{nome:<34} {r['media']:>7.3f} {r['mediana']:>8.3f} {r['p95']:>7.3f} {r['por_seg']:>8.0f} {req_bytes:>8} {resp_bytes:>8}")


def listar(sessao, base, stub, vazio, n, aq):
    resp = sessao.get(base)
    qtd = len(resp.json()['emps'])
    linha(f'REST GET /employee ({qtd} func.)', medir(lambda: sessao.get(base), n, aq), 0, len(resp.content))
    resp = stub.ListAllEmployees(vazio)
    qtd = len(resp.employee_data)
    linha(f'gRPC ListAllEmployees ({qtd} func.)', medir(lambda: stub.ListAllEmployees(vazio), n, aq), 0, resp.ByteSize())


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--rest-port', default='5678')
    p.add_argument('--grpc-port', default='50051')
    p.add_argument('-n', type=int, default=2000, help='chamadas por operação')
    p.add_argument('--extras', type=int, default=100, help='funcionários criados antes de medir a listagem grande')
    args = p.parse_args()
    aq = max(args.n // 20, 10)

    base = f'http://{args.host}:{args.rest_port}/empdb/employee'
    sessao = requests.Session()
    canal = grpc.insecure_channel(f'{args.host}:{args.grpc_port}')
    stub = pb_grpc.EmployeeServiceStub(canal)

    print(f'{args.n} chamadas por operação, {aq} de aquecimento')
    print('Bytes = corpo da mensagem (JSON ou Protobuf), sem cabeçalhos HTTP\n')
    print(f"{'Operação':<34} {'Média':>7} {'Mediana':>8} {'p95':>7} {'Cham/s':>8} {'Req (B)':>8} {'Resp (B)':>8}")
    print(f"{'':<34} {'(ms)':>7} {'(ms)':>8} {'(ms)':>7}")

    # Buscar um funcionário
    resp = sessao.get(base + '/201')
    linha('REST GET /employee/201', medir(lambda: sessao.get(base + '/201'), args.n, aq), 0, len(resp.content))
    msg = pb.EmployeeID(id=201)
    resp = stub.GetEmployeeDataFromID(msg)
    linha('gRPC GetEmployeeDataFromID', medir(lambda: stub.GetEmployeeDataFromID(msg), args.n, aq), msg.ByteSize(), resp.ByteSize())

    # Listar todos
    vazio = pb.EmptyMessage()
    listar(sessao, base, stub, vazio, args.n, aq)

    # Criar funcionários e listar de novo
    t_rest, t_grpc = [], []
    for i in range(args.extras):
        dados = {'id': str(1000 + i), 'name': f'Funcionario {i}', 'title': 'Programmer'}
        inicio = time.perf_counter()
        sessao.post(base, json=dados)
        t_rest.append((time.perf_counter() - inicio) * 1000)
        msg = pb.EmployeeData(id=1000 + i, name=f'Funcionario {i}', title='Programmer')
        inicio = time.perf_counter()
        stub.CreateEmployee(msg)
        t_grpc.append((time.perf_counter() - inicio) * 1000)
    req_json = len(requests.Request('POST', base, json=dados).prepare().body)
    print(f"{'REST POST /employee':<34} {statistics.mean(t_rest):>7.3f} {statistics.median(t_rest):>8.3f} {'':>7} {'':>8} {req_json:>8}")
    print(f"{'gRPC CreateEmployee':<34} {statistics.mean(t_grpc):>7.3f} {statistics.median(t_grpc):>8.3f} {'':>7} {'':>8} {msg.ByteSize():>8}")

    listar(sessao, base, stub, vazio, args.n, aq)

    canal.close()


if __name__ == '__main__':
    main()
