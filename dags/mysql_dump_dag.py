from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

gRPC_CLIENT_PATH = '/usr/local/airflow/grpcHandle/grpcclient'

default_args = {
    'owner': 'CloudIn',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'email': ['dingguoqiang@cloudin.cn'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('mysqldump', default_args=default_args)

database_info = [
    # {'database': 'offline', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 33333, 'days': 7},
    # {'database': 'schema_db', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 33333, 'days': 7},
    # {'database': 'mes', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 34444, 'days': 7},
    # {'database': 'wms', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 35555, 'days': 7},
    # {'database': 'erp', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 36666, 'days': 7},
    # {'database': 'demo', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 37777, 'days': 7},
    # {'database': 'aoi', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 30001, 'days': 3},
    # {'database': 'aoi_process', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 30001, 'days': 7},
    {'database': 'material', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 30002, 'days': 7},
    # {'database': 'aspen_cockpit', 'user': 'root', 'password': 'Rtsecret', 'host': '123.59.214.229', 'port': 30003, 'days': 7},
]
# material_dump = 'python mysqldump_client.py --database material --user root ' \
#                   '--password Rtsecret --host 123.59.214.229 --port 30002 --days 7'


t2 = BashOperator(
    task_id='sleep',
    bash_command='sleep 3',
    retries=3,
    dag=dag)

for i, database in enumerate(database_info):
    command = 'python {script_path}/mysqldump_client.py --database {db} --user {user} ' \
                  '--password {pd} --host {host} --port {port} --days {days}'.format(db=database['database'],
                                                                                     user=database['user'],
                                                                                     pd=database['password'],
                                                                                     host=database['host'],
                                                                                     port=database['port'],
                                                                                     days=database['days'],
                                                                                     script_path=gRPC_CLIENT_PATH
                                                                                     )
    task = BashOperator(
        task_id='{db}_dump'.format(db=database['database']),
        bash_command=command,
        dag=dag)
    # todo:  task's relationship

