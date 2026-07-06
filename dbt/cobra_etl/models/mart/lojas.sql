{{
    config(
        materialized='incremental',
        unique_key=['cod_loja','cod_empresa'],
        incremental_strategy='merge',
        merge_update_columns=['nome_loja','nome_regional','uf','cod_regional','cod_empresagrupo'],
        schema='public'
    )
}}
select
    nome_loja,
    cod_regional,
    nome_regional,
    cod_empresa,
    cod_loja::varchar           as cod_loja,
    uf,
    cod_empresagrupo::smallint  as cod_empresagrupo
from {{ ref('stg_filiais') }}
