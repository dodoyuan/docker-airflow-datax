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

dag = DAG('aoi_data_download_and_process', default_args=default_args)

download_command = 'python {script_path}/data_process_client.py ftp'.format(script_path=gRPC_CLIENT_PATH)
main_process_command = 'python {script_path}/data_process_client.py main'.format(script_path=gRPC_CLIENT_PATH)

t1 = BashOperator(
    task_id='dowmload_task',
    bash_command=download_command,
    retries=3,
    dag=dag)
t2 = BashOperator(
    task_id='main_process_task',
    bash_command=main_process_command,
    retries=3,
    dag=dag)

t1 >> t2


