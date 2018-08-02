from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'CloudIn',
    'depends_on_past': False,
    'start_date': datetime(2018, 7, 31),
    'email': ['18818216804@163.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('datax_command', default_args=default_args)

command_example = 'python /usr/local/airflow/grpcDatax/grpcclient.py abc_test.json'
t1 = BashOperator(
    task_id='print',
    bash_command=command_example,
    dag=dag)

t2 = BashOperator(
    task_id='sleep',
    bash_command='sleep 3',
    retries=3,
    dag=dag)

t2.set_upstream(t1)

