# -*- coding: utf-8 -*-
import os, json, logging, requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
logger = logging.getLogger(__name__)

API_URL     = os.getenv("API_URL")
API_USUARIO = os.getenv("API_USUARIO")
API_SENHA   = os.getenv("API_SENHA")
API_IDCOBR  = int(os.getenv("API_IDCOBRADORA", "0"))
_token_cache = {"token": None, "expires_at": None}

def get_token():
    agora = datetime.utcnow()
    if _token_cache["token"] and _token_cache["expires_at"] > agora:
        return _token_cache["token"]
    resp = requests.post(f"{API_URL}/cobradoras/login",
        json={"usuario": API_USUARIO, "senha": API_SENHA, "idcobradora": API_IDCOBR}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise Exception(f"Erro login: {data['error']}")
    token = data["result"]["token"].replace("Bearer ", "")
    expires_in = data["result"].get("expires_in", 86400)
    _token_cache["token"] = token
    _token_cache["expires_at"] = agora + timedelta(seconds=expires_in - 300)
    return token

def _headers():
    return {"Authorization": f"Bearer {get_token()}", "Accept": "application/json"}

def get_filiais():
    resp = requests.get(f"{API_URL}/filiais", headers=_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()["result"]

def get_paginado(endpoint, limite=1000, extra_params=None):
    todos, pagina = [], 1
    params = {"limite": limite, **(extra_params or {})}
    while True:
        params["pagina"] = pagina
        logger.info(f"GET {endpoint} pagina {pagina}...")
        resp = requests.get(f"{API_URL}{endpoint}", headers=_headers(), params=params, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise Exception(f"Erro {endpoint}: {data['error']}")
        result = data["result"]
        itens = result.get("itens", result if isinstance(result, list) else [])
        todos.extend(itens)
        paginacao = result.get("paginacao", {})
        logger.info(f"Pagina {pagina}: {len(itens)} itens | acumulado: {len(todos)}")
        if not paginacao.get("tem_mais", False):
            break
        pagina += 1
    logger.info(f"{endpoint}: {len(todos)} registros no total.")
    return todos

def get_crm_cadastro():
    return get_paginado("/cobradoras/crm/cadastro", limite=1000)

def get_crm_dividas():
    """Retorna (raw, rows) — raw é o JSON bruto para S3, rows é o flatten para o banco."""
    raw = get_paginado("/cobradoras/crm/dividas", limite=1000)
    rows = []
    for cliente in raw:
        cgc_cpf = cliente.get("cgc_cpf")
        for contrato in cliente.get("contratos", []):
            nr_contrato         = contrato.get("contrato")
            tipo_contrato_cod   = contrato.get("tipo_contrato", {}).get("codigo")
            tipo_contrato_leg   = contrato.get("tipo_contrato", {}).get("legenda")
            idprocesso_contrato = contrato.get("idprocesso")
            idfilial            = contrato.get("idfilial")
            taxa_juros          = contrato.get("taxa_juros")
            data_venda          = contrato.get("data_venda")
            idvendedor          = contrato.get("idvendedor")
            idpedidovenda       = contrato.get("idpedidovenda")
            cliente_novo        = contrato.get("cliente_novo")
            renegociacao        = contrato.get("renegociacao")
            data_reneg          = contrato.get("data_reneg")
            permite_renegociacao = contrato.get("permite_renegociacao")
            titulos_reneg       = json.dumps(contrato.get("titulos_renegociacao", []), ensure_ascii=False)
            produtos            = json.dumps(contrato.get("produtos", []), ensure_ascii=False)
            for parcela in contrato.get("parcelas", []):
                rows.append({
                    "cgc_cpf":               cgc_cpf,
                    "contrato":              nr_contrato,
                    "nr_parcela":            str(parcela.get("nr_parcela", "")),
                    "tipo_contrato_cod":     tipo_contrato_cod,
                    "tipo_contrato_leg":     tipo_contrato_leg,
                    "idprocesso":            parcela.get("idprocesso") or idprocesso_contrato,
                    "idfilial":              idfilial,
                    "taxa_juros":            taxa_juros,
                    "data_venda":            data_venda,
                    "idvendedor":            idvendedor,
                    "idpedidovenda":         idpedidovenda,
                    "cliente_novo":          cliente_novo,
                    "renegociacao":          renegociacao,
                    "data_reneg":            data_reneg,
                    "permite_renegociacao":  permite_renegociacao,
                    "titulos_renegociacao":  titulos_reneg,
                    "produtos":              produtos,
                    "vencimento":            parcela.get("vencimento"),
                    "valor_parcela":         parcela.get("valor_parcela"),
                    "valor_atualizado":      parcela.get("valor_atualizado"),
                })
    logger.info(f"Dividas: {len(rows)} parcelas de {len(raw)} clientes.")
    return raw, rows

def get_crm_pagamentos(dias_atras=90):
    hoje = datetime.today()
    params = {
        "data_inicial": (hoje - timedelta(days=dias_atras)).strftime("%Y-%m-%d"),
        "data_final":   hoje.strftime("%Y-%m-%d"),
    }
    return get_paginado("/cobradoras/crm/pagamentos", limite=1000, extra_params=params)


def get_processos():
    """Retorna lista completa de processos."""
    resp = requests.get(f"{API_URL}/processos", headers=_headers(), timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise Exception(f"Erro processos: {data['error']}")
    logger.info(f"Processos: {len(data['result'])} registros.")
    return data["result"]
