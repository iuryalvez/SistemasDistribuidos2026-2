// Servidor Java (Cenário 1: cliente Python -> servidor Java)
import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.Current;
import com.zeroc.Ice.ObjectAdapter;
import com.zeroc.Ice.Util;

public class Server {

    static class PrinterI implements Demo.Printer {
        @Override
        public String printString(String s, Current current) {
            System.out.println("[Servidor Java] printString: " + s);
            return s + "*";
        }

        @Override
        public int add(int a, int b, Current current) {
            int resultado = a + b;
            System.out.println("[Servidor Java] add: " + a + " + " + b + " = " + resultado);
            return resultado;
        }

        @Override
        public String toUpperCase(String s, Current current) {
            System.out.println("[Servidor Java] toUpperCase: " + s);
            return s.toUpperCase();
        }
    }

    public static void main(String[] args) {
        try (Communicator communicator = Util.initialize(args)) {
            ObjectAdapter adapter =
                communicator.createObjectAdapterWithEndpoints("SimpleAdapter", "default -p 5678");
            adapter.add(new PrinterI(), Util.stringToIdentity("SimplePrinter"));
            adapter.activate();
            System.out.println("Servidor Java aguardando na porta 5678...");
            communicator.waitForShutdown();
        }
    }
}
