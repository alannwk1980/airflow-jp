
  create view "gestor_magazine"."cobra_staging"."stg_processos__dbt_tmp"
    
    
  as (
    
select
    idprocesso::int             as idprocesso,
    descricao,
    nome_processo,
    idsituacaoprocesso::int     as idsituacaoprocesso,
    segmento,
    idoperacao::int             as idoperacao,
    descricao_operacao,
    permite_renegociacao::boolean as permite_renegociacao,
    dt_carga
from cobra.tb_processos
where idprocesso is not null
  );