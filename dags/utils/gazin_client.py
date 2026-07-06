import os
import logging
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env_gazin'))

logger = logging.getLogger(__name__)

SOAP_PAYLOAD = """<?xml version="1.0" encoding="utf-8"?>
<SOAP-ENV:Envelope
    SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
    xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:ns1="http://api-cobradoras.gazin.com.br/malta"
    xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body>
    <ns1:cargaConsultaDivida>
    </ns1:cargaConsultaDivida>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

NS = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'ns1':  'http://api-cobradoras.gazin.com.br/malta',
}


def _txt(el, tag):
    child = el.find(tag)
    return child.text.strip() if child is not None and child.text else None


def buscar_dividas_consorcio():
    url   = os.environ['GAZIN_API_URL']
    token = os.environ['GAZIN_API_TOKEN']

    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'Authorization': f'Bearer {token}',
    }

    logger.info("Chamando API SOAP Gazin: %s", url)
    response = requests.post(url, data=SOAP_PAYLOAD.encode('utf-8'), headers=headers, timeout=300)
    response.raise_for_status()

    logger.info("Status: %s | Tamanho: %d bytes", response.status_code, len(response.content))

    if not response.content or not response.text.strip():
        raise ValueError(f"API retornou resposta vazia. Headers: {dict(response.headers)}")

    root     = ET.fromstring(response.content)
    body     = root.find('soap:Body', NS)
    resp_el  = body.find('ns1:cargaConsultaDividaResponse', NS)
    return_el = resp_el.find('return')

    items = return_el.findall('item')
    logger.info("Total de clientes (items) recebidos: %d", len(items))

    registros = []
    for item in items:
        # Campos do cliente — repetidos em cada linha de cota
        cliente = {
            'cgc_cpf_cliente':    _txt(item, 'CGC_CPF_CLIENTE'),
            'nome':               _txt(item, 'NOME'),
            'data_nascimento':    _txt(item, 'DATANASCIMENTO'),
            'endereco_res':       _txt(item, 'CLIENT_ENDERECO'),
            'bairro_res':         _txt(item, 'CLIENT_BAIRRO'),
            'cidade_res':         _txt(item, 'CIDADE_NOME_RES'),
            'estado_res':         _txt(item, 'ESTADO_RES'),
            'cep':                _txt(item, 'CEP'),
            'endereco_com':       _txt(item, 'CLIENT_ENDERECO_COMERCIAL'),
            'bairro_com':         _txt(item, 'CLIENT_BAIRRO_COMERCIAL'),
            'cidade_com':         _txt(item, 'CIDADE_NOME_COM'),
            'estado_com':         _txt(item, 'ESTADO_COM'),
            'ddd_residencial':    _txt(item, 'CLIENT_DDD_RESIDENCIAL'),
            'fone_residencial':   _txt(item, 'FONE_FAX'),
            'ddd_comercial':      _txt(item, 'DDD_COMERCIAL'),
            'fone_comercial':     _txt(item, 'FONE_FAX_COMERCIAL'),
            'ddd_outro':          _txt(item, 'DDD_OUTRO'),
            'fone_outro':         _txt(item, 'FONE_FAX_OUTRO'),
            'ddd_celular':        _txt(item, 'DDD_CELULAR'),
            'celular':            _txt(item, 'CELULAR'),
            'fone_2':             _txt(item, 'FONE_FAX_2'),
            'email':              _txt(item, 'E_MAIL'),
            'cargo':              _txt(item, 'CARGO'),
            'salario':            _txt(item, 'SALARIO'),
            'classificacao':      _txt(item, 'CLASSIFICACAO'),
        }

        cotas_el = item.find('cotas')
        if cotas_el is None:
            continue

        cota_els = cotas_el.findall('cota')
        for cota in cota_els:
            registro = {
                **cliente,
                'codigo_grupo':        _txt(cota, 'CODIGO_GRUPO'),
                'codigo_cota':         _txt(cota, 'CODIGO_COTA'),
                'numero_contrato':     _txt(cota, 'NUMERO_CONTRATO'),
                'codigo_equipe':       _txt(cota, 'CODIGO_EQUIPE'),
                'vendedor':            _txt(cota, 'VENDEDOR'),
                'cpf_vendedor':        _txt(cota, 'CPF_VENDEDOR'),
                'filial':              _txt(cota, 'FILIAL'),
                'valor_credito':       _txt(cota, 'VALORCREDITO') or _txt(cota, 'VALOR_CREDITO'),
                'plano_cota':          _txt(cota, 'PLANO_COTA'),
                'primeira_assembleia': _txt(cota, 'PRIMEIRA_ASSEMBLEIA'),
                'prazo_grupo':         _txt(cota, 'PRAZO_GRUPO'),
                'valor_bem_entregue':  _txt(cota, 'VALOR_BEM_ENTREGUE'),
                'ultima_assembleia':   _txt(cota, 'ULTIMA_ASSEMBLEIA'),
                'numero_parcela':      _txt(cota, 'NUMERO_PARCELA'),
                'data_vencimento':     _txt(cota, 'DATA_VENCIMENTO'),
                'valor_parcela':       _txt(cota, 'VALOR_PARCELA'),
                'valor_juros':         _txt(cota, 'VALOR_JUROS'),
                'valor_multa':         _txt(cota, 'VALOR_MULTA'),
                'parcelas_atraso':     _txt(cota, 'PARCELAS_ATRASO'),
                'codigo_situacao':     _txt(cota, 'CODIGO_SITUACAO'),
                'fase_processo':       _txt(cota, 'FASE_PROCESSO'),
                'tipo_contemplacao':   _txt(cota, 'TIPO_CONTEMPLACAO'),
                'data_contemplacao':   _txt(cota, 'DATA_CONTEMPLACAO'),
                'data_adesao':         _txt(cota, 'DATA_ADESAO'),
                'debito_automatico':   _txt(cota, 'DEBITOAUTOMATICO'),
                'bloqueia_cobranca':   _txt(cota, 'BLOQUEIA_COBRANCA'),
                'percentual_pago':     _txt(cota, 'PERCENTUAL_PAGO'),
                'valor_quitacao':      _txt(cota, 'VALOR_QUITACAO'),
                'codigo_filial_venda': _txt(cota, 'CODIGO_FILIAL_VENDA'),
                'nome_filial_venda':   _txt(cota, 'NOME_FILIAL_VENDA'),
            }
            registros.append(registro)

    logger.info("Total de cotas extraídas: %d", len(registros))
    return registros
