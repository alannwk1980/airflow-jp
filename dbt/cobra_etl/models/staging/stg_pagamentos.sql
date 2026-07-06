{{
    config(
        materialized='view',
        schema='cobra_staging'
    )
}}
with source as (
    select * from cobra.tb_crm_pagamentos
),
renamed as (
    select
        cgc_cpf,
        contrato,
        replace(nr_parcela, '.', '')    as nr_parcela,
        vencimento::date                as vencimento,
        valor_parcela::numeric          as valor_parcela,
        valor_pago::numeric             as valor_pago,
        data_pagamento::date            as data_pagamento,
        tipo_baixa,
        tipo_pagamento,
        saldo_residual::numeric         as saldo_residual,
        contrato_original,
        data_atualizacao::date          as data_atualizacao,
        filial::int                     as filial,
        id_processo::int                as id_processo,
        id_pagamento::int               as id_pagamento,
        id_tipo_pagamento::int          as id_tipo_pagamento,
        linha_digitavel,
        id_acordo::int                  as id_acordo,
        dt_carga
    from source
    where cgc_cpf is not null
      and contrato is not null
      and nr_parcela is not null
),
deduplicado as (
    select distinct on (cgc_cpf, contrato, nr_parcela)
        *
    from renamed
    order by cgc_cpf, contrato, nr_parcela, dt_carga desc
)
select * from deduplicado
