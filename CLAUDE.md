# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Apache Airflow ETL pipeline for "Cobra Magazine do Povo" — a Brazilian debt collection agency. Orchestrates daily extraction from a REST API → PostgreSQL → dbt transformations → AWS S3 backup.

- **Airflow version**: 2.9.3 (CeleryExecutor with Redis broker)
- **Database**: PostgreSQL 13 (serves both as Airflow metadata DB and data warehouse)
- **Transformation**: dbt (`dbt/cobra_etl/`)

## Commands

### Start the Stack
```bash
docker-compose up -d
```

### Stop the Stack
```bash
docker-compose down
```

### Trigger the DAG manually
```bash
docker-compose exec airflow-webserver airflow dags trigger cobra_api_etl
```

### Access logs
- Airflow WebUI: http://localhost:8080 (default user/pass: `airflow`/`airflow`)
- Celery Flower: http://localhost:5555 (start with `--profile flower`)

### Run dbt manually (on host)
```bash
cd dbt/cobra_etl
dbt run --profiles-dir ~/.dbt
dbt test --profiles-dir ~/.dbt
```

### Start the dbt file-watcher daemon (on host)
```bash
bash dbt/watch_and_run.sh &
```

## Architecture

### Data Flow
```
Cobra REST API → Airflow DAG → PostgreSQL (schema: cobra) → dbt → public schema
                            ↘ S3 (raw JSON backup)
```

### Airflow DAG (`dags/cobra_api_dag.py`)
- **Schedule**: Daily at 06:00 UTC
- **Entry point**: `cobra_api_etl` DAG
- Task graph: `criar_schema` → 5 parallel `extrair_*` tasks → `sinalizar_dbt`
- `sinalizar_dbt` writes a signal file (`/opt/airflow/dbt/.run_dbt`) that the host-side `watch_and_run.sh` daemon picks up to trigger dbt

### Key modules
- `dags/utils/api_client.py` — REST client with token caching and automatic pagination
- `dags/utils/persistencia.py` — S3 backup (partitioned JSON) and PostgreSQL bulk loading

### dbt Layers (`dbt/cobra_etl/models/`)
- **`staging/`** → views in schema `cobra_staging` — type-cast and clean raw tables
  - `stg_*.sql`: standardized views
  - `chg_*.sql`: change-tracking views for audit
- **`mart/`** → incremental tables in schema `public` — production fact/dimension tables
  - `devedores` (upsert by `cpf_cnpj`), `dividas` (delete+insert with audit view), `pagamentos`, `processos`, `lojas`, `enderecos`, `telefones`, `emails`

### PostgreSQL schemas
| Schema | Contents |
|---|---|
| `cobra` | Raw tables loaded directly from API |
| `cobra_staging` | dbt staging views |
| `public` | dbt mart incremental tables (production) |

## Environment Variables

Both `.env` (root, Airflow) and `dags/.env` (DAG-level) are git-ignored. They contain:
- `API_URL`, `API_USUARIO`, `API_SENHA`, `API_IDCOBRADORA` — Cobra API credentials
- `PG_HOST`, `PG_PORT`, `PG_DATABASE`, `PG_USER`, `PG_PASSWORD` — PostgreSQL connection
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `S3_BUCKET`, `S3_PREFIX` — S3 backup

## dbt Signal Mechanism

dbt runs on the **host machine**, not inside Docker. The Airflow task `sinalizar_dbt` creates a trigger file at `/opt/airflow/dbt/.run_dbt`. The `watch_and_run.sh` daemon polls for this file and executes `run_dbt.sh` when detected. This is a deliberate design to avoid running dbt inside the container.
