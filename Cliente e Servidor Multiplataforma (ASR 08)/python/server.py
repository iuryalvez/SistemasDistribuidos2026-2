# Servidor Python (Cenário 2: cliente Java -> servidor Python)
import sys, Ice
import Demo


class PrinterI(Demo.Printer):
    def printString(self, s, current=None):
        print(f"[Servidor Python] printString: {s}")
        return s + "*"

    def add(self, a, b, current=None):
        resultado = a + b
        print(f"[Servidor Python] add: {a} + {b} = {resultado}")
        return resultado

    def toUpperCase(self, s, current=None):
        print(f"[Servidor Python] toUpperCase: {s}")
        return s.upper()


with Ice.initialize(sys.argv) as communicator:
    adapter = communicator.createObjectAdapterWithEndpoints("SimpleAdapter", "default -p 5679")
    adapter.add(PrinterI(), Ice.stringToIdentity("SimplePrinter"))
    adapter.activate()
    print("Servidor Python aguardando na porta 5679...")
    communicator.waitForShutdown()
