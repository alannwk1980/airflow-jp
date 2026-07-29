
      -- back compat for old kwarg name
  
  
        
            
	    
	    
            
        
    

    

    merge into "gestor_magazine"."public"."devedores" as DBT_INTERNAL_DEST
        using "devedores__dbt_tmp031029453920" as DBT_INTERNAL_SOURCE
        on ((DBT_INTERNAL_SOURCE.cpf_cnpj = DBT_INTERNAL_DEST.cpf_cnpj))

    
    when matched then update set
        nome_cliente = DBT_INTERNAL_SOURCE.nome_cliente,data_nasc = DBT_INTERNAL_SOURCE.data_nasc,sexo = DBT_INTERNAL_SOURCE.sexo,nome_conjuge = DBT_INTERNAL_SOURCE.nome_conjuge,nome_empresa = DBT_INTERNAL_SOURCE.nome_empresa,funcao_cargo = DBT_INTERNAL_SOURCE.funcao_cargo,renda_devedor = DBT_INTERNAL_SOURCE.renda_devedor,data_atualizacao = DBT_INTERNAL_SOURCE.data_atualizacao
    

    when not matched then insert
        ("cpf_cnpj", "nome_cliente", "data_nasc", "sexo", "nome_conjuge", "nome_empresa", "funcao_cargo", "renda_devedor", "data_atualizacao")
    values
        ("cpf_cnpj", "nome_cliente", "data_nasc", "sexo", "nome_conjuge", "nome_empresa", "funcao_cargo", "renda_devedor", "data_atualizacao")


  