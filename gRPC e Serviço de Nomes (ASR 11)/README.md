# gRPC e Serviço de Nomes (ASR 11)

Dois serviços de aplicação em **gRPC**, cada um em seu próprio processo, um **serviço de nomes** também em gRPC (a partir do template) e um cliente que descobre os servidores pelo serviço de nomes antes de fazer as requisições.

| Processo | Arquivo | Porta padrão | Operações |
|---|---|---|---|
| Serviço de nomes | `python/naming_server.py` | 5678 | `Bind`, `Lookup`, `Unbind`, `Rebind` |
| Serviço 1: Conversor | `python/converter_server.py` | 5679 | `ConvertTemperature` (C, F, K), `ConvertDistance` (km, mi) |
| Serviço 2: ChaveValor | `python/keyvalue_server.py` | 5680 | `Put`, `Get`, `Delete`, `List` |
| Cliente | `python/client.py` | | `lookup` + chamadas aos dois serviços |

```
.
├── ENUNCIADO.md
├── gRPC-SimpleNamingService-main/   # template original
├── protos/
│   ├── SimpleNamingService.proto    # contrato do serviço de nomes (copiado do template)
│   ├── Converter.proto              # contrato do serviço 1
│   └── KeyValue.proto               # contrato do serviço 2
└── python/
    ├── naming_server.py             # serviço de nomes
    ├── naming_client.py             # lookup / register (bind→rebind) / unregister (unbind)
    ├── converter_server.py
    ├── keyvalue_server.py
    ├── client.py
    └── *_pb2.py, *_pb2_grpc.py      # código gerado pelo grpc_tools.protoc
```

## Fluxo

```
  converter_server ──bind/rebind/unbind──┐
                                         ▼
  keyvalue_server ──bind/rebind/unbind──► naming_server (5678) ◄──lookup── client
        ▲                                                                     │
        └──────────────── requisições gRPC diretas (Put, Get, Convert...) ────┘
```

1. Ao subir, cada servidor de aplicação faz `bind(nome, ip, porta)`. Se o nome já existe (o servidor caiu e voltou em outro endereço), recebe `NOK` e faz `rebind`.
2. O cliente faz `lookup(nome)` e recebe `ip:porta`. A partir daí fala direto com o servidor; o serviço de nomes não fica no caminho das requisições.
3. Ao ser encerrado (Ctrl+C ou `kill`), o servidor faz `unbind`, mas só se o registro ainda aponta para ele.

## Escolhas de design

| Decisão | Escolha | Motivo |
|---|---|---|
| Serviços de aplicação | Conversor (sem estado) e ChaveValor (com estado em memória) | Mostram os dois tipos de serviço; tudo calculável sem internet |
| Contratos | Um `.proto` por serviço, mantendo o `SimpleNamingService.proto` do template | O cliente do template (`testNS.py`) continua compatível com o serviço de nomes |
| Regras do serviço de nomes | `Bind` recusa nome repetido; `Rebind` e `Unbind` dão `NOK` se o nome não existe; `Lookup` devolve endereço vazio quando não acha | No template, `Bind` duplicava nomes e `Rebind` quebrava com nome inexistente. Como o `AddressMsg` do template não tem status, endereço vazio = "não encontrado" |
| Concorrência | `threading.Lock` no serviço de nomes e no ChaveValor | O `grpc.server` atende cada requisição numa thread do `ThreadPoolExecutor`; sem lock, dois `bind` simultâneos do mesmo nome poderiam passar |
| Persistência | Registros do serviço de nomes em `names.json`, gravado a cada mudança (arquivo temporário + `os.replace`) | O comentário do template pede trocar a lista por algo persistente; os registros sobrevivem a um reinício do serviço de nomes. A troca atômica evita JSON pela metade |
| Quem registra | O próprio servidor (`bind` ao subir, `rebind` se já existe, `unbind` ao sair) | As quatro operações aparecem no fluxo real, como num registry de RMI |
| `unbind` seguro | Antes do `unbind`, o servidor faz `lookup` e só remove se o registro for dele | Evita que uma instância antiga apague o registro da instância nova que fez `rebind` |
| Endereço anunciado | `--host` (IP que vai no `bind`) separado do endereço de escuta (`[::]`, todas as interfaces) | Atrás de NAT ou na nuvem, o IP público não aparece na interface da máquina; o servidor escuta em tudo e anuncia o IP pelo qual é alcançado |
| Erros de aplicação | `context.abort(INVALID_ARGUMENT, ...)` para unidade inválida ou abaixo do zero absoluto | É o jeito padrão do gRPC de devolver erro; o cliente recebe `grpc.RpcError` com código e mensagem |
| Registro "velho" | Se um servidor cai sem `unbind` (ex.: `kill -9`), o nome continua registrado; o cliente trata o `UNAVAILABLE` | Limitação conhecida de serviços de nomes simples; resolvida quando o servidor volta e faz `rebind` |

## Tecnologias

- **Python 3.12** com `venv` próprio da pasta.
- **gRPC** (`grpcio` 1.85.1): RPC sobre HTTP/2, com stubs gerados a partir do contrato.
- **Protocol Buffers** (`protobuf` 7.36.2): linguagem de definição de interface (`.proto`) e serialização binária das mensagens.
- **grpcio-tools** 1.85.1: traz o `protoc`, que gera os `*_pb2.py` (mensagens) e `*_pb2_grpc.py` (stubs e servicers).
- **JSON** (biblioteca padrão) para a persistência do serviço de nomes.

## 1. Preparação (uma vez só)

```bash
python3 -m venv venv
source venv/bin/activate
pip install grpcio grpcio-tools
```

O código gerado já está em `python/`. Para gerar de novo depois de mudar algum `.proto`:

```bash
cd python
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/*.proto
```

## 2. Execução (tudo na mesma máquina)

Cada comando num terminal, com o venv ativo e dentro de `python/`:

```bash
# Terminal 1: serviço de nomes
python naming_server.py

# Terminal 2: serviço 1
python converter_server.py

# Terminal 3: serviço 2
python keyvalue_server.py

# Terminal 4: cliente
python client.py
```

Argumentos (todos opcionais): `naming_server.py --port 5678 --db names.json`; servidores de aplicação `--name`, `--host`, `--port`, `--ns IP:PORTA`; cliente `--ns IP:PORTA`.

## 3. Saídas reais

### Cliente com os três servidores no ar

```
[Cliente] serviço de nomes em 127.0.0.1:5678
[Cliente] lookup Conversor -> 127.0.0.1:5679
  ConvertTemperature(100 C -> F) = 212.0 F
  ConvertTemperature(98.6 F -> C) = 37.0 C
  ConvertTemperature(0 C -> K) = 273.15 K
  ConvertDistance(42.195 km -> mi) = 26.219 mi
  ConvertDistance(26.2 mi -> km) = 42.165 km
  ConvertTemperature(-300 C -> K) = erro INVALID_ARGUMENT: temperatura abaixo do zero absoluto
[Cliente] lookup ChaveValor -> 127.0.0.1:5680
  Put(disciplina='Sistemas Distribuidos') = OK
  Put(asr='11') = OK
  Put(middleware='gRPC') = OK
  Get(middleware) = found=True value='gRPC'
  Delete(asr) = OK
  Get(asr) = found=False
  List() = [('disciplina', 'Sistemas Distribuidos'), ('middleware', 'gRPC')]
[Cliente] lookup ServicoInexistente -> não encontrado
```

### Rebind: o Conversor cai sem `unbind` e volta em outra porta

Com `kill -9` no Conversor, o registro fica apontando para um endereço morto e o cliente recebe:

```
[Cliente] lookup Conversor -> 127.0.0.1:5679
  falha ao acessar Conversor em 127.0.0.1:5679: UNAVAILABLE
```

Subindo de novo com `python converter_server.py --port 5681`:

```
[Conversor] ouvindo na porta 5681
[Conversor] bind 127.0.0.1:5681 -> NOK
[Conversor] rebind 127.0.0.1:5681 -> OK
```

e o cliente passa a encontrar `lookup Conversor -> 127.0.0.1:5681`, com as mesmas respostas de antes.

### Persistência: reinício do serviço de nomes

`names.json` depois do rebind:

```json
{
  "Conversor": { "address": "127.0.0.1", "port": "5681" },
  "ChaveValor": { "address": "127.0.0.1", "port": "5680" }
}
```

Ao reiniciar o serviço de nomes, os registros voltam sem os servidores precisarem fazer `bind` de novo:

```
[NS] 2 registro(s) carregado(s) de names.json: ['Conversor', 'ChaveValor']
[NS] Serviço de nomes ouvindo na porta 5678
[NS] Lookup Conversor -> 127.0.0.1:5681
[NS] Lookup ChaveValor -> 127.0.0.1:5680
```

### Unbind: encerrando os servidores (Ctrl+C ou `kill`)

```
[Conversor] unbind -> OK
[Conversor] encerrado.
```

Log do serviço de nomes e cliente logo depois:

```
[NS] Unbind Conversor OK
[NS] Unbind ChaveValor OK
[NS] Lookup Conversor -> não encontrado
[NS] Lookup ChaveValor -> não encontrado
```

Se uma instância antiga fecha depois que outra já fez `rebind` do mesmo nome, ela não apaga o registro novo:

```
[Conversor] ouvindo na porta 5679
[Conversor] bind 127.0.0.1:5679 -> OK
[Conversor] registro aponta para outro endereço, unbind ignorado
[Conversor] encerrado.
```

### Compatibilidade com o cliente do template

O `testNS.py` do template, apontado para `127.0.0.1:5678`, roda sem mudanças contra o `naming_server.py`:

```
Added new name binding OK
Returned IP address: 3.232.34.176 and port number: 5679
Added new name binding OK
Returned IP address: 34.203.80.210 and port number: 5680
Removed name binding OK
Returned IP address:  and port number: 
```

### Log completo do serviço de nomes na primeira execução

```
[NS] Serviço de nomes ouvindo na porta 5678
[NS] Bind   Conversor -> 127.0.0.1:5679 OK
[NS] Bind   ChaveValor -> 127.0.0.1:5680 OK
[NS] Lookup Conversor -> 127.0.0.1:5679
[NS] Lookup ChaveValor -> 127.0.0.1:5680
[NS] Lookup ServicoInexistente -> não encontrado
[NS] Bind   Conversor -> NOK (nome já registrado)
[NS] Rebind Conversor -> 127.0.0.1:5681 OK
```

## 4. Rodando em máquinas diferentes

Só mudam dois argumentos: `--host`, o IP que cada servidor anuncia no `bind`, e `--ns`, o endereço do serviço de nomes. Funciona em qualquer conjunto de máquinas que se alcancem pela rede: computadores na mesma rede local, servidores próprios ou máquinas virtuais em nuvem.

### 4.1 Requisitos

- Python 3 em cada máquina, com esta pasta e o `venv` preparado como na seção 1.
- Portas TCP **5678 a 5681** liberadas no firewall das máquinas que rodam servidores. No Ubuntu, com `ufw`: `sudo ufw allow 5678:5681/tcp`.
- Saber o IP pelo qual o cliente alcança cada servidor.

### 4.2 Execução

Exemplo com quatro máquinas (os IPs são ilustrativos):

| Máquina | Roda | IP |
|---|---|---|
| A | `naming_server.py` | 192.168.0.10 |
| B | `converter_server.py` | 192.168.0.11 |
| C | `keyvalue_server.py` | 192.168.0.12 |
| D | `client.py` | |

```bash
# Máquina A: serviço de nomes
python naming_server.py

# Máquina B: Conversor, anunciando o próprio IP e apontando para o serviço de nomes
python converter_server.py --host 192.168.0.11 --ns 192.168.0.10:5678

# Máquina C: ChaveValor
python keyvalue_server.py --host 192.168.0.12 --ns 192.168.0.10:5678

# Máquina D: cliente
python client.py --ns 192.168.0.10:5678
```

O cliente deve imprimir `lookup Conversor -> 192.168.0.11:5679` e `lookup ChaveValor -> 192.168.0.12:5680`, seguido das mesmas respostas da seção 3. Os dois serviços também podem ficar na mesma máquina, desde que em portas diferentes.

Para manter um processo rodando depois de fechar o terminal ou a sessão SSH: `nohup python naming_server.py > ns.log 2>&1 &` (ou use `tmux`).

### 4.3 Cuidados

- **`--host` é o IP que o cliente usa**, não necessariamente o da interface da máquina. Atrás de NAT ou na nuvem, a máquina só enxerga o IP privado; se o cliente está fora dessa rede, anuncie o IP público.
- **Testar o Rebind**: encerre um servidor e suba de novo em outra porta (`--port`) ou em outra máquina. O `bind` dá `NOK`, o servidor faz `rebind` e o cliente passa a achar o endereço novo sem mudar nada.
- **Erro `UNAVAILABLE` no cliente**: quase sempre é porta fechada no firewall, processo parado ou `--host` errado. Teste a porta com `nc -vz 192.168.0.11 5679`.
- **Sem TLS**: o código usa `insecure_channel`/`add_insecure_port`, suficiente para testes. Em produção, use `grpc.ssl_channel_credentials` e restrinja quem pode acessar as portas.

### 4.4 Exemplo na AWS (EC2)

1. No console da AWS (EC2 → Launch instance), crie as instâncias com **Ubuntu 24.04** e tipo `t3.micro` (ou outro pequeno). Crie ou reaproveite um par de chaves `.pem`.
2. No **Security Group**, que faz o papel do firewall, adicione regras de entrada (Inbound rules):
   - SSH, TCP 22, origem: seu IP.
   - Custom TCP, portas **5678-5681**, origem: os IPs das outras máquinas e o seu (ou `0.0.0.0/0`, menos seguro).
3. Anote o **IP público** de cada instância. Ele muda quando a instância é parada e ligada de novo; para um IP fixo, associe um **Elastic IP**.
4. Prepare cada instância:

```bash
ssh -i minha-chave.pem ubuntu@<IP público>
sudo apt update && sudo apt install -y python3-venv git
git clone https://github.com/iuryalvez/SistemasDistribuidos2026-2.git
cd "SistemasDistribuidos2026-2/gRPC e Serviço de Nomes (ASR 11)"
python3 -m venv venv && source venv/bin/activate
pip install grpcio grpcio-tools
cd python
```

5. Rode os comandos da seção 4.2 trocando os IPs de exemplo pelos IPs públicos. Se o cliente também roda dentro da mesma VPC, os IPs privados (`172.31.x.x`) servem.
6. Para testar o Rebind de forma natural, pare e ligue a instância do Conversor: o IP público muda, e basta subir o servidor com o novo `--host`.
7. Desligue ou encerre as instâncias ao terminar, para não gerar custos.
