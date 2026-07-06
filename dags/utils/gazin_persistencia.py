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
    -- Cliente
    cgc_cpf_cliente     VARCHAR(20),
    nome                VARCHAR(200),
    data_nascimento     VARCHAR(20),
    endereco_res        VARCHAR(300),
    bairro_res          VARCHAR(100),
    cidade_res          VARCHAR(100),
    estado_res          VARCHAR(5),
    cep                 VARCHAR(10),
    endereco_com        VARCHAR(300),
    bairro_com          VARCHAR(100),
    cidade_com          VARCHAR(100),
    estado_com          VARCHAR(5),
    ddd_residencial     VARCHAR(5),
    fone_residencial    VARCHAR(20),
    ddd_comercial       VARCHAR(5),
    fone_comercial      VARCHAR(20),
    ddd_outro           VARCHAR(5),
    fone_outro          VARCHAR(20),
    ddd_celular         VARCHAR(5),
    celular             VARCHAR(20),
    fone_2              VARCHAR(20),
    email               VARCHAR(200),
    cargo               VARCHAR(100),
    salario             NUMERIC(15,2),
    classificacao       VARCHAR(50),
    -- Cota
    codigo_grupo        VARCHAR(20),
    codigo_cota         VARCHAR(20),
    numero_contrato     VARCHAR(20),
    codigo_equipe       VARCHAR(20),
    vendedor            VARCHAR(200),
    cpf_vendedor        VARCHAR(20),
    filial              VARCHAR(20),
    valor_credito       NUMERIC(15,2),
    plano_cota          VARCHAR(20),
    primeira_assembleia VARCHAR(20),
    prazo_grupo         VARCHAR(20),
    valor_bem_entregue  NUMERIC(15,2),
    ultima_assembleia   VARCHAR(20),
    numero_parcela      VARCHAR(20),
    data_vencimento     VARCHAR(20),
    valor_parcela       NUMERIC(15,2),
    valor_juros         NUMERIC(15,2),
    valor_multa         NUMERIC(15,2),
    parcelas_atraso     VARCHAR(20),
    codigo_situacao     VARCHAR(50),
    fase_processo       VARCHAR(100),
    tipo_contemplacao   VARCHAR(100),
    data_contemplacao   VARCHAR(20),
    data_adesao         VARCHAR(20),
    debito_automatico   VARCHAR(10),
    bloqueia_cobranca   VARCHAR(10),
    percentual_pago     NUMERIC(7,4),
    valor_quitacao      NUMERIC(15,2),
    codigo_filial_venda VARCHAR(50),
    nome_filial_venda   VARCHAR(200),
    dt_carga            TIMESTAMP DEFAULT NOW()
);
"""

COLUNAS = [
    'cgc_cpf_cliente', 'nome', 'data_nascimento',
    'endereco_res', 'bairro_res', 'cidade_res', 'estado_res', 'cep',
    'endereco_com', 'bairro_com', 'cidade_com', 'estado_com',
    'ddd_residencial', 'fone_residencial', 'ddd_comercial', 'fone_comercial',
    'ddd_outro', 'fone_outro', 'ddd_celular', 'celular', 'fone_2',
    'email', 'cargo', 'salario', 'classificacao',
    'codigo_grupo', 'codigo_cota', 'numero_contrato', 'codigo_equipe',
    'vendedor', 'cpf_vendedor', 'filial', 'valor_credito', 'plano_cota',
    'primeira_assembleia', 'prazo_grupo', 'valor_bem_entregue', 'ultima_assembleia',
    'numero_parcela', 'data_vencimento', 'valor_parcela', 'valor_juros', 'valor_multa',
    'parcelas_atraso', 'codigo_situacao', 'fase_processo', 'tipo_contemplacao',
    'data_contemplacao', 'data_adesao', 'debito_automatico', 'bloqueia_cobranca',
    'percentual_pago', 'valor_quitacao', 'codigo_filial_venda', 'nome_filial_venda',
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
            cur.execute("TRUNCATE TABLE public.dividas_consorcio RESTART IDENTITY")
            execute_values(cur, insert_sql, valores, page_size=500)
        conn.commit()

    logger.info("Carregados %d registros em dividas_consorcio.", len(registros))
