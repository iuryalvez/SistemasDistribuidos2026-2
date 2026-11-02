from concurrent import futures
import logging

import grpc
import SimpleNamingService_pb2
import SimpleNamingService_pb2_grpc

import const

nameDB=[ ]  # Replace with a proper database for persistence

class SimpleNamingServer(SimpleNamingService_pb2_grpc.SimpleNamingServiceServicer):

  def Bind(self, request, context):
    dat = {
    'name':request.name,
    'address':request.address.ipaddress,
    'port':request.address.portnumber
    }
    nameDB.append(dat)
    return SimpleNamingService_pb2.StatusMsg(status='OK')

  def Lookup(self, request, context):
    reg = [ r for r in nameDB if (r['name'] == request.name) ]
    if len(reg) == 0:
      return SimpleNamingService_pb2.AddressMsg(ipaddress='', portnumber='')
    else:
      return SimpleNamingService_pb2.AddressMsg(ipaddress=reg[0]['address'],
                                                portnumber=reg[0]['port'])

  def Rebind(self, request, context):
    reg = [ r for r in nameDB if (r['name'] == request.name) ]
    reg[0]['address'] = request.address.ipaddress;
    reg[0]['port'] = request.address.portnumber;
    return SimpleNamingService_pb2.StatusMsg(status='OK')

  def Unbind(self, request, context):
    reg = [ r for r in nameDB if (r['name'] == request.name) ]
    if len(reg) == 0:
      return SimpleNamingService_pb2.StatusMsg(status='NOK')

    nameDB.remove(reg[0])
    return SimpleNamingService_pb2.StatusMsg(status='OK')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    SimpleNamingService_pb2_grpc.add_SimpleNamingServiceServicer_to_server(
      SimpleNamingServer(), server)
    server.add_insecure_port('[::]:'+const.NS_PORT)
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
