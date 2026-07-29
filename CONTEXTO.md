# Projeto ETL Cobra — Magazine do Povo

## Servidor
- **Host:** root@172.63.120.124 (DBJPROCOB)
- **OS:** Ubuntu 24.04
- **Acesso:** SSH root

## Stack
- **Airflow:** Docker Compose · `/opt/airflow/`
- **dbt Core:** `/opt/dbt-env` (venv) · projeto em `/opt/airflow/dbt/cobra_etl`
- **dbt-watcher:** serviço systemd · lê flag `/opt/airflow/dbt/.run_dbt`
- **Banco:** PostgreSQL · `172.63.120.124:5432` · banco `gestor_magazine`
- **S3:** bucket `etl-jp-bronze-magazine` · região `us-east-1`

## Banco de Dados
- **Nome:** gestor_magazine
- **Credenciais:** em `dags/.env` (não versionado)

### Schemas e tabelas

**cobra.*** (fonte / raw)
- `tb_crm_cadastro`
- `tb_crm_dividas` — inclui `data_reneg`, `permite_renegociacao`
- `tb_crm_pagamentos` — inclui `contrato_original`, `filial`, `id_processo`, `id_pagamento`, `id_tipo_pagamento`, `linha_digitavel`, `id_acordo`, `data_atualizacao`
- `tb_filiais`
- `tb_processos` — inclui `permite_renegociacao`
- `tb_audit_mudancas`

**public.*** (destino / produção)
- `devedores`, `enderecos`, `emails`, `telefones`
- `dividas` / `dividas1` (snapshot para chg_dividas)
- `pagamentos` — inclui novos campos da API
- `lojas`
- `processos` — inclui `permite_renegociacao`

**cobra_staging.*** (views dbt)
- `stg_*` — cast e limpeza
- `chg_*` — comparação NOVO/EXISTENTE/REMOVIDO
- `audit_mudancas` — incremental

## dbt
- **20 models** passando
- Materialização: views (`cobra_staging`) + incremental (`public.*` e `cobra.tb_audit_mudancas`)
- `stg_pagamentos` tem deduplicação via `DISTINCT ON`
- `dividas.sql` tem pre_hook de snapshot em `dividas1`

## Pipeline Airflow
- **Schedule:** `0 6 * * *` (06:00 UTC = 03:00 Brasília)
- **Retry:** 3x com delay de 15 minutos
- **Containers:** webserver, scheduler, worker, triggerer, postgres, redis (todos healthy)
- **DAGs:**
  - `cobra_api_etl` — ETL principal API Cobra REST
  - `gazin_consorcio_etl` — ETL API SOAP Gazin Consórcio

## API Cobra
- **URL base:** https://api-cobra.magazinedopovo.com.br
- **Usuário:** jptecno · **ID Cobradora:** 900002
- Credenciais em `dags/.env`
- `get_crm_dividas()` retorna `(raw, rows)` — raw para S3, rows (flatten) para banco

## API Gazin (SOAP)
- **URL:** api-cobradoras.gazin.com.br/malta
- Parser XML customizado em `dags/utils/gazin_client.py`

## S3
- **Bucket:** `etl-jp-bronze-magazine` · prefixo `raw/`
- Salva JSON bruto (raw) antes do flatten
- Dados locais raw: `/opt/airflow/data/raw`

## Git / GitHub
- **Repositório:** https://github.com/alannwk1980/airflow-jp
- **Branch:** main
- **Servidor Linux:** `/opt/airflow` — SSH key configurada
- **Windows:** `C:\alann\airflow\airflow` — SSH key configurada
- **Claude Code:** instalado no Windows, aponta para `C:\alann\airflow\airflow`

### Fluxo Git
```bash
# Servidor Linux → GitHub:
cd /opt/airflow && git add -A && git commit -m "msg" && git push origin main

# Windows → puxar atualizações:
cd C:\alann\airflow\airflow && git pull origin main
```

## Integração Pentaho PDI
- **Servidor:** Windows Server 2012 R2 (sem SSH)
- **Script:** `check_dag_and_run_pentaho.bat`
- **Log:** `C:\DBA\magazine\agendamentos\log\dag_COBRA.txt`
- **Mecanismo:** polling API REST Airflow porta 8080 a cada 3min, máx 60 tentativas
- **Após sucesso DAG:** dispara `C:\DBA\magazine\agendamentos\distribuicao.bat`

## Pendências
1. **Timezone Airflow** — configurar `America/Sao_Paulo` no `docker-compose.yaml`
2. **Lógica REMOVIDO** — revisar/implementar nas views `chg_*`
3. **data1parc** — automatizar UPDATE em `public.dividas` via post_hook no dbt
4. **distribuicao/distribuicao1** — implementar mesmo padrão de snapshot que dividas/dividas1
5. **tipo_endereco na API** — validar campo na integração

## Histórico de decisões
- dbt-watcher via systemd para desacoplar execução dbt do Airflow
- S3 usado como camada bronze (raw files) — `get_crm_dividas()` salva raw antes do flatten
- `chg_*` views servem de base para `audit_mudancas`
- `stg_pagamentos` tem `DISTINCT ON` para deduplicar antes do merge
- `dividas.sql` usa pre_hook para snapshot em `dividas1` antes de recarregar
- Pentaho PDI mantido com polling HTTP em vez de SSH (Windows Server 2012 R2)
- Claude Code no Windows conectado ao repositório GitHub para edição direta
