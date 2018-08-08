# --*-- coding:utf8 --*--
import os

# ---------------------------gRPC config section------------------------------------------
# gRPC connect host through this ip and port
HOST = os.getenv('HOST', '172.17.0.1')
# HOST = '127.0.0.1'
PORT = os.getenv('PORT', 50051)
# gRPC service can handle the numbers of concurrent
MAX_WORKERS = os.getenv('MAX_WORKERS', 15)

# ---------------------------datax config section------------------------------------------
# the path for log file
DATAX_LOG_ROOT = os.getenv('LOG_ROOT', '/var/log/airflow/datax')
# the path for datax conf script
DATAX_SCRIPT_PATH = os.getenv('DATAX_SCRIPT_PATH', '/home/jump-openstack/workplace/docker-airflow/datax_script')
# the docker image to start datax server
IMAGE = os.getenv('IMAGE', 'cloudin/datax:2.0')


# ---------------------------AOI config section------------------------------------------
# 日志文件存放路径
AOI_LOG_DIR = '/var/log/airflow/aoi'
FTP_SCRIPT_ABS_PATH = '/home/jump-openstack/workplace/docker-airflow/grpcHandle/tools/aoi_script/get_remote_data.py'
MAIN_SCRIPT_ABS_PATH = '/home/jump-openstack/workplace/docker-airflow/grpcHandle/tools/aoi_script/main_process.py'
# PART1 FTP下载配置参数
# the DIR for pva file download from FTP server
PVA_HOME_PATH = os.getenv('PVA_HOME_PATH', '/home/jump-openstack/ftp/pva')
# the DIR for psa file download from FTP server
PSA_HOME_PATH = os.getenv('PSA_HOME_PATH', '/home/jump-openstack/ftp/psa')
# just handle the file of last day
FTP_ONE_DAY = os.getenv('ONEDAY', True)
# specify the days want to handle, like ['2018/07/22','2018/07/22']
FTP_DAYS = os.getenv('DAYS', ['2018/07/25'])
# PART2 数据处理配置参数
MAIN_USER = os.getenv('MAIN_USER', 'root')
MAIN_PASSWORD = os.getenv('MAIN_PASSWORD', 'Rtsecret')
MAIN_HOST = os.getenv('MAIN_HOST', '10.232.70.203')
MIAN_PORT = os.getenv('MIAN_PORT', 300001)
MAIN_DB = os.getenv('MAIN_DB', 'aoi_process')
MIAN_ONE_DAY = os.getenv('MIAN_ONE_DAY', True)
MIAN_DAYS = os.getenv('MIAN_DAYS', [])
MAIN_HOME_DIR = os.getenv('MAIN_HOME_DIR', '/home/jump-openstack/yqj/ftp')

# ---------------------------mysqldump config section------------------------------------------
# 日志文件存放路径
MYSQLDUMP_LOG_DIR = os.getenv('MYSQLDUMP_LOG_DIR', '/var/log/airflow/mysqldump')
# 数据库备份脚本位置，注意是绝对路径，包括文件本身   ****
MYSQLDUMP_SCRIPT_ABS_PATH = '/home/jump-openstack/workplace/docker-airflow/grpcHandle/tools/mysqldump/mysql_dump.py'
#  备份文件存放位置
FILE_STROE_PATH = '/data/mysql-bak'
# 备份任务失败接受邮箱
RECEIVE_EMAIL = '18818216804@163.com'
