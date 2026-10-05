# Cliente e Servidor Multiplataforma (ASR 08)

Dois cenários usando o middleware **ZeroC ICE** e a mesma interface `Printer.ice` da ASR 06:

| Cenário | Cliente | Servidor | Porta |
|---|---|---|---|
| 1 | Python (`python/client.py`) | Java (`java/Server.java`) | 5678 |
| 2 | Java (`java/Client.java`) | Python (`python/server.py`) | 5679 |

```
.
├── Printer.ice        # contrato único (Slice) compartilhado pelas duas linguagens
├── python/            # server.py, client.py (+ Demo/ gerado pelo slice2py)
└── java/              # Server.java, Client.java, lib/ice-3.7.10.jar (+ Demo/ gerado pelo slice2java)
```

## 1. Preparação (uma vez só)

### Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install zeroc-ice          # compila, demora alguns minutos
cd python && slice2py ../Printer.ice && cd ..
```

### Java
```bash
sudo apt install openjdk-21-jdk-headless
mkdir -p java/lib
wget https://repo1.maven.org/maven2/com/zeroc/ice/3.7.10/ice-3.7.10.jar -O java/lib/ice-3.7.10.jar
cd java
slice2java ../Printer.ice                     # gera a pasta Demo/
javac -cp lib/ice-3.7.10.jar -d . Demo/*.java Server.java Client.java
cd ..
```

## 2. Execução

### Cenário 1 — Cliente Python → Servidor Java
```bash
# Terminal 1
cd java && java -cp lib/ice-3.7.10.jar:. Server.java

# Terminal 2
source venv/bin/activate
cd python && python3 client.py
```

### Cenário 2 — Cliente Java → Servidor Python
```bash
# Terminal 1
source venv/bin/activate
cd python && python3 server.py

# Terminal 2
cd java && java -cp lib/ice-3.7.10.jar:. Client.java
```

Saída esperada no cliente:
```
printString -> Hello World vindo do ...!*
add(15, 27) -> 42
toUpperCase -> SISTEMAS DISTRIBUIDOS 2026/2
```

> O ICE do Python (pip, 3.8) e o do Java (jar, 3.7.10) são versões diferentes, mas
> interoperam porque usam o mesmo protocolo (1.0) e codificação (1.1) na rede.
