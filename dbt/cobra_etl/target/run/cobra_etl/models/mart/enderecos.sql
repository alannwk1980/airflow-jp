
      -- back compat for old kwarg name
  
  
        
            
                
                
            
                
                
            
                
                
            
        
    

    

    merge into "gestor_magazine"."public"."enderecos" as DBT_INTERNAL_DEST
        using "enderecos__dbt_tmp031029618973" as DBT_INTERNAL_SOURCE
        on (
                    DBT_INTERNAL_SOURCE.cpf_cnpj = DBT_INTERNAL_DEST.cpf_cnpj
                ) and (
                    DBT_INTERNAL_SOURCE.cep = DBT_INTERNAL_DEST.cep
                ) and (
                    DBT_INTERNAL_SOURCE.logradouro = DBT_INTERNAL_DEST.logradouro
                )

    
    when matched then update set
        numero = DBT_INTERNAL_SOURCE.numero,complemento = DBT_INTERNAL_SOURCE.complemento,bairro = DBT_INTERNAL_SOURCE.bairro,cidade = DBT_INTERNAL_SOURCE.cidade,uf = DBT_INTERNAL_SOURCE.uf,data_atualizacao = DBT_INTERNAL_SOURCE.data_atualizacao
    

    when not matched then insert
        ("cpf_cnpj", "logradouro", "numero", "complemento", "bairro", "cidade", "uf", "cep", "correspondencia", "blacklist", "data_atualizacao")
    values
        ("cpf_cnpj", "logradouro", "numero", "complemento", "bairro", "cidade", "uf", "cep", "correspondencia", "blacklist", "data_atualizacao")


  