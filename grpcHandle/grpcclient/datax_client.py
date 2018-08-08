import grpc
import os
import sys
try:
    import settings
except ImportError:
    PRO_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, PRO_ROOT_PATH)
    import settings
# import the generated classes
import core_function_pb2
import core_function_pb2_grpc

host = settings.HOST
port = str(settings.PORT)
# open a gRPC channel
url = host + ':' + port
channel = grpc.insecure_channel(url)

# create a stub (client)
stub = core_function_pb2_grpc.DataxCommandCallStub(channel)

# create a valid request message
print(sys.argv[1], sys.argv[2])
file_info = core_function_pb2.FileInfo(filedir=sys.argv[1], filename=sys.argv[2])

# make the call
response = stub.datax_command_call(file_info)
print(response.res)

assert response.res == 'success'
