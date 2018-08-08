# -*- coding:utf-8 -*-
import grpc
import os
import sys
from argparse import ArgumentParser
try:
    import settings
except ImportError:
    PRO_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, PRO_ROOT_PATH)
    import settings

# import the generated classes
import core_function_pb2
import core_function_pb2_grpc


def gRPC_mysql_client(args):
    host = settings.HOST
    port = str(settings.PORT)
    # open a gRPC channel
    url = host + ':' + port
    channel = grpc.insecure_channel(url)

    # create a stub (client)
    stub = core_function_pb2_grpc.MysqlDumpCommandCallStub(channel)

    # create a valid request message
    mysql_info = core_function_pb2.MysqlInfo(database=args.database, user=args.user,
                                             password=args.password,
                                             host=args.host, port=args.port,
                                             days=args.days)
    # make the call
    response = stub.mysqldump_command_call(mysql_info)
    print(response.res)
    assert response.res == 'success'


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--database',
                        type=str,
                        default='aspen_wheel',
                        help='the database you want to dump')
    parser.add_argument('--user',
                        type=str,
                        default='root',
                        help='user to access database')
    parser.add_argument('--password',
                        type=str,
                        default='yuan940110',
                        help='the password to access database')
    parser.add_argument('--host',
                        type=str,
                        default='127.0.0.1',
                        help='the host which database exist')
    parser.add_argument('--port',
                        type=int,
                        default=3306,
                        help='port to access mysql')
    # 运行数据保留天数，默认7天
    parser.add_argument('--days',
                        type=int,
                        default=7,
                        help='days want to keep')

    args = parser.parse_args()
    gRPC_mysql_client(args)