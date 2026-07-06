{{
    config(
        materialized='view',
        schema='cobra_staging'
    )
}}
with source as (
    select * from cobra.tb_crm_dividas
),
renamed as (
    select
        cgc_cpf,
        contrato::varchar               as contrato,
        replace(nr_parcela, '.', '')::int as nr_parcela,
        tipo_contrato_cod::int          as tipo_contrato_cod,
        tipo_contrato_leg,
        idprocesso::int                 as idprocesso,
        idfilial::int                   as idfilial,
        taxa_juros::numeric             as taxa_juros,
        data_venda::date                as data_venda,
        idvendedor::int                 as idvendedor,
        idpedidovenda::int              as idpedidovenda,
        cliente_novo::boolean           as cliente_novo,
        renegociacao::boolean           as renegociacao,
        data_reneg::date                as data_reneg,
        permite_renegociacao::boolean   as permite_renegociacao,
        titulos_renegociacao,
        produtos,
        vencimento::date                as vencimento,
        valor_parcela::numeric          as valor_parcela,
        valor_atualizado::numeric       as valor_atualizado,
        dt_carga
    from source
    where cgc_cpf is not null
      and contrato is not null
      and nr_parcela is not null
)
select * from renamed
