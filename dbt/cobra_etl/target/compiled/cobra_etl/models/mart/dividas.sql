
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
from "gestor_magazine"."cobra_staging"."stg_dividas"