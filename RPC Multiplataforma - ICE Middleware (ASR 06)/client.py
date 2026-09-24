import sys, Ice
import Demo
 
communicator = Ice.initialize(sys.argv)

base = communicator.stringToProxy("SimplePrinter:tcp -h localhost -p 5678")
printer = Demo.PrinterPrx.checkedCast(base)
if not printer:
    raise RuntimeError("Invalid proxy")

printer.printString("Hello World!")

soma = printer.add(15, 27)
print(f"O servidor somou e retornou: {soma}")

texto_maiusculo = printer.toUpperCase("sistemas distribuidos 2026/2")
print(f"O servidor converteu para: {texto_maiusculo}")
