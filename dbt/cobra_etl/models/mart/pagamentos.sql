{{
    config(
        materialized='incremental',
        unique_key=['cpf_cnpj','contrato','num_parcela'],
        incremental_strategy='merge',
        merge_update_columns=[
            'valor_pagamento','data_pagamento','operacao',
            'filial','id_processo','id_pagamento','id_tipo_pagamento',
            'linha_digitavel','id_acordo','contrato_original',
            'data_atualizacao','data_carga'
        ],
        schema='public'
    )
}}
select
    cgc_cpf                     as cpf_cnpj,
    contrato,
    nr_parcela                  as num_parcela,
    vencimento                  as data_vencimento,
    valor_pago                  as valor_pagamento,
    valor_parcela               as valor_atualizado,
    data_pagamento,
    tipo_baixa                  as operacao,
    contrato_original,
    data_atualizacao,
    filial,
    id_processo,
    id_pagamento,
    id_tipo_pagamento,
    linha_digitavel,
    id_acordo,
    dt_carga                    as data_carga
from {{ ref('stg_pagamentos') }}
