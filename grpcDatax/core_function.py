#! -*- coding:utf-8 -*-

import subprocess
import traceback
import os
import time

LOG_ROOT = '/var/log/datax'


def get_filename():
    '''
    以当前时间为文件名，格式是: 年-月-日.sql
    同时返回具体时间以及七天前文件的文件名
    :return:
    '''
    now = time.time()
    tl = time.localtime(now)
    filename = time.strftime("%Y-%m-%d", tl)
    return filename


def write_file(filepath, content):
    path = os.path.join(filepath, 'output.log')
    with open(path, 'a+') as f:
        f.write(content)
        f.write('\n')


def exec_server_command(jsonfile):
    cmd = 'sudo docker run --rm -it --net host -v ' \
          '/home/jump-openstack/workplace/docker-airflow/datax_script:/conf ' \
          'cloudin/datax:2.0 /opt/datax/bin/datax.py /conf/{jsfile}'.format(jsfile=jsonfile)
    filename = get_filename()
    filepath = os.path.join(LOG_ROOT, filename)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    write_file(filepath, cmd)
    try:
        output = subprocess.check_output(cmd, shell=True)
        write_file(filepath, output)
    except Exception:
        return traceback.print_exc()
    return 'success'

