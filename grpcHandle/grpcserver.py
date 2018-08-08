# -*- coding:utf8 -*-
import grpc
from concurrent import futures
import time
from settings import PORT
from settings import MAX_WORKERS
# import the generated classes
import core_function_pb2
import core_function_pb2_grpc

from servicefunction import datax_service_function
from servicefunction import mysqldump_service_function
from servicefunction import pieces_defects_process_service_function

# create a gRPC server， 并设置服务最大并发数量
server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))


# 注册datax启动函数服务
class DataxServicer(core_function_pb2_grpc.DataxCommandCallServicer):
    def datax_command_call(self, request, context):
        response = core_function_pb2.Result()
        response.res = datax_service_function.exec_server_command(request.filedir, request.filename)
        return response


core_function_pb2_grpc.add_DataxCommandCallServicer_to_server(
    DataxServicer(), server)


# 注册数据库同步服务
class MysqlDumpService(core_function_pb2_grpc.MysqlDumpCommandCallServicer):
    def mysqldump_command_call(self, request, context):
        response = core_function_pb2.Result()
        response.res = mysqldump_service_function.exec_server_command(request.database, request.user,
                                                                      request.password, request.host,
                                                                      request.port, request.days)
        return response


core_function_pb2_grpc.add_MysqlDumpCommandCallServicer_to_server(
    MysqlDumpService(), server)


# 注册pieces&defects处理服务
class PiecesDefectsService(core_function_pb2_grpc.PiecesDefectsProcessServicer):
    def pieces_defects_ftp_downloader(self, request, context):
        response = core_function_pb2.Result()
        response.res = pieces_defects_process_service_function.exec_ftpdownloader_command()
        return response

    def pieces_defects_main_process(self, request, context):
        response = core_function_pb2.Result()
        response.res = pieces_defects_process_service_function.exec_dataprocess_command()
        return response


core_function_pb2_grpc.add_PiecesDefectsProcessServicer_to_server(
    PiecesDefectsService(), server)

# listen on port 50051
print('Starting server. Listening on port {port}.'.format(port=str(PORT)))
server.add_insecure_port('[::]:{port}'.format(port=str(PORT)))
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
