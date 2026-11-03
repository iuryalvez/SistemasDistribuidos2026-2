# Cliente: descobre os servidores pelo serviço de nomes (lookup) e faz
# requisições gRPC aos dois serviços de aplicação.
import argparse

import grpc
import Converter_pb2
import Converter_pb2_grpc
import KeyValue_pb2
import KeyValue_pb2_grpc

from naming_client import lookup


def descobrir(ns, nome):
  endereco = lookup(ns, nome)
  print(f'[Cliente] lookup {nome} -> {endereco or "não encontrado"}')
  return endereco


def usar_conversor(endereco):
  with grpc.insecure_channel(endereco) as channel:
    stub = Converter_pb2_grpc.ConverterStub(channel)
    for valor, de, para in [(100, 'C', 'F'), (98.6, 'F', 'C'), (0, 'C', 'K')]:
      r = stub.ConvertTemperature(Converter_pb2.ConversionRequest(value=valor, from_unit=de, to_unit=para), timeout=5)
      print(f'  ConvertTemperature({valor} {de} -> {para}) = {r.value} {r.unit}')
    for valor, de, para in [(42.195, 'km', 'mi'), (26.2, 'mi', 'km')]:
      r = stub.ConvertDistance(Converter_pb2.ConversionRequest(value=valor, from_unit=de, to_unit=para), timeout=5)
      print(f'  ConvertDistance({valor} {de} -> {para}) = {r.value} {r.unit}')
    # Requisição inválida: o servidor responde com um erro gRPC (INVALID_ARGUMENT)
    try:
      stub.ConvertTemperature(Converter_pb2.ConversionRequest(value=-300, from_unit='C', to_unit='K'), timeout=5)
    except grpc.RpcError as e:
      print(f'  ConvertTemperature(-300 C -> K) = erro {e.code().name}: {e.details()}')


def usar_chave_valor(endereco):
  with grpc.insecure_channel(endereco) as channel:
    stub = KeyValue_pb2_grpc.KeyValueStub(channel)
    for chave, valor in [('disciplina', 'Sistemas Distribuidos'), ('asr', '11'), ('middleware', 'gRPC')]:
      r = stub.Put(KeyValue_pb2.KeyValueMsg(key=chave, value=valor), timeout=5)
      print(f'  Put({chave}={valor!r}) = {r.status}')
    r = stub.Get(KeyValue_pb2.KeyMsg(key='middleware'), timeout=5)
    print(f'  Get(middleware) = found={r.found} value={r.value!r}')
    r = stub.Delete(KeyValue_pb2.KeyMsg(key='asr'), timeout=5)
    print(f'  Delete(asr) = {r.status}')
    r = stub.Get(KeyValue_pb2.KeyMsg(key='asr'), timeout=5)
    print(f'  Get(asr) = found={r.found}')
    r = stub.List(KeyValue_pb2.ListRequest(), timeout=5)
    print(f'  List() = {[(i.key, i.value) for i in r.items]}')


def main():
  parser = argparse.ArgumentParser(description='Cliente dos serviços Conversor e ChaveValor')
  parser.add_argument('--ns', default='127.0.0.1:5678', help='endereço do serviço de nomes')
  args = parser.parse_args()
  print(f'[Cliente] serviço de nomes em {args.ns}')

  for nome, usar in [('Conversor', usar_conversor), ('ChaveValor', usar_chave_valor)]:
    endereco = descobrir(args.ns, nome)
    if endereco is None:
      continue
    try:
      usar(endereco)
    except grpc.RpcError as e:
      # Registro "velho": o nome existe, mas o servidor naquele endereço caiu.
      print(f'  falha ao acessar {nome} em {endereco}: {e.code().name}')

  descobrir(args.ns, 'ServicoInexistente')


if __name__ == '__main__':
  main()
