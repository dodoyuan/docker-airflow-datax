#! -*- coding:utf-8 -*-

import subprocess
import os

import settings
from servicefunction.utils import get_format_time, write_file

datax_log_root = settings.DATAX_LOG_ROOT
datax_script_path = settings.DATAX_SCRIPT_PATH
image = settings.IMAGE


def exec_server_command(filedir, filename):
    cmd = 'sudo docker run --rm -it --net host -v ' \
          '{datax_script_path}/{filedir}/:/conf ' \
          '{image} /opt/datax/bin/datax.py /conf/{filename}'\
        .format(datax_script_path=datax_script_path, filedir=filedir,
                image=image, filename=filename)
    dirname = get_format_time()
    filepath = os.path.join(datax_log_root, filedir, dirname)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    file_name = filename.split('.')[0]
    write_file(filepath, cmd, file_name)
    # 程序运行后才会输出
    # try:
    #     output = subprocess.check_output(cmd, shell=True)
    #     write_file(filepath, output, file_name)
    # except Exception:
    #     return traceback.print_exc()
    # return 'success'
    # 获取实时输出
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while p.poll() is None:
        out = p.stdout.readline()
        if out:
            write_file(filepath, out, file_name)
    print(p.returncode)
    if p.returncode == 0:
        return 'success'
    else:
        return 'failed'
