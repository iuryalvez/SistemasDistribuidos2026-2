import sys, Ice
import Demo
 
class PrinterI(Demo.Printer):
    def printString(self, s, current=None):
        print(s)
        return s + "*"
        
    # Primeiro Método (implementado pelo professor em sala de aula)
    def add(self, a, b, current=None):
        resultado = a + b
        print(f"Recebi pedido para somar {a} e {b} = {resultado}")
        return resultado

    # Segundo Método
    def toUpperCase(self, s, current=None):
        print(f"Recebi pedido para converter: {s}")
        return s.upper()

communicator = Ice.initialize(sys.argv) 

adapter = communicator.createObjectAdapterWithEndpoints("SimpleAdapter", "default -p 5678")
object = PrinterI()
adapter.add(object, Ice.stringToIdentity("SimplePrinter"))
adapter.activate()

communicator.waitForShutdown()
