import os
import logging
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env_gazin'))

logger = logging.getLogger(__name__)

DDL_TABELA = """
CREATE TABLE IF NOT EXISTS public.dividas_consorcio (
    id                  SERIAL PRIMARY KEY,
    codigo_grupo        VARCHAR(50),
    codigo_cota         VARCHAR(50),
    numero_contrato     VARCHAR(100),
    vendedor            VARCHAR(200),
    cpf_vendedor        VARCHAR(20),
    codigo_equipe       VARCHAR(50),
    equipe_venda        VARCHAR(200),
    valor_credito       NUMERIC(15,2),
    valor_bem_entregue  NUMERIC(15,2),
    plano_cota          VARCHAR(50),
    prazo_grupo         INTEGER,
    primeira_assembleia DATE,
    ultima_assembleia   DATE,
    numero_parcela      INTEGER,
    data_vencimento     DATE,
    valor_parcela       NUMERIC(15,2),
    valor_juros         NUMERIC(15,2),
    valor_multa         NUMERIC(15,2),
    parcelas_atraso     INTEGER,
    codigo_situacao     VARCHAR(50),
    fase_processo       VARCHAR(100),
    tipo_contemplacao   VARCHAR(100),
    data_contemplacao   DATE,
    data_adesao         DATE,
    debito_automatico   VARCHAR(10),
    bloqueia_cobranca   VARCHAR(10),
    percentual_pago     NUMERIC(7,4),
    valor_quitacao      NUMERIC(15,2),
    codigo_filial_venda VARCHAR(50),
    nome_filial_venda   VARCHAR(200),
    ddd                 VARCHAR(5),
    numero_telefone     VARCHAR(20),
    dt_carga            TIMESTAMP DEFAULT NOW()
);
"""

COLUNAS = [
    'codigo_grupo', 'codigo_cota', 'numero_contrato', 'vendedor', 'cpf_vendedor',
    'codigo_equipe', 'equipe_venda', 'valor_credito', 'valor_bem_entregue',
    'plano_cota', 'prazo_grupo', 'primeira_assembleia', 'ultima_assembleia',
    'numero_parcela', 'data_vencimento', 'valor_parcela', 'valor_juros', 'valor_multa',
    'parcelas_atraso', 'codigo_situacao', 'fase_processo', 'tipo_contemplacao',
    'data_contemplacao', 'data_adesao', 'debito_automatico', 'bloqueia_cobranca',
    'percentual_pago', 'valor_quitacao', 'codigo_filial_venda', 'nome_filial_venda',
    'ddd', 'numero_telefone',
]


def _get_conn():
    return psycopg2.connect(
        host=os.environ['GAZIN_PG_HOST'],
        port=int(os.environ['GAZIN_PG_PORT']),
        dbname=os.environ['GAZIN_PG_DATABASE'],
        user=os.environ['GAZIN_PG_USER'],
        password=os.environ['GAZIN_PG_PASSWORD'],
        options='-c client_encoding=UTF8',
    )


def criar_tabela():
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL_TABELA)
        conn.commit()
    logger.info("Tabela dividas_consorcio verificada/criada.")


def carregar_dividas(registros: list[dict]):
    if not registros:
        logger.warning("Nenhum registro para carregar.")
        return

    valores = [tuple(r.get(col) for col in COLUNAS) for r in registros]
    insert_sql = f"""
        INSERT INTO public.dividas_consorcio ({', '.join(COLUNAS)})
        VALUES %s
    """

    with _get_conn() as conn:
        with conn.cursor() as cur:
            # Carga completa diária: limpa antes de inserir (dentro da mesma transação)
            cur.execute("TRUNCATE TABLE public.dividas_consorcio RESTART IDENTITY")
            execute_values(cur, insert_sql, valores, page_size=500)
        conn.commit()

    logger.info("Carregados %d registros em dividas_consorcio.", len(registros))
