# Serviço de nomes em gRPC, a partir do template do professor
# (gRPC-SimpleNamingService-main/python/SimpleNamingService.py).
# Mudanças: regras de bind/rebind/unbind/lookup, lock para as threads do gRPC
# e persistência dos registros em um arquivo JSON.
import argparse
import json
import os
import threading
from concurrent import futures

import grpc
import SimpleNamingService_pb2
import SimpleNamingService_pb2_grpc


class SimpleNamingServer(SimpleNamingService_pb2_grpc.SimpleNamingServiceServicer):

  def __init__(self, db_path):
    self.db_path = db_path
    # O gRPC atende cada requisição em uma thread do pool: o lock evita que
    # dois binds simultâneos do mesmo nome passem pela verificação ao mesmo tempo.
    self.lock = threading.Lock()
    self.nameDB = self.load()

  # ---------- persistência ----------
  def load(self):
    if not os.path.exists(self.db_path):
      return {}
    with open(self.db_path) as f:
      db = json.load(f)
    print(f'[NS] {len(db)} registro(s) carregado(s) de {self.db_path}: {list(db)}', flush=True)
    return db

  def save(self):
    # Escreve em um arquivo temporário e troca de uma vez, para nunca deixar
    # o JSON pela metade se o processo cair durante a escrita.
    tmp = self.db_path + '.tmp'
    with open(tmp, 'w') as f:
      json.dump(self.nameDB, f, indent=2)
    os.replace(tmp, self.db_path)

  # ---------- operações ----------
  def Bind(self, request, context):
    with self.lock:
      if request.name in self.nameDB:
        print(f'[NS] Bind   {request.name} -> NOK (nome já registrado)', flush=True)
        return SimpleNamingService_pb2.StatusMsg(status='NOK')
      self.nameDB[request.name] = {'address': request.address.ipaddress,
                                   'port': request.address.portnumber}
      self.save()
    print(f'[NS] Bind   {request.name} -> {request.address.ipaddress}:{request.address.portnumber} OK', flush=True)
    return SimpleNamingService_pb2.StatusMsg(status='OK')

  def Lookup(self, request, context):
    with self.lock:
      reg = self.nameDB.get(request.name)
    if reg is None:
      # O .proto do professor não tem campo de status no AddressMsg:
      # endereço vazio significa "nome não encontrado".
      print(f'[NS] Lookup {request.name} -> não encontrado', flush=True)
      return SimpleNamingService_pb2.AddressMsg(ipaddress='', portnumber='')
    print(f'[NS] Lookup {request.name} -> {reg["address"]}:{reg["port"]}', flush=True)
    return SimpleNamingService_pb2.AddressMsg(ipaddress=reg['address'], portnumber=reg['port'])

  def Rebind(self, request, context):
    with self.lock:
      if request.name not in self.nameDB:
        print(f'[NS] Rebind {request.name} -> NOK (nome não registrado)', flush=True)
        return SimpleNamingService_pb2.StatusMsg(status='NOK')
      self.nameDB[request.name] = {'address': request.address.ipaddress,
                                   'port': request.address.portnumber}
      self.save()
    print(f'[NS] Rebind {request.name} -> {request.address.ipaddress}:{request.address.portnumber} OK', flush=True)
    return SimpleNamingService_pb2.StatusMsg(status='OK')

  def Unbind(self, request, context):
    with self.lock:
      if request.name not in self.nameDB:
        print(f'[NS] Unbind {request.name} -> NOK (nome não registrado)', flush=True)
        return SimpleNamingService_pb2.StatusMsg(status='NOK')
      del self.nameDB[request.name]
      self.save()
    print(f'[NS] Unbind {request.name} OK', flush=True)
    return SimpleNamingService_pb2.StatusMsg(status='OK')


def serve(port, db_path):
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  SimpleNamingService_pb2_grpc.add_SimpleNamingServiceServicer_to_server(
    SimpleNamingServer(db_path), server)
  server.add_insecure_port(f'[::]:{port}')
  server.start()
  print(f'[NS] Serviço de nomes ouvindo na porta {port}', flush=True)
  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    server.stop(grace=1)
    print('[NS] Encerrado.', flush=True)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Serviço de nomes gRPC')
  parser.add_argument('--port', default='5678')
  parser.add_argument('--db', default='names.json', help='arquivo JSON com os registros')
  args = parser.parse_args()
  serve(args.port, args.db)
