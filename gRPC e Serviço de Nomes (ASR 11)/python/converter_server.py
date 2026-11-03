# Serviço de aplicação 1: Conversor de unidades (temperatura e distância).
from concurrent import futures

import grpc
import Converter_pb2
import Converter_pb2_grpc

from naming_client import app_args, serve_registered

KM_POR_MILHA = 1.609344


def para_celsius(valor, unidade):
  if unidade == 'C':
    return valor
  if unidade == 'F':
    return (valor - 32) * 5 / 9
  return valor - 273.15  # K


def de_celsius(valor, unidade):
  if unidade == 'C':
    return valor
  if unidade == 'F':
    return valor * 9 / 5 + 32
  return valor + 273.15  # K


class ConverterServer(Converter_pb2_grpc.ConverterServicer):

  def ConvertTemperature(self, request, context):
    origem, destino = request.from_unit.upper(), request.to_unit.upper()
    if origem not in ('C', 'F', 'K') or destino not in ('C', 'F', 'K'):
      context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'unidades de temperatura válidas: C, F, K')
    celsius = para_celsius(request.value, origem)
    if celsius < -273.15:
      context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'temperatura abaixo do zero absoluto')
    resultado = round(de_celsius(celsius, destino), 2)
    print(f'[Conversor] {request.value} {origem} -> {resultado} {destino}', flush=True)
    return Converter_pb2.ConversionReply(value=resultado, unit=destino)

  def ConvertDistance(self, request, context):
    origem, destino = request.from_unit.lower(), request.to_unit.lower()
    if origem not in ('km', 'mi') or destino not in ('km', 'mi'):
      context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'unidades de distância válidas: km, mi')
    km = request.value * KM_POR_MILHA if origem == 'mi' else request.value
    resultado = round(km / KM_POR_MILHA if destino == 'mi' else km, 3)
    print(f'[Conversor] {request.value} {origem} -> {resultado} {destino}', flush=True)
    return Converter_pb2.ConversionReply(value=resultado, unit=destino)


if __name__ == '__main__':
  args = app_args('Servidor gRPC do Conversor', 'Conversor', 5679)
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  Converter_pb2_grpc.add_ConverterServicer_to_server(ConverterServer(), server)
  serve_registered(server, args)
