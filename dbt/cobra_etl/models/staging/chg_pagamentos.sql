{{ config(materialized='view', schema='cobra_staging') }}
select
    case when p.cpf_cnpj is null then 'NOVO' else 'EXISTENTE' end as status,
    count(*) as qtd,
    current_timestamp as verificado_em
from cobra.tb_crm_pagamentos s
left join public.pagamentos p
    on  p.cpf_cnpj    = s.cgc_cpf
    and p.contrato    = s.contrato
    and p.num_parcela = replace(s.nr_parcela, '.', '')
group by 1
