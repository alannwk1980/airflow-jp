# -*- coding: utf-8 -*-
import os, json, logging, boto3
from datetime import datetime
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
logger = logging.getLogger(__name__)

PG_HOST   = os.getenv("PG_HOST", "localhost")
PG_PORT   = os.getenv("PG_PORT", "5432")
PG_DB     = os.getenv("PG_DATABASE", "gestor_magazine")
PG_USER   = os.getenv("PG_USER", "postgres")
PG_PASS   = os.getenv("PG_PASSWORD", "")

S3_BUCKET = os.getenv("S3_BUCKET", "etl-jp-bronze-magazine")
S3_PREFIX = os.getenv("S3_PREFIX", "raw")
AWS_KEY   = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SEC   = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REG   = os.getenv("AWS_REGION", "us-east-1")


def get_s3():
    return boto3.client("s3",
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SEC,
        region_name=AWS_REG)


def salvar_json_particionado(dados, nome_entidade, data_ref=None):
    if data_ref is None:
        data_ref = datetime.today().strftime("%Y-%m-%d")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    conteudo = json.dumps({
        "extraido_em": datetime.now().isoformat(),
        "total": len(dados),
        "dados": dados
    }, ensure_ascii=False, indent=2)
    s3_key = f"{S3_PREFIX}/{nome_entidade}/{data_ref}/{nome_entidade}_{ts}.json"
    s3 = get_s3()
    s3.put_object(Bucket=S3_BUCKET, Key=s3_key,
                  Body=conteudo.encode("utf-8"), ContentType="application/json")
    s3_path = f"s3://{S3_BUCKET}/{s3_key}"
    logger.info(f"Salvo no S3: {s3_path} ({len(dados)} registros)")
    return s3_path


def get_engine():
    url = f"postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    return create_engine(url, pool_pre_ping=True)


def truncate_and_load(df, tabela, schema="cobra"):
    """Trunca e recarrega sem afetar views dependentes."""
    engine = get_engine()
    with engine.begin() as conn:
        # Verifica se a tabela existe
        existe = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = '{schema}'
                AND table_name = '{tabela}'
            )
        """)).scalar()
        if existe:
            conn.execute(text(f"TRUNCATE TABLE {schema}.{tabela}"))
            # Insere os dados
            for _, row in df.iterrows():
                pass  # usa pandas abaixo
    if existe:
        df.to_sql(tabela, engine, schema=schema, if_exists="append", index=False)
    else:
        df.to_sql(tabela, engine, schema=schema, if_exists="replace", index=False)
    logger.info(f"{schema}.{tabela}: {len(df)} registros carregados.")


def criar_schema():
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS cobra;"))
    logger.info("Schema cobra verificado.")


def load_filiais(dados):
    if not dados: return
    df = pd.DataFrame(dados)
    df["dt_carga"] = datetime.now()
    truncate_and_load(df, "tb_filiais")


def load_crm_cadastro(dados):
    if not dados: return
    rows = []
    for d in dados:
        end     = d.get("endereco") or {}
        con     = d.get("contatos") or {}
        emp     = d.get("emprego") or {}
        emp_end = emp.get("endereco") or {}
        conj    = d.get("conjuge") or {}
        refs    = d.get("referencias") or []
        ref1    = refs[0] if len(refs) > 0 else {}
        ref2    = refs[1] if len(refs) > 1 else {}
        rows.append({
            "cgc_cpf":            d.get("cgc_cpf"),
            "nome":               d.get("nome"),
            "estado_civil":       d.get("estado_civil"),
            "genero":             d.get("genero"),
            "data_nascimento":    d.get("data_nascimento"),
            "end_cep":            end.get("cep"),
            "end_rua":            end.get("rua"),
            "end_numero":         end.get("numero"),
            "end_complemento":    end.get("complemento"),
            "end_bairro":         end.get("bairro"),
            "end_cidade":         end.get("cidade"),
            "end_uf":             end.get("uf"),
            "email":              con.get("email"),
            "email2":             con.get("email2"),
            "telefone_fixo":      con.get("telefone_fixo"),
            "celular":            con.get("celular"),
            "whatsapp":           con.get("whatsapp"),
            "conjuge_nome":       conj.get("nome") if conj else None,
            "conjuge_cpf":        conj.get("cgc_cpf") if conj else None,
            "emp_empresa":        emp.get("empresa"),
            "emp_cargo":          emp.get("cargo"),
            "emp_salario":        emp.get("salario"),
            "emp_telefone":       emp.get("telefone"),
            "emp_end_logradouro": emp_end.get("logradouro"),
            "emp_end_numero":     emp_end.get("numero"),
            "emp_end_cep":        emp_end.get("cep"),
            "emp_end_bairro":     emp_end.get("bairro"),
            "emp_end_cidade":     emp_end.get("cidade"),
            "ref1_nome":          ref1.get("nome"),
            "ref1_grau":          ref1.get("grau"),
            "ref1_telefone":      ref1.get("telefone"),
            "ref2_nome":          ref2.get("nome"),
            "ref2_grau":          ref2.get("grau"),
            "ref2_telefone":      ref2.get("telefone"),
            "dt_carga":           datetime.now(),
        })
    truncate_and_load(pd.DataFrame(rows), "tb_crm_cadastro")


def load_crm_dividas(dados):
    if not dados: return
    df = pd.DataFrame(dados)
    df["dt_carga"] = datetime.now()
    truncate_and_load(df, "tb_crm_dividas")


def load_crm_pagamentos(dados):
    if not dados: return
    df = pd.DataFrame(dados)
    df["dt_carga"] = datetime.now()
    truncate_and_load(df, "tb_crm_pagamentos")


def load_processos(dados):
    if not dados: return
    df = pd.DataFrame(dados)
    df["dt_carga"] = datetime.now()
    truncate_and_load(df, "tb_processos")
    logger.info(f"tb_processos: {len(df)} registros.")
