{{ config(materialized='view', schema='cobra_staging') }}
with source as (
    select cgc_cpf, lower(trim(email)) as email
    from cobra.tb_crm_cadastro
    where email is not null and trim(email) != '' and email like '%@%'
    union all
    select cgc_cpf, lower(trim(email2))
    from cobra.tb_crm_cadastro
    where email2 is not null and trim(email2) != '' and email2 like '%@%'
)
select
    case when e.cpf_cnpj is null then 'NOVO' else 'EXISTENTE' end as status,
    count(*) as qtd,
    current_timestamp as verificado_em
from source s
left join public.emails e
    on e.cpf_cnpj = s.cgc_cpf
    and e.email   = s.email
group by 1
