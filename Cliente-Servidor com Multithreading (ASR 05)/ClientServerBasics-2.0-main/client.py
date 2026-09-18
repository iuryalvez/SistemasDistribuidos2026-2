from socket import *
from constCS import HOST, PORT

def fazer_requisicao(comando, texto):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((HOST, PORT))
    
    # Protocolo: COMMAND|PAYLOAD
    mensagem_formatada = f"{comando}|{texto}"
    s.send(mensagem_formatada.encode())
    
    data = s.recv(1024)
    print(f"Resultado ({comando}): {data.decode()}")
    s.close()

fazer_requisicao("UPPER", "Hello World")
fazer_requisicao("REVERSE", "Hello World")