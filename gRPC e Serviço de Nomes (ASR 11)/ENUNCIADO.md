# gRPC e Serviço de Nomes (ASR 11)

Defina e implemente pelos dois serviços para acesso remoto, os quais serão localizados em processos (e máquinas) diferentes. Implemente um cliente que faça acesso a esses serviços (por meio de requisições).

Implemente um Serviço de Nomes para permitir que o cliente descubra o endereço dos serviços remotos. O serviço de nomes deve fornecer as seguintes funções:

- bind — usado por um servidor para registrar seu nome e seu endereço
- lookup — usado pelos clientes para descobrir o endereço de um servidor
- unbind — usado para remover um registro de nomea
- rebind — usado para atualizar o registro de um nome (com um novo endereço)

Tanto o serviço de nomes quando os serviços de aplicação deverão ser implementados em gRPC.

Referência sobre gRPC: https://grpc.io/docs/languages/python/quickstart/

Código base: serviço de nomes simples (template do professor) em `gRPC-SimpleNamingService-main/`.
