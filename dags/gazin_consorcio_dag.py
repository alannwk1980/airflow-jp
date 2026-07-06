from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from utils.gazin_client import buscar_dividas_consorcio
from utils.gazin_persistencia import criar_tabela, carregar_dividas

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=15),
    'email_on_failure': False,
}

with DAG(
    dag_id='gazin_consorcio_etl',
    description='Extrai dívidas de consórcio da API SOAP Gazin e carrega no PostgreSQL RDS',
    default_args=default_args,
    schedule_interval='0 7 * * *',  # 04:00 horário de Brasília (UTC-3)
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['gazin', 'consorcio', 'etl'],
) as dag:

    def task_criar_tabela():
        criar_tabela()

    def task_extrair_e_carregar():
        registros = buscar_dividas_consorcio()
        carregar_dividas(registros)

    criar_tabela_task = PythonOperator(
        task_id='criar_tabela',
        python_callable=task_criar_tabela,
    )

    extrair_carregar_task = PythonOperator(
        task_id='extrair_e_carregar',
        python_callable=task_extrair_e_carregar,
    )

    criar_tabela_task >> extrair_carregar_task
