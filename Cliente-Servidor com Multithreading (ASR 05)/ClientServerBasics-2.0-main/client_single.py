from socket import *
import time
from constCS import HOST, PORT

# Sites solicitados
SITES = [
    "google.com",
    "sigaa.sistemas.ufg.br",
    "ufg.br",
    "gitlab.com",
    "youtube.com",
    "amazon.com"
]

def fazer_requisicao(comando, texto):
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((HOST, PORT))
        
        mensagem_formatada = f"{comando}|{texto}"
        s.send(mensagem_formatada.encode())
        
        # Receber resposta num loop caso ela exceda 1024 bytes
        resposta_completa = ""
        while True:
            data = s.recv(4096)
            if not data:
                break
            resposta_completa += data.decode()
            
        print(f"\n--- Resultado para {texto} ---")
        linhas = [linha for linha in resposta_completa.split('\n') if linha.strip()]
        if len(linhas) > 2:
            print(linhas[0])
            print("...")
            print(linhas[-1])
        else:
            print(resposta_completa)
            
        s.close()
    except Exception as e:
        print(f"Erro ao conectar com servidor para {texto}: {e}")

if __name__ == "__main__":
    print(f"Iniciando requisições em modo SINGLE-THREAD (sequencial)...")
    print(f"Total de sites: {len(SITES)}")
    
    inicio = time.time()
    
    # Envia e espera uma requisição por vez
    for site in SITES:
        fazer_requisicao("PING", site)
        
    fim = time.time()
    print(f"\n=======================================================")
    print(f"Tempo total de execução SINGLE-THREAD: {fim - inicio:.2f} segundos.")
    print(f"=======================================================\n")
