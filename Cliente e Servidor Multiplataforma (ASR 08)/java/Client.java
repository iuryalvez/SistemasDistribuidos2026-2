// Cliente Java (Cenário 2: cliente Java -> servidor Python)
import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.ObjectPrx;
import com.zeroc.Ice.Util;

import Demo.PrinterPrx;

public class Client {
    public static void main(String[] args) {
        try (Communicator communicator = Util.initialize(args)) {
            ObjectPrx base = communicator.stringToProxy("SimplePrinter:default -h localhost -p 5679");
            PrinterPrx printer = PrinterPrx.checkedCast(base);
            if (printer == null) {
                throw new Error("Invalid proxy");
            }

            System.out.println("printString -> " + printer.printString("Hello World vindo do Java!"));
            System.out.println("add(15, 27) -> " + printer.add(15, 27));
            System.out.println("toUpperCase -> " + printer.toUpperCase("sistemas distribuidos 2026/2"));
        }
    }
}
