import settings
import os
from servicefunction.utils import get_format_time, write_file
import subprocess

log_file_dir = settings.AOI_LOG_DIR


def exec_ftpdownloader_command():
    pva_home = settings.PVA_HOME_PATH
    psa_home = settings.PSA_HOME_PATH
    oneday = settings.FTP_ONE_DAY
    days = settings.FTP_DAYS

    ftp_script_abs_path = settings.FTP_SCRIPT_ABS_PATH
    format_time = get_format_time()
    # os.path.join()
    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir)
    file_name = format_time + '_ftp'
    cmd = 'python {script} --pva_home_path {pva} --psa_home_path {psa} --oneday {oneday} --days {days}'.\
          format(script=ftp_script_abs_path, pva=pva_home, psa=psa_home, oneday=oneday, days=days)
    write_file(log_file_dir, cmd, file_name)

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while p.poll() is None:
        out = p.stdout.readline()
        if out:
            write_file(log_file_dir, out, file_name)
    # print(p.returncode)
    if p.returncode == 0:
        return 'success'
    else:
        return 'failed'


def exec_dataprocess_command():
    main_script_abs_path = settings.MAIN_SCRIPT_ABS_PATH
    user = settings.MAIN_USER
    password = settings.MAIN_PASSWORD
    host = settings.MAIN_HOST
    port = settings.MIAN_PORT
    db = settings.MAIN_DB
    oneday = settings.MIAN_ONE_DAY
    days = settings.MIAN_DAYS
    homedir = settings.MAIN_HOME_DIR

    format_time = get_format_time()
    # filepath = os.path.join(LOG_ROOT, log_file_dir)
    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir)
    file_name = format_time + '_main.log'
    cmd = 'python {script} --user {user} --password {passwd} --host {host} --port {port} --mysqldb {db} --oneday ' \
          '{oneday} --days {days} --home_dir {homedir}'.format(script=main_script_abs_path, user=user, passwd=password,
                                                               host=host, port=port, db=db, oneday=oneday, days=days,
                                                               homedir=homedir)
    write_file(log_file_dir, cmd, file_name)

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while p.poll() is None:
        out = p.stdout.readline()
        if out:
            write_file(log_file_dir, out, file_name)
    # print(p.returncode)
    if p.returncode == 0:
        return 'success'
    else:
        return 'failed'

