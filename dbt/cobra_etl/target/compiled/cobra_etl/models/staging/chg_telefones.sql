
with source as (
    select cgc_cpf, trim(celular) as telefone, 2 as tipo
    from cobra.tb_crm_cadastro
    where celular is not null and trim(celular) != ''
    union all
    select cgc_cpf, trim(telefone_fixo), 1
    from cobra.tb_crm_cadastro
    where telefone_fixo is not null and trim(telefone_fixo) != ''
)
select
    case when t.cpf_cnpj is null then 'NOVO' else 'EXISTENTE' end as status,
    count(*) as qtd,
    current_timestamp as verificado_em
from source s
left join public.telefones t
    on  t.cpf_cnpj         = s.cgc_cpf
    and t.telefone         = s.telefone
    and t.id_tipo_telefone = s.tipo
group by 1