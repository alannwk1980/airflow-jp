{{ config(materialized='view', schema='cobra_staging') }}
select
    case when d.cpf_cnpj is null then 'NOVO' else 'EXISTENTE' end as status,
    count(*) as qtd,
    current_timestamp as verificado_em
from cobra.tb_crm_cadastro s
left join public.devedores d on d.cpf_cnpj = s.cgc_cpf
group by 1
