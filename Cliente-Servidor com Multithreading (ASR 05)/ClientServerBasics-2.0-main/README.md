O código-fonte a ser usado como base para esta tarefa deve ser o código que resultou da Tarefa ASR 04, o qual contém um par de programas cliente-servidor com as seguintes características:

 - o cliente envia requisições de operações que são processadas no servidor e cujas respostas são retornadas para o cliente;

O que implementar nesta tarefa:

 - o servidor deve disparar uma nova thread para cada requisição recebida;
 - cada requisição do cliente deve ser enviada por uma nova thread, de modo que o cliente possa enviar múltiplas requisições em paralelo (para mais de um servidor, por exemplo);
 - automatizar a geração de requisições no cliente (por exemplo, usando um gerador de números aleatórios para gerar os dados das requisições);

Após implementar e testar o cliente e o servidor multithread, fazer um experimento para medir o desempenho para o envio, processamento e resposta de uma certa quantidade (suficientemente grande) de requisições.

Em seguida, repetir o mesmo experimento com o par cliente-servidor single-threaded (da tarefa anterior) e comparar o desempenho de ambas as implementações, ou seja, o tempo necessário para processar a mesma quantidade de requisições.

Comparar também com o desempenho da versão original, com multithreading apenas no servidor (para isto, você terá que automatizar a geração de requisições, da mesma forma como fez para a versão multithread do cliente).