#### 0. 功能描述
1. docker部署airflow，基于 https://github.com/puckel/docker-airflow
2. 利用gRPC实现容器定时启动宿主机服务

#### 1. 项目结构
```
├── circle.yml
├── config
│   └── airflow.cfg
├── dags
│   ├── datax_command.py
│   └── shell_test_dag.py
├── datax_script
│   └── abc_test.json
├── docker-compose-CeleryExecutor.yml
├── docker-compose-LocalExecutor.yml
├── Dockerfile
├── grpcDatax
│   ├── core_function_pb2_grpc.py
│   ├── core_function_pb2_grpc.pyc
│   ├── core_function_pb2.py
│   ├── core_function_pb2.pyc
│   ├── core_function.proto
│   ├── core_function.py
│   ├── core_function.pyc
│   ├── ExecCommand.log
│   ├── grpcclient.py
│   └── grpcserver.py
├── LICENSE
├── README.md
├── requirements.txt
└── script
    └── entrypoint.sh
```

#### 用法
##### 1. 启动airflow服务
``` 
docker-compose -f docker-compose-CeleryExecutor.yml up -d
```
##### 2. 启动gRPC server
```
python grpcserver.py   # 在宿主机执行
```
##### 3. 自定义dag文件
将需要调度的任务脚本放在目录dags下
##### 4. 额外的依赖库
容器内需要安装的依赖放在requirements.txt文件中，在启动时会自动安装
##### 5. gRPC通信配置
获取docker0虚拟地址
```
# ifconfig
docker0   Link encap:Ethernet  HWaddr 02:42:66:72:66:47
          inet addr:172.17.0.1
```
根据inet addr修改grpcclient.py
```
# 本地测试是 localhost， 在docker上是 172.17.0.1
channel = grpc.insecure_channel('172.17.0.1:50051')
```
#### 常用命令
1) 删除所有容器 
```
docker ps|awk '{if (NR!=1) print $1}'| xargs docker stop
```
2) 删除所有的退出状态的容器
```
sudo docker rm $(sudo docker ps -a -q)
sudo docker rm $(sudo docker ps -qf status=exited)
```

#### 补充
1. gRPC注册函数为 grpc/core_function.py文件中exec_server_command函数，只有一个输入输出，并且都是string类型，输入输出类型不变，可以直接对函数进行重写。如果需要改变输入输出，需要重新编译，参考https://www.jianshu.com/p/14e6f5217f40
2. 容器采用host网络模式从而使连接地址为127.0.0.1:50051，理论上可行，但是会导致airflow服务出现问题，连接不上Postgres数据库。
