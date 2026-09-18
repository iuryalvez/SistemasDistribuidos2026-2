from socket import *
from constCS import HOST, PORT

s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT)) 
# Habilita o servidor para aceitar conexões de clientes
s.listen(1) 

while True:
    (conn, addr) = s.accept()
    data = conn.recv(1024)
    if not data:
        conn.close()
        continue
    
    mensagem = data.decode()
    
    partes = mensagem.split("|", 1) 
    comando = partes[0]
    conteudo = partes[1] if len(partes) > 1 else ""

    # Processa a requisição com base no comando recebido
    if comando == "UPPER":
        resposta = conteudo.upper()
    elif comando == "REVERSE":
        resposta = conteudo[::-1]
    else:
        resposta = "Comando invalido"
        
    conn.send(resposta.encode())
    conn.close()