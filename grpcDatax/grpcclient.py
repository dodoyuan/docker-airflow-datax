import grpc
import sys
# import the generated classes
import core_function_pb2 as  docker_command_pb2
import core_function_pb2_grpc as docker_command_pb2_grpc
# open a gRPC channel
channel = grpc.insecure_channel('172.17.0.1:50051')

# create a stub (client)
stub = docker_command_pb2_grpc.DockerCommandCallStub(channel)

# create a valid request message
print(sys.argv[1])
filename = docker_command_pb2.Data(text=sys.argv[1])

# make the call
response = stub.CommandCall(filename)

print(response.text)

assert response.text=='success'
