#### 1. 项目结构
```
├── circle.yml
├── config
│   └── airflow.cfg
├── dags
│   ├── datax_command.py
│   ├── mysql_dump_dag.py
│   ├── pieces_defects_process_dag.py
│   └── shell_test_dag.py
├── datax_script
│   ├── MES-table
│   │   ├── aa.conf
│   │   ├── abc_test.conf
│   │   ├── ....
│   │   ├── mes_wpc_wo.conf
│   │   └── mes_wpc_wo_hist.conf
│   ├── MES-view
│   │   ├── absorbaxis1.conf
│   │   ├── ....
│   │   ├── yield_ro_or.conf
│   │   └── yuanfancheck.conf
│   ├── WMS-table
│   │   ├── a_accept_hist.conf
│   │   ├── ...
│   │   └── zz_mmslotinfoforwms.conf
│   └── WMS-view
│       ├── mes_fg_onhand_detail_view.conf
│       ├── ....
│       ├── ywms_receipt_detail.conf
│       └── zwms_temp_item.conf
├── docker-compose-CeleryExecutor.yml
├── docker-compose-LocalExecutor.yml
├── Dockerfile
├── grpcHandle
│   ├── core_function_pb2_grpc.py
│   ├── core_function_pb2_grpc.pyc
│   ├── core_function_pb2.py
│   ├── core_function_pb2.pyc
│   ├── core_function.proto
│   ├── grpcclient
│   │   ├── data_process_client.py
│   │   ├── datax_client.py
│   │   ├── __init__.py
│   │   └── mysqldump_client.py
│   ├── grpcserver.py
│   ├── __init__.py
│   ├── servicefunction
│   │   ├── datax_service_function.py
│   │   ├── datax_service_function.pyc
│   │   ├── __init__.py
│   │   ├── __init__.pyc
│   │   ├── mysqldump_service_function.py
│   │   ├── mysqldump_service_function.pyc
│   │   ├── pieces_defects_process_service_function.py
│   │   ├── pieces_defects_process_service_function.pyc
│   │   ├── utils.py
│   │   └── utils.pyc
│   ├── settings.py
│   ├── settings.pyc
│   └── tools
│       ├── aoi_script
│       │   ├── ftpdownloader.py
│       │   ├── get_remote_data.py
│       │   ├── __init__.py
│       │   └── main_process.py
│       ├── __init__.py
│       └── mysqldump
│           ├── __init__.py
│           └── mysql_dump.py
├── LICENSE
├── README.md
├── requirements.txt
└── script
    └── entrypoint.sh
```
#### 2. 项目说明
1. docker部署airflow，基于 https://github.com/puckel/docker-airflow，但需要根据自己项目依赖进行简单修改,如添加gRPC服务，挂载额外目录等。
2. 利用gRPC实现容器定时启动宿主机服务。airflow可以对DAG任务进行自定义调度，但定时任务部署在宿主机，需要从容器启动宿主机服务。因此采用gRPC服务框架实现简单远程过程调用。
3. 目前集成三类任务，包括数据库备份任务，datax异构数据迁移任务，AOI日常数据处理任务。可以自定义扩展。

##### 目录说明
1. dags.存放定时任务脚本，当需要添加定时任务时，根据相应格式写好放在该文件夹下就会被airflow 调度器自动识别和调度。注：通过文件共享实现，如下：
```
volumes:
    - ./dags:/usr/local/airflow/dags
    - ./grpcHandle:/usr/local/airflow/grpcHandle
    - ./datax_script:/usr/local/airflow/datax_script
```
DAG文件本质是通过不同参数调用client脚本，再间接调用宿主机服务。
如：
```
python /usr/local/airflow/grpcHandle/grpcclient/data_process_client.py ftp
```
2. data_script. 存放datax脚本文件，以数据库为文件夹，单个文件一般对应一个表的迁移配置。
3. grpcclient。client端脚本文件，通过执行相应client文件实现容器调用宿主机服务。
4. servicefiction。容器内调用对应client脚本，最终执行的是该文件夹下对应的函数。如调用 `data_process_client.py ftp`，调用的是pieces_defects_process_service_function.py文件下的如下函数：
```
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
```
最终通过shell执行另一个脚本文件。
5. tools. 存放server端最终要运行的脚本文件，如上执行的脚本文件就存放在该文件夹下。

#### 3. 配置文件说明
项目所有的配置在settings.py文件中设置。主要分为四个模块，
##### 1）gRPC相关配置
包括监听IP和端口，以及最大支持连接数。HOST地址需要额外注意，因为容器和服务器通信，采用的是默认bridge网络，地址为宿主机docker0地址。
```
# gRPC connect host through this ip and port
HOST = os.getenv('HOST', '172.17.0.1')
# HOST = '127.0.0.1'
PORT = os.getenv('PORT', 50051)
# gRPC service can handle the numbers of concurrent
MAX_WORKERS = os.getenv('MAX_WORKERS', 15)
```
##### 2）datax相关配置
包括日志文件存放目录，以及datax配置脚本位置，和datax启动镜像名称
```
DATAX_LOG_ROOT = os.getenv('LOG_ROOT', '/var/log/airflow/datax')
# the path for datax conf script
DATAX_SCRIPT_PATH = os.getenv('DATAX_SCRIPT_PATH', '/home/jump-openstack/workplace/docker-airflow/datax_script')
# the docker image to start datax server
IMAGE = os.getenv('IMAGE', 'cloudin/datax:2.0')
```
##### 3）AOI数据处理配置
AOI数据处理配置包括两个部分，一是FTP下载相关配置，二是对下载数据处理的主函数配置。两个任务有先后关系。
```
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

```
重点说明FTP_ONE_DAY和FTP_DAYS两个参数，当FTP_ONE_DAY为True，表示从生产服务器上下载前一天数据到本地，对应MIAN_ONE_DAY为True表示只处理前一天数据。FTP_DAYS则可以通过列表方式手动指定需要处理的日期，以['2018/07/25']格式，同理MIAN_DAYS。要使用FTP_DAYS和MIAN_DAYS一定要将FTP_ONE_DAY和MIAN_ONE_DAY设置为False。
##### 4.数据库备份配置
```
# 日志文件存放路径
MYSQLDUMP_LOG_DIR = os.getenv('MYSQLDUMP_LOG_DIR', '/var/log/airflow/mysqldump')
# 数据库备份脚本位置，注意是绝对路径，包括文件本身   ****
MYSQLDUMP_SCRIPT_ABS_PATH = '/home/jump-openstack/workplace/docker-airflow/grpcHandle/tools/mysqldump/mysql_dump.py'
#  备份文件存放位置
FILE_STROE_PATH = '/data/mysql-bak'
# 备份任务失败接受邮箱
RECEIVE_EMAIL = '18818216804@163.com'
```

#### 4. 部署步骤
##### 0. 镜像获取
airflow服务依赖cloudin/airflow-docker镜像，需要通过执行Dockerfile生成指定镜像。
##### 1. 启动airflow服务
```
docker-compose -f docker-compose-CeleryExecutor.yml up -d
```
##### 2. 启动gRPC server
进入文件目录：
```
python grpcserver.py   # 在宿主机执行
```
##### 3. 自定义dag文件
将需要调度的任务脚本放在目录dags下
##### 4. 额外的依赖库
容器内需要安装的依赖放在requirements.txt文件中，在启动时会自动安装。这种方式在国内环境比较慢，也可以重新定制镜像。
##### 5. settings.py配置
配置相应服务的参数。

#### 5. gRPC服务扩展
参考： https://www.jianshu.com/p/14e6f5217f40

gRPC可以很方便在服务端注册监听函数，客户端根据需求调用，并获得服务端返回的执行结果。使用gRPC服务分为以下几个步骤：
##### 1） 自定义服务端执行函数
放在servicefuction目录下，如定义最终执行函数
```
def exec_server_command(str1, str2):
    ...
    return 'success'
```
##### 2）定义proto文件
gRPC基于 ProtoBuf 序列化协议进行开发，需要对输入输出进行格式化定义,并定义服务：
如下：
```
message FileInfo {
    string filedir = 1;
    string filename = 2;
}

message Result {
    string res = 1;
}

service DataxCommandCall {
    rpc datax_command_call(FileInfo) returns (Result) {}
}
```
再执行 python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./core_function.proto #在 example 目录中执行编译，会生成：core_function_pb2.py 与 core_function_pb2_grpc.py。这两个文件是自动生成，无需进行修改。

##### 3）定义服务端执行文件
服务端执行文件主要完成自定义函数exec_server_command注册到服务DataxCommandCall中。
模版为：

```
import core_function_pb2
import core_function_pb2_grpc

from servicefunction import datax_service_function

# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))


# 注册datax启动函数服务
class DataxServicer(core_function_pb2_grpc.DataxCommandCallServicer):
    def datax_command_call(self, request, context):
        response = core_function_pb2.Result()
        response.res = datax_service_function.exec_server_command(request.filedir, request.filename)
        return response

core_function_pb2_grpc.add_DataxCommandCallServicer_to_server(
    DataxServicer(), server)
```
##### 4）client端执行文件
```
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
```

##### 补充
获取到远程批量生成的dag文件
```
wget -nH -m ftp://123.59.214.230:8821/dags/* --ftp-user=user --ftp-password=pass
```
文件会放在当前文件下dags文件中


