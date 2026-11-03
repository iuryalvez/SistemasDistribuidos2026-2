# Funções de acesso ao serviço de nomes, usadas pelos servidores de aplicação
# (register/unregister) e pelo cliente (lookup).
import argparse
import signal

import grpc
import SimpleNamingService_pb2
import SimpleNamingService_pb2_grpc


def _stub(ns_addr):
  channel = grpc.insecure_channel(ns_addr)
  return channel, SimpleNamingService_pb2_grpc.SimpleNamingServiceStub(channel)


def lookup(ns_addr, name):
  """Retorna 'ip:porta' do serviço ou None se o nome não estiver registrado."""
  channel, stub = _stub(ns_addr)
  with channel:
    resp = stub.Lookup(SimpleNamingService_pb2.NameMsg(name=name), timeout=5)
  if not resp.ipaddress:
    return None
  return f'{resp.ipaddress}:{resp.portnumber}'


def register(ns_addr, name, host, port):
  """bind; se o nome já existe (servidor reiniciado em outro endereço), rebind."""
  channel, stub = _stub(ns_addr)
  msg = SimpleNamingService_pb2.BindMsg(
    name=name, address=SimpleNamingService_pb2.AddressMsg(ipaddress=host, portnumber=str(port)))
  with channel:
    status = stub.Bind(msg, timeout=5).status
    print(f'[{name}] bind {host}:{port} -> {status}', flush=True)
    if status != 'OK':
      status = stub.Rebind(msg, timeout=5).status
      print(f'[{name}] rebind {host}:{port} -> {status}', flush=True)
  return status


def unregister(ns_addr, name, host, port):
  """unbind, mas só se o registro ainda aponta para este servidor.

  Sem essa verificação, uma instância antiga que fecha depois de outra ter feito
  rebind apagaria o registro da instância nova.
  """
  channel, stub = _stub(ns_addr)
  with channel:
    resp = stub.Lookup(SimpleNamingService_pb2.NameMsg(name=name), timeout=5)
    if (resp.ipaddress, resp.portnumber) != (host, str(port)):
      print(f'[{name}] registro aponta para outro endereço, unbind ignorado', flush=True)
      return 'IGNORED'
    status = stub.Unbind(SimpleNamingService_pb2.NameMsg(name=name), timeout=5).status
  print(f'[{name}] unbind -> {status}', flush=True)
  return status


def app_args(description, default_name, default_port):
  """Argumentos comuns aos servidores de aplicação."""
  parser = argparse.ArgumentParser(description=description)
  parser.add_argument('--name', default=default_name, help='nome registrado no serviço de nomes')
  parser.add_argument('--host', default='127.0.0.1',
                      help='IP que os clientes usam para chegar a este servidor (vai no bind)')
  parser.add_argument('--port', type=int, default=default_port)
  parser.add_argument('--ns', default='127.0.0.1:5678', help='endereço do serviço de nomes')
  return parser.parse_args()


def serve_registered(server, args):
  """Sobe o servidor gRPC, registra no serviço de nomes e faz unbind ao sair."""
  def on_sigterm(signum, frame):
    raise KeyboardInterrupt
  signal.signal(signal.SIGTERM, on_sigterm)

  # Escuta em todas as interfaces; o IP anunciado no bind é o --host.
  server.add_insecure_port(f'[::]:{args.port}')
  server.start()
  print(f'[{args.name}] ouvindo na porta {args.port}', flush=True)
  register(args.ns, args.name, args.host, args.port)
  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    unregister(args.ns, args.name, args.host, args.port)
    server.stop(grace=1)
    print(f'[{args.name}] encerrado.', flush=True)
