# -*- coding:utf-8 -*-
import grpc
import sys
import os
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


def data_process(args):
    '''
    AOI数据处理，根据type调用不同的功能
    :param type:
    :return:
    '''
    type = args.type
    host = settings.HOST
    port = str(settings.PORT)
    # open a gRPC channel
    url = host + ':' + port
    channel = grpc.insecure_channel(url)

    # create a stub (client)
    stub = core_function_pb2_grpc.PiecesDefectsProcessStub(channel)

    # create a valid request message
    none_info = core_function_pb2.Nonetype()

    # make the call
    if type == 'ftp':
        response = stub.pieces_defects_ftp_downloader(none_info)
        print(response.res)
        assert response.res == 'success'
    elif type == 'main':
        response = stub.pieces_defects_main_process(none_info)
        print(response.res)
        assert response.res == 'success'


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--type',
                        type=str,
                        default='ftp',
                        help='exec ftpdownload or main process')
    args = parser.parse_args()
    data_process(args)