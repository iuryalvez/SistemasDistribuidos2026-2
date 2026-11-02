from __future__ import print_function
import logging

import grpc
import SimpleNamingService_pb2
import SimpleNamingService_pb2_grpc

import const

def run():
    with grpc.insecure_channel(const.NS_IPADDR+':'+const.NS_PORT) as channel:
        stub = SimpleNamingService_pb2_grpc.SimpleNamingServiceStub(channel)

        # Register a new name
        appsvc_address = SimpleNamingService_pb2.AddressMsg(ipaddress='3.232.34.176', portnumber='5679')
        response = stub.Bind(SimpleNamingService_pb2.BindMsg(name='AppSvcName123', address=appsvc_address))
        print ('Added new name binding ' + response.status)
        
        # Lookup a name
        response = stub.Lookup(SimpleNamingService_pb2.NameMsg(name='AppSvcName123'))
        print ('Returned IP address: ' + str(response.ipaddress) + ' and port number: ' + str(response.portnumber))

        # Rebind a name
        appsvc_address = SimpleNamingService_pb2.AddressMsg(ipaddress='34.203.80.210', portnumber='5680')
        response = stub.Rebind(SimpleNamingService_pb2.BindMsg(name='AppSvcName123', address=appsvc_address))
        print ('Added new name binding ' + response.status)

        # Lookup the same name again
        response = stub.Lookup(SimpleNamingService_pb2.NameMsg(name='AppSvcName123'))
        print ('Returned IP address: ' + str(response.ipaddress) + ' and port number: ' + str(response.portnumber))

        # Unbing a name
        response = stub.Unbind(SimpleNamingService_pb2.NameMsg(name='AppSvcName123'))
        print ('Removed name binding ' + response.status)

        # Try to lookup the same name again
        response = stub.Lookup(SimpleNamingService_pb2.NameMsg(name='AppSvcName123'))
        print ('Returned IP address: ' + str(response.ipaddress) + ' and port number: ' + str(response.portnumber))

if __name__ == '__main__':
    logging.basicConfig()
    run()
