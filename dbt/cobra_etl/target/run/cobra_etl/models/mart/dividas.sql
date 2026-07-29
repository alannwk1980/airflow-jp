
      
        delete from "gestor_magazine"."public"."dividas" as DBT_INTERNAL_DEST
        where (cpf_cnpj, contrato, num_parcela) in (
            select distinct cpf_cnpj, contrato, num_parcela
            from "dividas__dbt_tmp031029281342" as DBT_INTERNAL_SOURCE
        );

    

    insert into "gestor_magazine"."public"."dividas" ("cpf_cnpj", "contrato", "num_parcela", "id_processo", "cod_loja", "id_vendedor", "cliente_novo", "renegociacao", "data_venda", "data_vencimento", "valor_debito", "valor_atualizado", "taxa_juros", "cod_produtos", "data_atualizacao", "data1parc", "cod_empresa_gazin", "qtd_parcelas", "data_reneg", "permite_renegociacao")
    (
        select "cpf_cnpj", "contrato", "num_parcela", "id_processo", "cod_loja", "id_vendedor", "cliente_novo", "renegociacao", "data_venda", "data_vencimento", "valor_debito", "valor_atualizado", "taxa_juros", "cod_produtos", "data_atualizacao", "data1parc", "cod_empresa_gazin", "qtd_parcelas", "data_reneg", "permite_renegociacao"
        from "dividas__dbt_tmp031029281342"
    )
  