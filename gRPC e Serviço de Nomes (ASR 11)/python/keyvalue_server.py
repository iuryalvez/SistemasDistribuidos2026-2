# Serviço de aplicação 2: armazenamento chave-valor em memória.
import threading
from concurrent import futures

import grpc
import KeyValue_pb2
import KeyValue_pb2_grpc

from naming_client import app_args, serve_registered


class KeyValueServer(KeyValue_pb2_grpc.KeyValueServicer):

  def __init__(self):
    self.store = {}
    self.lock = threading.Lock()  # requisições chegam em threads diferentes

  def Put(self, request, context):
    with self.lock:
      self.store[request.key] = request.value
    print(f'[ChaveValor] Put {request.key}={request.value!r}', flush=True)
    return KeyValue_pb2.StatusMsg(status='OK')

  def Get(self, request, context):
    with self.lock:
      found = request.key in self.store
      value = self.store.get(request.key, '')
    print(f'[ChaveValor] Get {request.key} -> {repr(value) if found else "não encontrada"}', flush=True)
    return KeyValue_pb2.ValueMsg(found=found, value=value)

  def Delete(self, request, context):
    with self.lock:
      status = 'OK' if self.store.pop(request.key, None) is not None else 'NOK'
    print(f'[ChaveValor] Delete {request.key} -> {status}', flush=True)
    return KeyValue_pb2.StatusMsg(status=status)

  def List(self, request, context):
    with self.lock:
      items = [KeyValue_pb2.KeyValueMsg(key=k, value=v) for k, v in sorted(self.store.items())]
    print(f'[ChaveValor] List -> {len(items)} item(ns)', flush=True)
    return KeyValue_pb2.KeyValueList(items=items)


if __name__ == '__main__':
  args = app_args('Servidor gRPC do armazenamento chave-valor', 'ChaveValor', 5680)
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  KeyValue_pb2_grpc.add_KeyValueServicer_to_server(KeyValueServer(), server)
  serve_registered(server, args)
