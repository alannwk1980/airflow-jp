
with dep_dividas as (
    select 1 from "gestor_magazine"."public"."dividas" limit 1
)
select 'devedores'  as tabela, status, qtd, current_timestamp as data_carga from "gestor_magazine"."cobra_staging"."chg_devedores"
union all
select 'enderecos',  status, qtd, current_timestamp from "gestor_magazine"."cobra_staging"."chg_enderecos"
union all
select 'emails',     status, qtd, current_timestamp from "gestor_magazine"."cobra_staging"."chg_emails"
union all
select 'telefones',  status, qtd, current_timestamp from "gestor_magazine"."cobra_staging"."chg_telefones"
union all
select 'pagamentos', status, qtd, current_timestamp from "gestor_magazine"."cobra_staging"."chg_pagamentos"
union all
select 'lojas',      status, qtd, current_timestamp from "gestor_magazine"."cobra_staging"."chg_lojas"
union all
select 'dividas',    status, qtd, current_timestamp from cobra_staging.chg_dividas
union all
select 'processos',  'EXISTENTE', count(*), current_timestamp from public.processos