# gRPC-WS-Example
This is the gRPC equivalent of the RESTful WS example, meant to illustrate the difference between generic interfaces (i.e., RESTful) and application-specific interfaces.

See here for instructions on how to install gRPC and compile the interface specification (.proto): https://grpc.io/docs/languages/python/quickstart/

Step-by-step (steps 1-4 on both machines, client and server):

## 1) Install PIP

$:> sudo apt install python3-pip

## 2) Upgrade PIP

$:> python3 -m pip install --upgrade pip

## 3) Install gRPC runtime

$:> python3 -m pip install grpcio

## 4) Install gRPC tools

$:> python3 -m pip install grpcio-tools

## 5) Clone this repo

## 6) Compile interface specification (Protocol Buffers .proto file)

$:> cd python

$:> python3 -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/EmployeeService.proto

## 7) Run the example (using two differente machines)

### On the first machine:

$:> python3 EmployeeService.py

### On the second machine:

$:> python3 EmployeeClient.py

### Note: open port 50051 on the firewall at EC2 (security group)
