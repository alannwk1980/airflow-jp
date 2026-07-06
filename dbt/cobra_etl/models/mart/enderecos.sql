{{
    config(
        materialized='incremental',
        unique_key=['cpf_cnpj','cep','logradouro'],
        incremental_strategy='merge',
        merge_update_columns=['numero','complemento','bairro','cidade','uf','data_atualizacao'],
        schema='public'
    )
}}
select
    cgc_cpf                                         as cpf_cnpj,
    coalesce(nullif(trim(end_rua),''), 'NAO INFORMADO')      as logradouro,
    coalesce(nullif(trim(end_numero),''), 'S/N')             as numero,
    coalesce(nullif(trim(end_complemento),''), null)         as complemento,
    coalesce(nullif(trim(end_bairro),''), 'NAO INFORMADO')   as bairro,
    coalesce(nullif(trim(end_cidade),''), 'NAO INFORMADO')   as cidade,
    coalesce(nullif(trim(end_uf),''), 'NA')::bpchar(2)       as uf,
    coalesce(nullif(trim(end_cep),''), '00000000')           as cep,
    true                                            as correspondencia,
    false                                           as blacklist,
    dt_carga                                        as data_atualizacao
from {{ ref('stg_cadastro') }}
where end_rua is not null
  and trim(end_rua) != ''
  and end_cep is not null
  and trim(end_cep) != ''
