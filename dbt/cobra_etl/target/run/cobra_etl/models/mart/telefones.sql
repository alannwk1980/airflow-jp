
      -- back compat for old kwarg name
  
  
        
            
                
                
            
                
                
            
                
                
            
        
    

    

    merge into "gestor_magazine"."public"."telefones" as DBT_INTERNAL_DEST
        using "telefones__dbt_tmp031030317500" as DBT_INTERNAL_SOURCE
        on (
                    DBT_INTERNAL_SOURCE.cpf_cnpj = DBT_INTERNAL_DEST.cpf_cnpj
                ) and (
                    DBT_INTERNAL_SOURCE.telefone = DBT_INTERNAL_DEST.telefone
                ) and (
                    DBT_INTERNAL_SOURCE.id_tipo_telefone = DBT_INTERNAL_DEST.id_tipo_telefone
                )

    
    when matched then update set
        whatsapp = DBT_INTERNAL_SOURCE.whatsapp,data_atualizacao = DBT_INTERNAL_SOURCE.data_atualizacao
    

    when not matched then insert
        ("cpf_cnpj", "id_tipo_telefone", "telefone", "whatsapp", "data_atualizacao", "blacklist", "ddd")
    values
        ("cpf_cnpj", "id_tipo_telefone", "telefone", "whatsapp", "data_atualizacao", "blacklist", "ddd")


  