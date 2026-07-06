{{ config(materialized='view', schema='cobra_staging') }}
select
    case when e.cpf_cnpj is null then 'NOVO' else 'EXISTENTE' end as status,
    count(*) as qtd,
    current_timestamp as verificado_em
from cobra.tb_crm_cadastro s
left join public.enderecos e
    on  e.cpf_cnpj   = s.cgc_cpf
    and e.cep        = coalesce(nullif(trim(s.end_cep),''), '00000000')
    and e.logradouro = coalesce(nullif(trim(s.end_rua),''), 'NAO INFORMADO')
where s.end_rua is not null and trim(s.end_rua) != ''
  and s.end_cep is not null and trim(s.end_cep) != ''
group by 1
