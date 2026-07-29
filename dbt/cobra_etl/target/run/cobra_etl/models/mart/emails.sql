
      -- back compat for old kwarg name
  
  
        
            
                
                
            
                
                
            
        
    

    

    merge into "gestor_magazine"."public"."emails" as DBT_INTERNAL_DEST
        using "emails__dbt_tmp031029600522" as DBT_INTERNAL_SOURCE
        on (
                    DBT_INTERNAL_SOURCE.cpf_cnpj = DBT_INTERNAL_DEST.cpf_cnpj
                ) and (
                    DBT_INTERNAL_SOURCE.email = DBT_INTERNAL_DEST.email
                )

    
    when matched then update set
        prioritario = DBT_INTERNAL_SOURCE.prioritario,data_atualizacao = DBT_INTERNAL_SOURCE.data_atualizacao
    

    when not matched then insert
        ("cpf_cnpj", "email", "prioritario", "blacklist", "data_atualizacao")
    values
        ("cpf_cnpj", "email", "prioritario", "blacklist", "data_atualizacao")


  