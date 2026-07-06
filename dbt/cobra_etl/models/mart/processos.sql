{{
    config(
        materialized='incremental',
        unique_key='id_processo',
        incremental_strategy='merge',
        merge_update_columns=['descricao','nome_processo','status','permite_renegociacao'],
        schema='public'
    )
}}
select
    descricao,
    idsituacaoprocesso          as status,
    idprocesso::int             as id_processo,
    nome_processo,
    permite_renegociacao
from {{ ref('stg_processos') }}
