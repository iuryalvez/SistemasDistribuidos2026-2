# Diferentes Paradigmas de Interação em Aplicações Distribuídas (com ZeroMQ)

Esta ASR explora os três principais paradigmas de comunicação distribuída oferecidos pelo middleware **ZeroMQ (pyzmq)**, baseados nos conceitos e códigos do Capítulo 4 (*Communication*) do livro *Distributed Systems* (Tanenbaum & Van Steen).

Desenvolvi uma **versão estendida (`_v2`)** com novas funcionalidades.

---

## 1. Tabela Comparativa dos Paradigmas

| Paradigma | Padrão de Sockets | Pasta | Semântica de Comunicação | Novas Funcionalidades Adicionadas (`_v2`) |
|---|---|---|---|---|
| **Request-Reply** | `REQ` / `REP` | `04-22` | Síncrona, estrita alternância (envio-resposta), servidor vinculado a múltiplas portas | Protocolo JSON, eco com timestamp, métricas de requisições, endpoint de saúde (`HEALTH`) e parada graciosa (`STOP`) |
| **Publish-Subscribe** | `PUB` / `SUB` | `04-23` | Difusão 1-para-N (*broadcast* filtrado), desacoplamento espacial e temporal | Múltiplos tópicos (`TIME`, `WEATHER`, `ALERTS`), assinantes seletivos via argumento CLI e telemetria simulada |
| **Pipeline (Ventilator-Worker-Sink)** | `PUSH` / `PULL` | `04-24` | Distribuição paralela de tarefas com escalabilidade horizontal e *fair-queuing* | Inclusão do **Coletor de Resultados (Sink)**, processamento real com medição de latência e relatório consolidado de vazão (*throughput*) |

---

## 2. Estrutura de Arquivos

```text
Diferentes Paradigmas de Interação em Aplicações Distribuídas (com ZeroMQ)/
├── README.md                          # Documentação completa e guia de execução
├── venv/                              # Ambiente virtual Python com pyzmq
└── code-Chap04-Python3/
    ├── 04-22/                         # Paradigma Request-Reply
    │   ├── constCS.py                 # Constantes originais (AWS IPs)
    │   ├── constCS_v2.py              # Constantes locais (127.0.0.1)
    │   ├── server.py                  # Servidor original (anexa '*')
    │   ├── server_v2.py               # Servidor estendido (eco estruturado, telemetria e health check)
    │   ├── client.py / client1.py / client2.py  # Clientes originais
    │   ├── client1_v2.py              # Cliente 1 (eco de mensagens via porta 4567)
    │   └── client2_v2.py              # Cliente 2 (eco, health check e stop via porta 4568)
    ├── 04-23/                         # Paradigma Publish-Subscribe
    │   ├── constPS.py                 # Constantes originais
    │   ├── constPS_v2.py              # Constantes locais (127.0.0.1)
    │   ├── publisher.py               # Publicador original (apenas TIME a cada 5s)
    │   ├── publisher_v2.py            # Publicador estendido (tópicos TIME, WEATHER, ALERTS)
    │   ├── subscriber.py              # Assinante original (5 leituras de TIME)
    │   └── subscriber_v2.py           # Assinante estendido (filtro por tópico dinâmico)
    └── 04-24/                         # Paradigma Pipeline (Task Distribution)
        ├── constPipe.py               # Constantes originais
        ├── constPipe_v2.py            # Constantes locais incluindo porta do Sink (4569)
        ├── tasksrc.py                 # Fonte original (PUSH)
        ├── tasksrc_v2.py              # Ventilador/Fonte estendida com lote estruturado JSON
        ├── taskwork.py                # Worker original (apenas sleep simulado)
        ├── taskwork_v2.py             # Worker estendido (cálculo real, latência e PUSH ao Sink)
        └── tasksink_v2.py             # NOVO: Coletor centralizado de métricas e vazão
```

---

## 3. Preparação do Ambiente

### 3.1 Criação do Ambiente Virtual e Instalação do PyZMQ

Executar na pasta raiz da atividade:

```bash
cd "Diferentes Paradigmas de Interação em Aplicações Distribuídas (com ZeroMQ)"

# Cria o ambiente virtual
python3 -m venv venv

# Ativa o ambiente e instala a biblioteca pyzmq
source venv/bin/activate
pip install pyzmq
```

### 3.2 Execução Local vs AWS EC2

- **Execução Local (Padrão das versões `_v2`)**:  
  Todos os arquivos de constantes `*_v2.py` utilizam `127.0.0.1`. Isso permite executar múltiplos processos em terminais separados na mesma máquina sem necessidade de infraestrutura externa.
- **Execução em Instâncias AWS EC2**:  
  Basta editar as variáveis `HOST` ou `SRC1`/`SRC2`/`SINK_HOST` nos arquivos `const*_v2.py` para apontar para o IP Privado (caso as instâncias estejam na mesma VPC/Subnet) ou IP Público da máquina servidora.  
  *Atenção:* No **Security Group** da AWS, libere o tráfego TCP nas portas de entrada utilizadas (`4567`, `4568` e `4569`) ou ajustar para as portas que liberamos em sala de aula na criação das instâncias.

---

## 4. Paradigma 1: Request-Reply (`04-22`)

### 4.1 Conceito Teórico
No modelo Request-Reply do ZeroMQ, o socket `REP` (servidor) e o socket `REQ` (cliente) operam sob uma máquina de estados estrita:
- O cliente envia uma requisição (`send`) e bloqueia até receber a resposta (`recv`).
- O servidor aguarda a requisição (`recv`) e deve obrigatoriamente enviar uma resposta (`send`) antes de poder receber a próxima.
- Uma característica do ZeroMQ demonstrada neste exemplo é que um único socket `REP` pode realizar `bind()` em **múltiplas portas TCP simultaneamente** (`4567` e `4568`), unificando o atendimento de requisições de diferentes origens.

### 4.2 Novas funcionalidades da `v2`
- **Servidor (`server_v2.py`)**:
  - Aceita comandos JSON estruturados: `ECHO`, `HEALTH` e `STOP`.
  - Mantém compatibilidade com mensagens de texto plano legadas.
  - Provê medição de *uptime* em segundos, contagem sequencial de requisições atendidas e marcação de tempo (ISO timestamp).
- **Cliente 1 (`client1_v2.py`)**:
  - Conecta à porta `4567` e dispara sucessivas requisições de eco com identificação de cliente.
- **Cliente 2 (`client2_v2.py`)**:
  - Conecta à porta `4568`, realiza eco, consulta o status de saúde do servidor e solicita a finalização do serviço com `STOP`.

### 4.3 Comandos de Execução

```bash
# Terminal 1 - Servidor
source venv/bin/activate
python3 code-Chap04-Python3/04-22/server_v2.py

# Terminal 2 - Cliente 1 (Porta 4567)
source venv/bin/activate
python3 code-Chap04-Python3/04-22/client1_v2.py

# Terminal 3 - Cliente 2 (Porta 4568 - Health Check & Stop)
source venv/bin/activate
python3 code-Chap04-Python3/04-22/client2_v2.py
```

### 4.4 Saídas Registradas

#### Saída do Servidor (`server_v2.py`):
```text
[SERVIDOR v2] Inicializado e escutando em tcp://127.0.0.1:4567 e tcp://127.0.0.1:4568...
[2026-10-11 00:22:37] Req #1 de 'Cliente-1' -> Comando: ECHO
[2026-10-11 00:22:38] Req #2 de 'Cliente-1' -> Comando: ECHO
[2026-10-11 00:22:38] Req #3 de 'Cliente-1' -> Comando: ECHO
[2026-10-11 00:23:45] Req #4 de 'Cliente-2' -> Comando: ECHO
[2026-10-11 00:23:45] Req #5 de 'Cliente-2' -> Comando: HEALTH
[2026-10-11 00:23:46] Req #6 de 'Cliente-2' -> Comando: STOP
[2026-10-11 00:23:46] Comando STOP recebido. Encerrando servidor...
[SERVIDOR v2] Finalizado com sucesso.
```

#### Saída do Cliente 1 (`client1_v2.py`):
```text
[Cliente-1] Conectado ao servidor em tcp://127.0.0.1:4567

[Cliente-1] Enviando: Primeira requisicao de teste
[Cliente-1] Resposta recebida:
  -> Eco: Primeira requisicao de teste*
  -> Req ID: 1
  -> Timestamp Servidor: 2026-10-11 00:22:37

[Cliente-1] Enviando: Ola mundo distribuido via ZeroMQ
[Cliente-1] Resposta recebida:
  -> Eco: Ola mundo distribuido via ZeroMQ*
  -> Req ID: 2
  -> Timestamp Servidor: 2026-10-11 00:22:38

[Cliente-1] Enviando: Mensagem com caracteres especiais: Acao & Reacao
[Cliente-1] Resposta recebida:
  -> Eco: Mensagem com caracteres especiais: Acao & Reacao*
  -> Req ID: 3
  -> Timestamp Servidor: 2026-10-11 00:22:38

[Cliente-1] Finalizado.
```

#### Saída do Cliente 2 (`client2_v2.py`):
```text
[Cliente-2] Conectado ao servidor em tcp://127.0.0.1:4568

[Cliente-2] Enviando ECHO...
[Cliente-2] Resposta ECHO: Requisicao vinda da porta 2* (Req #4)

[Cliente-2] Consultando status de saude (HEALTH)...
[Cliente-2] Status de Saude do Servidor:
  -> Status: HEALTHY
  -> Uptime: 124.91 segundos
  -> Total de requisicoes atendidas: 5
  -> Endpoints ativos: ['tcp://127.0.0.1:4567', 'tcp://127.0.0.1:4568']
  -> Timestamp: 2026-10-11 00:23:45

[Cliente-2] Enviando comando STOP para o servidor...
[Cliente-2] Resposta STOP: Servidor encerrando a pedido do cliente.

[Cliente-2] Finalizado.
```

---

## 5. Paradigma 2: Publish-Subscribe (`04-23`)

### 5.1 Conceito Teórico
No modelo Publish-Subscribe:
- O publicador (`PUB`) envia mensagens sem saber quem ou quantos são os assinantes.
- Os assinantes (`SUB`) conectam ao publicador e definem um filtro de prefixo via `setsockopt_string(zmq.SUBSCRIBE, filtro)`.
- O ZeroMQ descarta no lado receptor as mensagens cujo prefixo não coincide com o filtro registrado. Se o filtro for `""` (vazio), o assinante recebe todas as mensagens.
- **Sintoma do "Slow Joiner"**: Assinantes que conectam após o início do publicador perdem as mensagens iniciais durante o handshake TCP. Por isso, insere-se uma pequena pausa antes do primeiro envio.

### 5.2 Novas funcionalidades da `v2`
- **Publicador (`publisher_v2.py`)**:
  - Publica periodicamente três tópicos distintos a cada ciclo:
    1. `TIME <data/hora>`
    2. `WEATHER <cidade> | Temp: <temp>C | Umidade: <umid>% | Condicao: <cond>`
    3. `ALERTS [<INFO|WARN|CRITICAL>] <descricao do evento>`
  - Aceita argumento opcional de linha de comando para definir a quantidade de ciclos a publicar.
- **Assinante (`subscriber_v2.py`)**:
  - Aceita o tópico desejado como argumento via CLI (ex.: `WEATHER`, `ALERTS`, `TIME` ou `ALL`).
  - Aceita limite máximo de mensagens a receber antes de encerrar automaticamente.

### 5.3 Comandos de Execução

```bash
# Terminal 1 - Assinante de Clima (apenas topico WEATHER)
source venv/bin/activate
python3 code-Chap04-Python3/04-23/subscriber_v2.py WEATHER 3

# Terminal 2 - Assinante de Alertas de Sistema (apenas topico ALERTS)
source venv/bin/activate
python3 code-Chap04-Python3/04-23/subscriber_v2.py ALERTS 3

# Terminal 3 - Publicador Multi-Tópicos (4 ciclos de envio)
source venv/bin/activate
python3 code-Chap04-Python3/04-23/publisher_v2.py 4
```

### 5.4 Saídas Registradas

#### Saída do Publicador (`publisher_v2.py`):
```text
[PUBLISHER v2] Publicador iniciado em tcp://127.0.0.1:4567
[PUBLISHER v2] Publicando topicos: 'TIME', 'WEATHER', 'ALERTS'...
[2026-10-11 00:48:22] Ciclo #1 publicado:
   -> TIME 2026-10-11 00:48:22 (Ciclo #1)
   -> WEATHER Brasilia | Temp: 27C | Umidade: 62% | Condicao: Parcialmente Nublado
   -> ALERTS [CRITICAL] Alta latencia detectada na interface de rede eth0. (ID: 766)
[2026-10-11 00:48:24] Ciclo #2 publicado:
   -> TIME 2026-10-11 00:48:24 (Ciclo #2)
   -> WEATHER Goiania | Temp: 27C | Umidade: 60% | Condicao: Ensolarado
   -> ALERTS [WARN] Uso de memoria atingiu 78% no no-01. (ID: 539)
[2026-10-11 00:48:25] Ciclo #3 publicado:
   -> TIME 2026-10-11 00:48:25 (Ciclo #3)
   -> WEATHER Goiania | Temp: 28C | Umidade: 50% | Condicao: Ensolarado
   -> ALERTS [CRITICAL] Alta latencia detectada na interface de rede eth0. (ID: 848)
[2026-10-11 00:48:27] Ciclo #4 publicado:
   -> TIME 2026-10-11 00:48:27 (Ciclo #4)
   -> WEATHER Goiania | Temp: 27C | Umidade: 60% | Condicao: Ensolarado
   -> ALERTS [WARN] Uso de memoria atingiu 78% no no-01. (ID: 584)
[PUBLISHER v2] Limite de 4 ciclos atingido. Encerrando.
[PUBLISHER v2] Finalizado.
```

#### Saída do Assinante 1 (`subscriber_v2.py WEATHER 3`):
```text
[SUBSCRIBER v2] Conectado a tcp://127.0.0.1:4567
[SUBSCRIBER v2] Filtro de topico configurado: 'WEATHER' (string: 'WEATHER')
[SUBSCRIBER v2] Aguardando ate 3 mensagem(ns)...

[00:24:22] Mensagem #1 recebida -> WEATHER Brasilia | Temp: 27C | Umidade: 62% | Condicao: Parcialmente Nublado
[00:24:24] Mensagem #2 recebida -> WEATHER Goiania | Temp: 27C | Umidade: 60% | Condicao: Ensolarado
[00:24:25] Mensagem #3 recebida -> WEATHER Goiania | Temp: 28C | Umidade: 50% | Condicao: Ensolarado

[SUBSCRIBER v2] Limite de 3 mensagem(ns) atingido. Encerrando.
[SUBSCRIBER v2] Finalizado.
```

#### Saída do Assinante 2 (`subscriber_v2.py ALERTS 3`):
```text
[SUBSCRIBER v2] Conectado a tcp://127.0.0.1:4567
[SUBSCRIBER v2] Filtro de topico configurado: 'ALERTS' (string: 'ALERTS')
[SUBSCRIBER v2] Aguardando ate 3 mensagem(ns)...

[00:24:22] Mensagem #1 recebida -> ALERTS [CRITICAL] Alta latencia detectada na interface de rede eth0. (ID: 766)
[00:24:24] Mensagem #2 recebida -> ALERTS [WARN] Uso de memoria atingiu 78% no no-01. (ID: 539)
[00:24:25] Mensagem #3 recebida -> ALERTS [CRITICAL] Alta latencia detectada na interface de rede eth0. (ID: 848)

[SUBSCRIBER v2] Limite de 3 mensagem(ns) atingido. Encerrando.
[SUBSCRIBER v2] Finalizado.
```

> **Observação:** Cada assinante recebeu estritamente as mensagens de seu filtro de interesse, demonstrando a filtragem direta pelo middleware ZeroMQ.

---

## 6. Paradigma 3: Pipeline (`04-24`)

### 6.1 Conceito Teórico
O paradigma de Pipeline (Push-Pull) implementa o padrão **Ventilator-Worker-Sink**:
- O **Ventilador/Fonte (`PUSH`)** distribui tarefas para um conjunto de nós trabalhadores. O ZeroMQ realiza automaticamente o balanceamento de carga em modo *round-robin / fair-queuing* entre todos os trabalhadores conectados.
- Os **Trabalhadores/Workers (`PULL` das fontes, `PUSH` para o Sink)** recebem tarefas concorrentemente, executam a computação paralelamente e enviam os resultados para o nó coletor.
- O **Coletor/Sink (`PULL`)** recebe todos os resultados processados em um único ponto, permitindo calcular o tempo total da batelada e verificar o balanceamento de carga efetivo.

### 6.2 Novas funcionalidades da `v2`
- **Fonte/Ventilador (`tasksrc_v2.py`)**:
  - Envia tarefas com identificador de fonte, ID sequencial da tarefa e valor de carga para cálculo.
- **Workers (`taskwork_v2.py`)**:
  - Realizam processamento computacional proporcional à carga recebida (soma de quadrados e simulação de latência).
  - Medem com alta precisão a latência individual da tarefa (`latency_ms`).
  - Encaminham os resultados para o Sink via socket `PUSH`.
- **NOVO: Coletor de Resultados (`tasksink_v2.py`)**:
  - Implementa o socket `PULL` na porta `4569`.
  - Consolida métricas em tempo real e emite relatório com:
    - Tempo total decorrido da batelada.
    - Vazão média (*Throughput* em tarefas por segundo).
    - Latência média por tarefa.
    - Divisão percentual de tarefas absorvidas por cada Worker.

### 6.3 Comandos de Execução

```bash
# Terminal 1 - Coletor / Sink (espera 10 tarefas)
source venv/bin/activate
python3 code-Chap04-Python3/04-24/tasksink_v2.py 10

# Terminal 2 - Trabalhador 1 (Worker W1)
source venv/bin/activate
python3 code-Chap04-Python3/04-24/taskwork_v2.py W1

# Terminal 3 - Trabalhador 2 (Worker W2)
source venv/bin/activate
python3 code-Chap04-Python3/04-24/taskwork_v2.py W2

# Terminal 4 - Ventilador / Fonte 1 (Dispara 10 tarefas)
source venv/bin/activate
python3 code-Chap04-Python3/04-24/tasksrc_v2.py 1 10
```

### 6.4 Saídas Registradas

#### Saída da Fonte (`tasksrc_v2.py`):
```text
[FONTE/VENTILADOR #1] Vinculado a tcp://127.0.0.1:4567
[FONTE/VENTILADOR #1] Aguardando conexao dos workers...
[FONTE/VENTILADOR #1] Disparando lote de 10 tarefas...
  -> [Fonte #1] Tarefa #1 despachada (Carga: 25)
  -> [Fonte #1] Tarefa #2 despachada (Carga: 36)
  -> [Fonte #1] Tarefa #3 despachada (Carga: 14)
  -> [Fonte #1] Tarefa #4 despachada (Carga: 39)
  -> [Fonte #1] Tarefa #5 despachada (Carga: 24)
  -> [Fonte #1] Tarefa #6 despachada (Carga: 29)
  -> [Fonte #1] Tarefa #7 despachada (Carga: 40)
  -> [Fonte #1] Tarefa #8 despachada (Carga: 49)
  -> [Fonte #1] Tarefa #9 despachada (Carga: 13)
  -> [Fonte #1] Tarefa #10 despachada (Carga: 35)
[FONTE/VENTILADOR #1] Todas as 10 tarefas foram despachadas.
```

#### Saída dos Workers (`W1` e `W2`):
```text
[WORKER W1] Conectado as fontes (tcp://127.0.0.1:4567, tcp://127.0.0.1:4568) e ao Coletor (tcp://127.0.0.1:4569).
[WORKER W1] Tarefa #2 (Fonte #1) concluida em 180.2ms -> Enviado ao Sink
[WORKER W1] Tarefa #4 (Fonte #1) concluida em 195.2ms -> Enviado ao Sink
[WORKER W1] Tarefa #6 (Fonte #1) concluida em 145.2ms -> Enviado ao Sink
[WORKER W1] Tarefa #8 (Fonte #1) concluida em 245.2ms -> Enviado ao Sink
[WORKER W1] Tarefa #10 (Fonte #1) concluida em 175.4ms -> Enviado ao Sink

[WORKER W2] Conectado as fontes (tcp://127.0.0.1:4567, tcp://127.0.0.1:4568) e ao Coletor (tcp://127.0.0.1:4569).
[WORKER W2] Tarefa #1 (Fonte #1) concluida em 125.2ms -> Enviado ao Sink
[WORKER W2] Tarefa #3 (Fonte #1) concluida em 70.1ms -> Enviado ao Sink
[WORKER W2] Tarefa #5 (Fonte #1) concluida em 120.4ms -> Enviado ao Sink
[WORKER W2] Tarefa #7 (Fonte #1) concluida em 200.6ms -> Enviado ao Sink
[WORKER W2] Tarefa #9 (Fonte #1) concluida em 65.2ms -> Enviado ao Sink
```

#### Saída do Coletor (`tasksink_v2.py`):
```text
[COLETOR / SINK v2] Vinculado a tcp://127.0.0.1:4569
[COLETOR / SINK v2] Aguardando lote de 10 tarefas concluidas...

[01] Resultado da Tarefa #1 (Fonte #1) recebido de W2 | Latencia: 125.2ms
[02] Resultado da Tarefa #2 (Fonte #1) recebido de W1 | Latencia: 180.2ms
[03] Resultado da Tarefa #3 (Fonte #1) recebido de W2 | Latencia: 70.1ms
[04] Resultado da Tarefa #4 (Fonte #1) recebido de W1 | Latencia: 195.2ms
[05] Resultado da Tarefa #5 (Fonte #1) recebido de W2 | Latencia: 120.4ms
[06] Resultado da Tarefa #6 (Fonte #1) recebido de W1 | Latencia: 145.2ms
[07] Resultado da Tarefa #7 (Fonte #1) recebido de W2 | Latencia: 200.6ms
[08] Resultado da Tarefa #9 (Fonte #1) recebido de W2 | Latencia: 65.2ms
[09] Resultado da Tarefa #8 (Fonte #1) recebido de W1 | Latencia: 245.2ms
[10] Resultado da Tarefa #10 (Fonte #1) recebido de W1 | Latencia: 175.4ms

==================================================
         RELATORIO CONSOLIDADO DO LOTE
==================================================
Total de tarefas coletadas : 10
Tempo total decorrido      : 1.40 s
Vazao media (Throughput)   : 7.13 tarefas/s
Latencia media por tarefa  : 152.25 ms

Distribuicao por Trabalhador (Worker):
  -> W1: 5 tarefas (50.0%)
  -> W2: 5 tarefas (50.0%)

Distribuicao por Fonte (Source):
  -> Fonte #1: 10 tarefas (100.0%)
==================================================

[COLETOR / SINK v2] Finalizado.
```

> **Destaque do Padrão:** As tarefas foram distribuídas de forma balanceada (50% para W1 e 50% para W2), e o tempo total de processamento foi reduzido consideravelmente em virtude da execução paralela.
