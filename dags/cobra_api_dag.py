# -*- coding: utf-8 -*-
import sys, os, pathlib
from datetime import datetime, date, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, os.path.dirname(__file__))
from utils.api_client import get_filiais, get_crm_cadastro, get_crm_dividas, get_crm_pagamentos, get_processos
from utils.persistencia import criar_schema, salvar_json_particionado, load_filiais, load_crm_cadastro, load_crm_dividas, load_crm_pagamentos, load_processos

default_args = {
    "owner": "etl-cobra",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=15),
    "email_on_failure": False,
}

def task_criar_schema():
    criar_schema()

def task_filiais(**ctx):
    data_ref = date.today().strftime("%Y-%m-%d")
    dados = get_filiais()
    salvar_json_particionado(dados, "filiais", data_ref)
    load_filiais(dados)

def task_processos(**ctx):
    data_ref = date.today().strftime("%Y-%m-%d")
    dados = get_processos()
    salvar_json_particionado(dados, "processos", data_ref)
    load_processos(dados)

def task_crm_cadastro(**ctx):
    data_ref = date.today().strftime("%Y-%m-%d")
    dados = get_crm_cadastro()
    salvar_json_particionado(dados, "crm_cadastro", data_ref)
    load_crm_cadastro(dados)

def task_crm_dividas(**ctx):
    data_ref = date.today().strftime("%Y-%m-%d")
    raw, rows = get_crm_dividas()                          # raw para S3, rows para banco
    salvar_json_particionado(raw, "crm_dividas", data_ref) # salva JSON bruto no S3
    load_crm_dividas(rows)                                 # carrega flatten no banco

def task_crm_pagamentos(**ctx):
    data_ref = date.today().strftime("%Y-%m-%d")
    dados = get_crm_pagamentos(dias_atras=90)
    salvar_json_particionado(dados, "crm_pagamentos", data_ref)
    load_crm_pagamentos(dados)

def task_sinalizar_dbt():
    pathlib.Path("/opt/airflow/dbt/.run_dbt").touch()
    print("Sinal criado — dbt sera executado no host em ate 30 segundos")

with DAG(
    dag_id="cobra_api_etl",
    description="ETL diario API Cobra Magazine do Povo para PostgreSQL",
    schedule="0 6 * * *",
    start_date=datetime(2026, 5, 1),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["cobra", "etl", "crm"],
) as dag:

    t_schema     = PythonOperator(task_id="criar_schema",          python_callable=task_criar_schema)
    t_filiais    = PythonOperator(task_id="extrair_filiais",        python_callable=task_filiais)
    t_processos  = PythonOperator(task_id="extrair_processos",      python_callable=task_processos)
    t_cadastro   = PythonOperator(task_id="extrair_crm_cadastro",   python_callable=task_crm_cadastro)
    t_dividas    = PythonOperator(task_id="extrair_crm_dividas",    python_callable=task_crm_dividas)
    t_pagamentos = PythonOperator(task_id="extrair_crm_pagamentos", python_callable=task_crm_pagamentos)
    t_dbt        = PythonOperator(task_id="sinalizar_dbt",          python_callable=task_sinalizar_dbt)

    t_schema >> [t_filiais, t_processos, t_cadastro, t_dividas, t_pagamentos] >> t_dbt
