import grpc
from concurrent import futures
import time

# import the generated classes
import core_function_pb2 as docker_command_pb2
import core_function_pb2_grpc as docker_command_pb2_grpc
# import the original datax_command.py
import core_function


# create a class to define the server functions, derived from
# calculator_pb2_grpc.CalculatorServicer
class CoreServicer(docker_command_pb2_grpc.DockerCommandCallServicer):

    # calculator.square_root is exposed here
    # the request and response are of the data type
    # calculator_pb2.Number
    def CommandCall(self, request, context):
        response = docker_command_pb2.Data()
        response.text = core_function.exec_server_command(request.text)
        return response


# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# use the generated function `add_CalculatorServicer_to_server`
# to add the defined class to the server
docker_command_pb2_grpc.add_DockerCommandCallServicer_to_server(
    CoreServicer(), server)

# listen on port 50051
print('Starting server. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
