{{ config(materialized='view', schema='cobra_staging') }}
select
    case when l.cod_empresa is null then 'NOVO' else 'EXISTENTE' end as status,
    count(*) as qtd,
    current_timestamp as verificado_em
from cobra.tb_filiais s
left join public.lojas l
    on  l.cod_loja::varchar = s.cod_loja::varchar
    and l.cod_empresa::int  = s.cod_empresa::int
group by 1
