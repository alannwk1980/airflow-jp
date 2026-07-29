
select
    descricao,
    idsituacaoprocesso          as status,
    idprocesso::int             as id_processo,
    nome_processo,
    permite_renegociacao
from "gestor_magazine"."cobra_staging"."stg_processos"