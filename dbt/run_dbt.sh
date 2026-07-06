#!/bin/bash
source /opt/dbt-env/bin/activate
dbt run \
    --project-dir /opt/airflow/dbt/cobra_etl \
    --profiles-dir /root/.dbt

# Roda o audit separado para garantir que roda por último
dbt run \
    --select audit_mudancas \
    --project-dir /opt/airflow/dbt/cobra_etl \
    --profiles-dir /root/.dbt
