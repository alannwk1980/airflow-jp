#!/bin/bash
SIGNAL="/opt/airflow/dbt/.run_dbt"
LOG="/opt/airflow/dbt/dbt_run.log"

while true; do
    if [ -f "$SIGNAL" ]; then
        rm -f "$SIGNAL"
        echo "$(date) - Iniciando dbt run..." >> "$LOG"
        /opt/dbt-env/bin/dbt run \
            --project-dir /opt/airflow/dbt/cobra_etl \
            --profiles-dir /root/.dbt >> "$LOG" 2>&1
        echo "$(date) - dbt finalizado com código $?" >> "$LOG"
    fi
    sleep 30
done
