# ETL Cobra — Magazine do Povo

Pipeline de dados diário que extrai informações da API Cobra, armazena no PostgreSQL e transforma via dbt.

## Arquitetura

```
API Cobra → Airflow DAG → PostgreSQL (cobra.*) → dbt → PostgreSQL (public.*) → S3 Bronze
```

## Stack

| Componente | Tecnologia | Localização |
|------------|-----------|-------------|
| Orquestração | Apache Airflow (Docker) | `/opt/airflow/` |
| Transformação | dbt Core | `/opt/airflow/dbt/cobra_etl/` |
| Banco de dados | PostgreSQL | `172.63.120.124:5432` |
| Storage | AWS S3 | `etl-jp-bronze-magazine` (us-east-1) |

## Estrutura do Repositório

```
airflow/
├── dags/
│   ├── cobra_api_dag.py          # DAG principal ETL Cobra
│   ├── gazin_consorcio_dag.py    # DAG ETL Consórcio Gazin (SOAP)
│   ├── .env                      # Credenciais (NÃO versionado)
│   └── utils/
│       ├── api_client.py         # Cliente API Cobra REST
│       ├── persistencia.py       # Carga no banco e S3
│       └── gazin_client.py       # Cliente API Gazin SOAP
├── dbt/
│   ├── cobra_etl/
│   │   └── models/
│   │       ├── staging/          # stg_* e chg_* (views)
│   │       └── mart/             # tabelas public.*
│   ├── run_dbt.sh                # Script manual dbt
│   └── watch_and_run.sh          # Watcher systemd
├── docker-compose.yaml           # Stack Airflow
├── profiles_template.yml         # Template conexão dbt (sem credenciais)
├── CLAUDE.md                     # Contexto para Claude Code
└── CONTEXTO.md                   # Contexto geral do projeto
```

## Configuração do Ambiente

### Pré-requisitos
- Docker + Docker Compose
- Python 3.12+
- dbt Core (`pip install dbt-postgres`)
- Acesso ao PostgreSQL `gestor_magazine`
- Credenciais AWS S3

### 1. Clonar o repositório
```bash
git clone git@github.com:alannwk1980/airflow-jp.git
cd airflow-jp
```

### 2. Configurar credenciais

Crie o arquivo `dags/.env` baseado no template:
```bash
cp dags/.env.template dags/.env
# edite com suas credenciais
```

Crie o `profiles.yml` do dbt:
```bash
mkdir -p ~/.dbt
cp profiles_template.yml ~/.dbt/profiles.yml
# edite com suas credenciais
```

### 3. Subir o Airflow
```bash
docker-compose up -d
```

Acesse: `http://localhost:8080` (admin/admin123)

### 4. Configurar dbt-watcher (systemd)
```bash
cp dbt/watch_and_run.sh /opt/airflow/dbt/
systemctl enable dbt-watcher
systemctl start dbt-watcher
```

## DAGs

### `cobra_api_etl`
- **Schedule:** `0 6 * * *` (03:00 Brasília)
- **Retry:** 3x com delay de 15 minutos
- **Fluxo:** `criar_schema → [filiais, processos, cadastro, dividas, pagamentos] → sinalizar_dbt`

### `gazin_consorcio_etl`
- **Schedule:** após `cobra_api_etl`
- **Fonte:** API SOAP `api-cobradoras.gazin.com.br/malta`

## dbt Models

### Staging (`cobra_staging.*`)
| Model | Tipo | Descrição |
|-------|------|-----------|
| `stg_cadastro` | view | Cadastro de devedores |
| `stg_dividas` | view | Dívidas e parcelas |
| `stg_pagamentos` | view | Pagamentos (deduplicado) |
| `stg_filiais` | view | Filiais/lojas |
| `stg_processos` | view | Processos de cobrança |
| `chg_*` | view | Comparação NOVO/EXISTENTE/REMOVIDO |
| `audit_mudancas` | incremental | Auditoria de mudanças |

### Mart (`public.*`)
| Model | Tipo | Chave |
|-------|------|-------|
| `devedores` | incremental/merge | `cpf_cnpj` |
| `dividas` | incremental | `cpf_cnpj+contrato+num_parcela` |
| `pagamentos` | incremental/merge | `cpf_cnpj+contrato+num_parcela` |
| `enderecos` | incremental/merge | `cpf_cnpj` |
| `emails` | incremental/merge | `cpf_cnpj` |
| `telefones` | incremental/merge | `cpf_cnpj` |
| `lojas` | incremental/merge | `cod_loja` |
| `processos` | incremental/merge | `id_processo` |

## Integração Pentaho PDI

Script `check_dag_and_run_pentaho.bat` no Windows Server monitora a DAG via API REST do Airflow e dispara o job Pentaho após sucesso.

- **Log:** `C:\DBA\magazine\agendamentos\log\dag_COBRA.txt`
- **API Airflow:** `http://172.63.120.124:8080/api/v1/dags/cobra_api_etl/dagRuns`

## Git — Fluxo de Trabalho

```bash
# No servidor Linux após mudanças:
cd /opt/airflow
git add -A
git commit -m "descricao"
git push origin main

# No Windows (Claude Code ou Git Bash):
git pull origin main
```

## Arquivos NÃO versionados (.gitignore)
- `dags/.env` — credenciais API e banco
- `.env` — variáveis Airflow
- `__pycache__/`, `*.pyc` — cache Python
- `logs/`, `data/` — gerados pelo Airflow
- `dbt/cobra_etl/target/` — compilados dbt
