# Cliente Python (Cenário 1: cliente Python -> servidor Java)
import sys, Ice
import Demo

with Ice.initialize(sys.argv) as communicator:
    base = communicator.stringToProxy("SimplePrinter:default -h localhost -p 5678")
    printer = Demo.PrinterPrx.checkedCast(base)
    if not printer:
        raise RuntimeError("Invalid proxy")

    print(f"printString -> {printer.printString('Hello World vindo do Python!')}")
    print(f"add(15, 27) -> {printer.add(15, 27)}")
    print(f"toUpperCase -> {printer.toUpperCase('sistemas distribuidos 2026/2')}")
