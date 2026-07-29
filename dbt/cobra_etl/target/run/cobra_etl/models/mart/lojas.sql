
      -- back compat for old kwarg name
  
  
        
            
                
                
            
                
                
            
        
    

    

    merge into "gestor_magazine"."public"."lojas" as DBT_INTERNAL_DEST
        using "lojas__dbt_tmp031030556153" as DBT_INTERNAL_SOURCE
        on (
                    DBT_INTERNAL_SOURCE.cod_loja = DBT_INTERNAL_DEST.cod_loja
                ) and (
                    DBT_INTERNAL_SOURCE.cod_empresa = DBT_INTERNAL_DEST.cod_empresa
                )

    
    when matched then update set
        nome_loja = DBT_INTERNAL_SOURCE.nome_loja,nome_regional = DBT_INTERNAL_SOURCE.nome_regional,uf = DBT_INTERNAL_SOURCE.uf,cod_regional = DBT_INTERNAL_SOURCE.cod_regional,cod_empresagrupo = DBT_INTERNAL_SOURCE.cod_empresagrupo
    

    when not matched then insert
        ("nome_loja", "cod_regional", "nome_regional", "cod_empresa", "cod_loja", "uf", "cod_empresagrupo")
    values
        ("nome_loja", "cod_regional", "nome_regional", "cod_empresa", "cod_loja", "uf", "cod_empresagrupo")


  