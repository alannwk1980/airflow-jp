{{
    config(
        materialized='incremental',
        schema='cobra',
        alias='tb_audit_mudancas'
    )
}}
with dep_dividas as (
    select 1 from {{ ref('dividas') }} limit 1
)
select 'devedores'  as tabela, status, qtd, current_timestamp as data_carga from {{ ref('chg_devedores') }}
union all
select 'enderecos',  status, qtd, current_timestamp from {{ ref('chg_enderecos') }}
union all
select 'emails',     status, qtd, current_timestamp from {{ ref('chg_emails') }}
union all
select 'telefones',  status, qtd, current_timestamp from {{ ref('chg_telefones') }}
union all
select 'pagamentos', status, qtd, current_timestamp from {{ ref('chg_pagamentos') }}
union all
select 'lojas',      status, qtd, current_timestamp from {{ ref('chg_lojas') }}
union all
select 'dividas',    status, qtd, current_timestamp from cobra_staging.chg_dividas
union all
select 'processos',  'EXISTENTE', count(*), current_timestamp from public.processos
