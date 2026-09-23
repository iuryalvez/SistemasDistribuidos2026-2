from socket import *
import subprocess
import threading
from constCS import HOST, PORT

def process_ping(domain):
    try:
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

def handle_client(conn, addr):
    print(f"[{addr}] Conexão aceita (Thread ativa).")
    try:
        data = conn.recv(1024)
        if data:
            mensagem = data.decode()
            partes = mensagem.split("|", 1)
            comando = partes[0]
            conteudo = partes[1] if len(partes) > 1 else ""

            if comando == "PING":
                print(f"[{addr}] Iniciando ping para: {conteudo}")
                resposta = process_ping(conteudo)
            else:
                resposta = "Comando invalido"
                
            conn.send(resposta.encode())
    except Exception as e:
        print(f"[{addr}] Erro: {e}")
    finally:
        conn.close()
        print(f"[{addr}] Conexão encerrada.")

s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(10)
print(f"Servidor MULTI-THREAD rodando em {HOST}:{PORT}...")

while True:
    (conn, addr) = s.accept()
    # Para cada requisição recebida, dispara uma nova thread para processar o cliente
    t = threading.Thread(target=handle_client, args=(conn, addr))
    t.start()
