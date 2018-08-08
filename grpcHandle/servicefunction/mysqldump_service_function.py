# -*- coding:utf-8 -*-
import settings
import os
from servicefunction.utils import get_format_time, write_file
import subprocess

log_file_dir = settings.MYSQLDUMP_LOG_DIR
mysqldump_script_abs_path = settings.MYSQLDUMP_SCRIPT_ABS_PATH


def exec_server_command(database, user, password, host, port, days):
    format_time = get_format_time()
    file_path = os.path.join(log_file_dir, format_time)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_name = database
    cmd = 'python {script} --database {database}  --user {user} ' \
          '--password {passwd} ' \
          '--host {host} --port {port} --days {days}'.format(script=mysqldump_script_abs_path, database=database,
                                                             user=user, passwd=password, host=host,
                                                             port=port, days=days)
    write_file(file_path, cmd, file_name)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while p.poll() is None:
        out = p.stdout.readline()
        if out:
            write_file(file_path, out, file_name)
    # print(p.returncode)  TODO:任务失败可见
    if p.returncode == 0:
        return 'success'
    else:
        return 'failed'
