
      -- back compat for old kwarg name
  
  
        
            
                
                
            
                
                
            
                
                
            
        
    

    

    merge into "gestor_magazine"."public"."pagamentos" as DBT_INTERNAL_DEST
        using "pagamentos__dbt_tmp031030623926" as DBT_INTERNAL_SOURCE
        on (
                    DBT_INTERNAL_SOURCE.cpf_cnpj = DBT_INTERNAL_DEST.cpf_cnpj
                ) and (
                    DBT_INTERNAL_SOURCE.contrato = DBT_INTERNAL_DEST.contrato
                ) and (
                    DBT_INTERNAL_SOURCE.num_parcela = DBT_INTERNAL_DEST.num_parcela
                )

    
    when matched then update set
        valor_pagamento = DBT_INTERNAL_SOURCE.valor_pagamento,data_pagamento = DBT_INTERNAL_SOURCE.data_pagamento,operacao = DBT_INTERNAL_SOURCE.operacao,filial = DBT_INTERNAL_SOURCE.filial,id_processo = DBT_INTERNAL_SOURCE.id_processo,id_pagamento = DBT_INTERNAL_SOURCE.id_pagamento,id_tipo_pagamento = DBT_INTERNAL_SOURCE.id_tipo_pagamento,linha_digitavel = DBT_INTERNAL_SOURCE.linha_digitavel,id_acordo = DBT_INTERNAL_SOURCE.id_acordo,contrato_original = DBT_INTERNAL_SOURCE.contrato_original,data_atualizacao = DBT_INTERNAL_SOURCE.data_atualizacao,data_carga = DBT_INTERNAL_SOURCE.data_carga
    

    when not matched then insert
        ("cpf_cnpj", "contrato", "num_parcela", "data_vencimento", "valor_pagamento", "valor_atualizado", "data_pagamento", "operacao", "data_carga", "contrato_original", "data_atualizacao", "filial", "id_processo", "id_pagamento", "id_tipo_pagamento", "linha_digitavel", "id_acordo")
    values
        ("cpf_cnpj", "contrato", "num_parcela", "data_vencimento", "valor_pagamento", "valor_atualizado", "data_pagamento", "operacao", "data_carga", "contrato_original", "data_atualizacao", "filial", "id_processo", "id_pagamento", "id_tipo_pagamento", "linha_digitavel", "id_acordo")


  