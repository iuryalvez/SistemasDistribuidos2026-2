# Comparação gRPC x RESTful (ASR 12)

O mesmo serviço de cadastro de funcionários implementado de duas formas, em **REST** (Flask, JSON sobre HTTP/1.1) e em **gRPC** (Protocol Buffers sobre HTTP/2), e um script que mede as duas com as mesmas operações.

| Versão | Servidor | Cliente | Porta | Interface |
|---|---|---|---|---|
| REST | `RESTful-WS-Example-main/EmployeeService.py` | `EmployeeServiceClient.py` | 5678 | Recursos e verbos HTTP em `/empdb/employee` |
| gRPC | `gRPC-WS-Example-main/python/EmployeeService.py` | `EmployeeClient.py` | 50051 | Operações definidas em `protos/EmployeeService.proto` |

```
.
├── ENUNCIADO.md
├── benchmark.py                      # mede tempo e tamanho das mensagens nas duas versões
├── RESTful-WS-Example-main/
│   ├── EmployeeService.py            # servidor Flask
│   ├── EmployeeServiceClient.py      # cliente com requests
│   └── const.py                      # IP e porta do servidor
└── gRPC-WS-Example-main/
    ├── protos/EmployeeService.proto  # contrato do serviço
    └── python/
        ├── EmployeeService.py        # servidor gRPC
        ├── EmployeeClient.py         # cliente com o stub gerado
        ├── const.py                  # IP e porta do servidor
        └── EmployeeService_pb2*.py   # código gerado pelo grpc_tools.protoc
```

## As duas interfaces

| Operação | REST | gRPC |
|---|---|---|
| Listar todos | `GET /empdb/employee` | `ListAllEmployees(EmptyMessage)` |
| Buscar um | `GET /empdb/employee/<id>` | `GetEmployeeDataFromID(EmployeeID)` |
| Criar | `POST /empdb/employee` com JSON no corpo | `CreateEmployee(EmployeeData)` |
| Alterar nome/cargo | `PUT /empdb/employee/<id>` com JSON no corpo | `UpdateEmployeeTitle(EmployeeTitleUpdate)` |
| Alterar salário | `PUT /empdb/employee/<id>/<salario>` | (não existe) |
| Remover | `DELETE /empdb/employee/<id>` | `DeleteEmployee(EmployeeID)` |

No REST a interface é genérica (URL + verbo HTTP + JSON) e qualquer cliente HTTP a usa, até o `curl`. No gRPC a interface é específica da aplicação: cada operação tem nome, tipo de entrada e tipo de saída no `.proto`, e o cliente chama métodos de um stub gerado a partir dele.

## Tecnologias

- **Python 3.12** com `venv` próprio da pasta.
- **Flask** 3.1.3 e **requests** 2.34.2 na versão REST.
- **gRPC** (`grpcio` e `grpcio-tools` 1.85.1) e **Protocol Buffers** (`protobuf` 7.36.2) na versão gRPC.

## 1. Preparação

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask requests grpcio grpcio-tools
```

O código gerado do gRPC já está em `gRPC-WS-Example-main/python/`. Para gerar de novo depois de mudar o `.proto`:

```bash
cd gRPC-WS-Example-main/python
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/EmployeeService.proto
```

Os clientes leem o endereço do servidor em `const.py` (`127.0.0.1` por padrão). Para rodar cliente e servidor em máquinas diferentes, troque o IP nos dois `const.py` pelo IP do servidor e libere as portas 5678 (REST) e 50051 (gRPC) no firewall.

## 2. Execução dos exemplos

Cada versão usa dois terminais, com o venv ativo.

### REST

```bash
cd RESTful-WS-Example-main
python EmployeeService.py        # terminal 1
python EmployeeServiceClient.py  # terminal 2
```

Saída do cliente:

```
Will connect to: http://127.0.0.1:5678/empdb/employee
Calling GET on endpoint: http://127.0.0.1:5678/empdb/employee
{'emps': [{'id': '101', 'name': 'Arício Segundo', 'salary': '2000', 'title': 'Technical Leader'}, {'id': '201', 'name': 'Rusmão Terceiro', 'salary': '3000', 'title': 'Sr Software Engineer'}]}
Calling GET on endpoint: http://127.0.0.1:5678/empdb/employee/201
{'emp': [{'id': '201', 'name': 'Rusmão Terceiro', 'salary': '3000', 'title': 'Sr Software Engineer'}]}
Calling PUT on endpoint: http://127.0.0.1:5678/empdb/employee/101
[{'id': '101', 'name': 'Arício Segundo', 'salary': '2000', 'title': 'Programmer'}]
Calling PUT on endpoint: http://127.0.0.1:5678/empdb/employee/201/4000
[{'id': '201', 'name': 'Rusmão Terceiro', 'salary': '4000', 'title': 'Sr Software Engineer'}]
Calling POST on endpoint: http://127.0.0.1:5678/empdb/employee
{'id': '301', 'name': 'Juaríssimo Salvo', 'title': 'Sr Programmer'}
Calling DELETE on endpoint: http://127.0.0.1:5678/empdb/employee/101
{'response': 'Success'}
Calling PUT on endpoint: http://127.0.0.1:5678/empdb/employee/201/40000/Programmer
HTTP Error
404 Client Error: NOT FOUND for url: http://127.0.0.1:5678/empdb/employee/201/40000/Programmer
```

A última chamada usa uma URL que o servidor não tem e recebe o erro HTTP 404.

### gRPC

```bash
cd gRPC-WS-Example-main/python
python EmployeeService.py   # terminal 1
python EmployeeClient.py    # terminal 2
```

Saída do cliente:

```
Employee's data: id: 101
name: "Saravanan S"
title: "Technical Leader"

Added new employee OK
Updated employee OK
Deleted employee OK
All employees: employee_data {
  id: 101
  name: "Saravanan S"
  title: "Technical Leader"
}
employee_data {
  id: 301
  name: "Jose da Silva"
  title: "Senior Programmer"
}
```

Os dois servidores guardam os dados em memória: para repetir a saída acima, reinicie o servidor antes de rodar o cliente de novo.

## 3. Medição de desempenho

`benchmark.py` faz as mesmas operações nas duas versões e mede o tempo de cada chamada no cliente (com `time.perf_counter`) e o tamanho do corpo das mensagens (JSON no REST, Protobuf no gRPC, sem os cabeçalhos HTTP). Cada operação é chamada N vezes depois de um aquecimento; em seguida o script cria 100 funcionários em cada servidor e mede a listagem de novo.

Com os dois servidores recém-iniciados:

```bash
python benchmark.py -n 5000
```

Opções: `--host` (IP dos servidores), `--rest-port`, `--grpc-port`, `-n` (chamadas por operação) e `--extras` (funcionários criados antes da segunda listagem).

### Resultado

Cliente e servidores na mesma máquina (Linux, 16 núcleos), 5000 chamadas por operação:

```
5000 chamadas por operação, 250 de aquecimento
Bytes = corpo da mensagem (JSON ou Protobuf), sem cabeçalhos HTTP

Operação                             Média  Mediana     p95   Cham/s  Req (B) Resp (B)
                                      (ms)     (ms)    (ms)
REST GET /employee/201               1.802    1.751   2.467      555        0      100
gRPC GetEmployeeDataFromID           0.470    0.443   0.666     2130        3       37
REST GET /employee (2 func.)         1.875    1.834   2.463      533        0      186
gRPC ListAllEmployees (2 func.)      0.487    0.461   0.666     2055        0       74
REST POST /employee                  1.994    1.950                        63
gRPC CreateEmployee                  0.978    0.971                        31
REST GET /employee (102 func.)       1.889    1.854   2.577      529        0     6076
gRPC ListAllEmployees (102 func.)    0.714    0.681   0.952     1401        0     3364
```

| Operação | REST (ms) | gRPC (ms) | REST / gRPC | Resposta REST (B) | Resposta gRPC (B) |
|---|---|---|---|---|---|
| Buscar um | 1,80 | 0,47 | 3,8x | 100 | 37 |
| Listar 2 | 1,88 | 0,49 | 3,8x | 186 | 74 |
| Criar | 1,99 | 0,98 | 2,0x | 63 (requisição) | 31 (requisição) |
| Listar 102 | 1,89 | 0,71 | 2,6x | 6076 | 3364 |

O gRPC respondeu de 2 a 4 vezes mais rápido e com mensagens de 45% a 63% menores. Como tudo roda em `localhost`, a rede quase não pesa: a diferença vem do protocolo e da serialização. Dois pontos explicam a maior parte:

- **Conexão.** O servidor de desenvolvimento do Flask responde com `Connection: close`, então cada chamada REST abre uma conexão TCP nova. O canal gRPC mantém uma conexão HTTP/2 aberta e a reutiliza em todas as chamadas.
- **Formato.** O JSON repete o nome dos campos em toda mensagem e escreve números como texto; o Protobuf identifica os campos por número e codifica inteiros em binário. Na listagem de 102 funcionários a resposta REST também carrega o campo `salary` dos dois funcionários iniciais, que a versão gRPC não tem.

Os números variam de uma máquina para outra; o que se mantém é a proporção entre as duas versões. Em máquinas separadas a latência da rede se soma aos dois lados e a diferença relativa diminui, enquanto a diferença de tamanho das mensagens continua a mesma.
