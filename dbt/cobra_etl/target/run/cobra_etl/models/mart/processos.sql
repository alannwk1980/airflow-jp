
      -- back compat for old kwarg name
  
  
        
            
	    
	    
            
        
    

    

    merge into "gestor_magazine"."public"."processos" as DBT_INTERNAL_DEST
        using "processos__dbt_tmp031030775163" as DBT_INTERNAL_SOURCE
        on ((DBT_INTERNAL_SOURCE.id_processo = DBT_INTERNAL_DEST.id_processo))

    
    when matched then update set
        descricao = DBT_INTERNAL_SOURCE.descricao,nome_processo = DBT_INTERNAL_SOURCE.nome_processo,status = DBT_INTERNAL_SOURCE.status,permite_renegociacao = DBT_INTERNAL_SOURCE.permite_renegociacao
    

    when not matched then insert
        ("status", "id_processo", "descricao", "nome_processo", "permite_renegociacao")
    values
        ("status", "id_processo", "descricao", "nome_processo", "permite_renegociacao")


  