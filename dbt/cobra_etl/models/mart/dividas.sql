{{
    config(
        materialized='incremental',
        unique_key=['cpf_cnpj','contrato','num_parcela'],
        incremental_strategy='delete+insert',
        schema='public',
        pre_hook=[
            "TRUNCATE TABLE public.dividas1",
            "INSERT INTO public.dividas1 SELECT * FROM public.dividas",
            "DELETE FROM public.dividas"
        ],
        post_hook=[
            """
            CREATE OR REPLACE VIEW cobra_staging.chg_dividas AS
            with novos as (
                select 'NOVO' as status, count(*) as qtd
                from public.dividas d
                where not exists (
                    select 1 from public.dividas1 d1
                    where d1.cpf_cnpj = d.cpf_cnpj
                      and d1.contrato = d.contrato
                      and d1.num_parcela = d.num_parcela
                )
            ),
            removidos as (
                select 'REMOVIDO' as status, count(*) as qtd
                from public.dividas1 d1
                where not exists (
                    select 1 from public.dividas d
                    where d.cpf_cnpj = d1.cpf_cnpj
                      and d.contrato = d1.contrato
                      and d.num_parcela = d1.num_parcela
                )
            ),
            existentes as (
                select 'EXISTENTE' as status, count(*) as qtd
                from public.dividas d
                inner join public.dividas1 d1
                    on d1.cpf_cnpj = d.cpf_cnpj
                    and d1.contrato = d.contrato
                    and d1.num_parcela = d.num_parcela
            )
            select status, qtd, current_timestamp as verificado_em
            from novos union all
            select status, qtd, current_timestamp from removidos union all
            select status, qtd, current_timestamp from existentes
            """
        ]
    )
}}
select
    cgc_cpf                         as cpf_cnpj,
    contrato,
    nr_parcela                      as num_parcela,
    idprocesso                      as id_processo,
    idfilial::varchar               as cod_loja,
    idvendedor::varchar             as id_vendedor,
    cliente_novo,
    renegociacao,
    data_reneg,
    permite_renegociacao,
    data_venda,
    vencimento                      as data_vencimento,
    valor_parcela                   as valor_debito,
    valor_atualizado,
    taxa_juros,
    produtos                        as cod_produtos,
    dt_carga                        as data_atualizacao,
    null::date                      as data1parc,
    null::int                       as cod_empresa_gazin,
    null::int                       as qtd_parcelas
from {{ ref('stg_dividas') }}
