from socket import *
import subprocess
from constCS import HOST, PORT

def process_ping(domain):
    try:
        # Executa o ping. -c 3 envia 3 pacotes.
        result = subprocess.run(
            ["ping", "-c", "3", domain],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            return f"SUCESSO:\n{result.stdout}"
        else:
            return f"FALHA:\n{result.stderr or result.stdout}"
    except Exception as e:
        return f"ERRO ao executar ping em {domain}: {str(e)}"

s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind((HOST, PORT))
# Habilita o servidor para aceitar conexões (maior backlog para não recusar)
s.listen(10)
print(f"Servidor SINGLE-THREAD rodando em {HOST}:{PORT}...")

while True:
    (conn, addr) = s.accept()
    print(f"[{addr}] Conexão aceita.")
    data = conn.recv(1024)
    if not data:
        conn.close()
        continue
    
    mensagem = data.decode()
    partes = mensagem.split("|", 1)
    comando = partes[0]
    conteudo = partes[1] if len(partes) > 1 else ""

    # Processa a requisição bloqueando a thread principal
    if comando == "PING":
        print(f"[{addr}] Iniciando ping para: {conteudo}")
        resposta = process_ping(conteudo)
    else:
        resposta = "Comando invalido"
        
    conn.send(resposta.encode())
    conn.close()
    print(f"[{addr}] Conexão encerrada.")
