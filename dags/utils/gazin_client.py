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


def _get_text(element, tag):
    """Retorna o texto de um subelemento ou None se ausente."""
    child = element.find(tag)
    return child.text.strip() if child is not None and child.text else None


def buscar_dividas_consorcio():
    """
    Chama a API SOAP da Gazin e retorna lista de dicts com os dados das cotas.
    O XML de resposta pode precisar de ajuste de tags conforme retorno real da API.
    """
    url = os.environ['GAZIN_API_URL']
    token = os.environ['GAZIN_API_TOKEN']

    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'Authorization': f'Bearer {token}',
        'SOAPAction': 'cargaConsultaDivida',
    }

    logger.info("Chamando API SOAP Gazin: %s", url)
    response = requests.post(
        url,
        data=SOAP_PAYLOAD.encode('utf-8'),
        headers=headers,
        timeout=120,
    )
    response.raise_for_status()

    logger.info("Resposta recebida. Status: %s | Tamanho: %d bytes", response.status_code, len(response.content))
    logger.info("XML bruto (primeiros 3000 chars):\n%s", response.text[:3000] if response.text else "(vazio)")

    if not response.content or not response.text.strip():
        raise ValueError(f"API retornou resposta vazia. Status: {response.status_code} | Headers: {dict(response.headers)}")

    root = ET.fromstring(response.content)

    # Loga a estrutura de tags do Body para facilitar diagnóstico na primeira execução
    body_raw = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body')
    if body_raw is not None:
        def _log_tree(el, depth=0):
            logger.info("%s<%s>", "  " * depth, el.tag.split('}')[-1])
            for child in list(el)[:5]:  # máx 5 filhos por nível para não poluir o log
                _log_tree(child, depth + 1)
        logger.info("--- Estrutura do Body SOAP (primeiros níveis) ---")
        _log_tree(body_raw)
        logger.info("--- Fim da estrutura ---")

    # Navega pelo envelope SOAP até os registros de cota
    # ATENÇÃO: ajustar os caminhos de tag conforme a resposta real da API
    ns = {
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'ns1': 'http://api-cobradoras.gazin.com.br/malta',
    }
    body = root.find('soap:Body', ns)
    response_el = body[0] if body is not None and len(body) > 0 else None

    # Tenta localizar os elementos de cota em caminhos comuns de resposta SOAP
    cotas = []
    if response_el is not None:
        # Tenta: <return><cotas><cota> ou <cotas><cota> direto
        for candidate in ['./cotas/cota', './return/cotas/cota', './cota', './return/cota']:
            cotas = response_el.findall(candidate)
            if cotas:
                logger.info("Encontradas %d cotas via path '%s'", len(cotas), candidate)
                break

    if not cotas:
        logger.warning("Nenhuma cota encontrada no XML. Verifique o path de tags da resposta.")
        return []

    registros = []
    for cota in cotas:
        registro = {
            'codigo_grupo':        _get_text(cota, 'CODIGO_GRUPO'),
            'codigo_cota':         _get_text(cota, 'CODIGO_COTA'),
            'numero_contrato':     _get_text(cota, 'NUMERO_CONTRATO'),
            'vendedor':            _get_text(cota, 'VENDEDOR'),
            'cpf_vendedor':        _get_text(cota, 'CPF_VENDEDOR'),
            'codigo_equipe':       _get_text(cota, 'CODIGO_EQUIPE'),
            'equipe_venda':        _get_text(cota, 'EQUIPEVENDA'),
            'valor_credito':       _get_text(cota, 'VALORCREDITO') or _get_text(cota, 'VALOR_CREDITO'),
            'valor_bem_entregue':  _get_text(cota, 'VALOR_BEM_ENTREGUE'),
            'plano_cota':          _get_text(cota, 'PLANO_COTA'),
            'prazo_grupo':         _get_text(cota, 'PRAZO_GRUPO'),
            'primeira_assembleia': _get_text(cota, 'PRIMEIRA_ASSEMBLEIA'),
            'ultima_assembleia':   _get_text(cota, 'ULTIMA_ASSEMBLEIA'),
            'numero_parcela':      _get_text(cota, 'NUMERO_PARCELA'),
            'data_vencimento':     _get_text(cota, 'DATA_VENCIMENTO'),
            'valor_parcela':       _get_text(cota, 'VALOR_PARCELA'),
            'valor_juros':         _get_text(cota, 'VALOR_JUROS'),
            'valor_multa':         _get_text(cota, 'VALOR_MULTA'),
            'parcelas_atraso':     _get_text(cota, 'PARCELAS_ATRASO'),
            'codigo_situacao':     _get_text(cota, 'CODIGO_SITUACAO'),
            'fase_processo':       _get_text(cota, 'FASE_PROCESSO'),
            'tipo_contemplacao':   _get_text(cota, 'TIPO_CONTEMPLACAO'),
            'data_contemplacao':   _get_text(cota, 'DATA_CONTEMPLACAO'),
            'data_adesao':         _get_text(cota, 'DATA_ADESAO'),
            'debito_automatico':   _get_text(cota, 'DEBITOAUTOMATICO'),
            'bloqueia_cobranca':   _get_text(cota, 'BLOQUEIA_COBRANCA'),
            'percentual_pago':     _get_text(cota, 'PERCENTUAL_PAGO'),
            'valor_quitacao':      _get_text(cota, 'VALOR_QUITACAO'),
            'codigo_filial_venda': _get_text(cota, 'CODIGO_FILIAL_VENDA'),
            'nome_filial_venda':   _get_text(cota, 'NOME_FILIAL_VENDA'),
            'ddd':                 _get_text(cota, 'DDD'),
            'numero_telefone':     _get_text(cota, 'NUMERO'),
        }
        registros.append(registro)

    logger.info("Total de registros extraídos: %d", len(registros))
    return registros
