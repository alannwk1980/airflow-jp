
      insert into "gestor_magazine"."cobra"."tb_audit_mudancas" ("qtd", "data_carga", "tabela", "status")
    (
        select "qtd", "data_carga", "tabela", "status"
        from "tb_audit_mudancas__dbt_tmp031034657100"
    )


  