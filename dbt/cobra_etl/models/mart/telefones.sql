{{
    config(
        materialized='incremental',
        unique_key=['cpf_cnpj','telefone','id_tipo_telefone'],
        incremental_strategy='merge',
        merge_update_columns=['whatsapp','data_atualizacao'],
        schema='public'
    )
}}
with celulares as (
    select
        cgc_cpf                             as cpf_cnpj,
        2                                   as id_tipo_telefone,
        trim(celular)                       as telefone,
        coalesce(whatsapp, false)           as whatsapp,
        null::boolean                       as blacklist,
        null::integer                       as ddd,
        dt_carga                            as data_atualizacao
    from {{ ref('stg_cadastro') }}
    where celular is not null
      and trim(celular) != ''
),
fixos as (
    select
        cgc_cpf                             as cpf_cnpj,
        1                                   as id_tipo_telefone,
        trim(telefone_fixo)                 as telefone,
        false                               as whatsapp,
        null::boolean                       as blacklist,
        null::integer                       as ddd,
        dt_carga                            as data_atualizacao
    from {{ ref('stg_cadastro') }}
    where telefone_fixo is not null
      and trim(telefone_fixo) != ''
)
select * from celulares
union all
select * from fixos
