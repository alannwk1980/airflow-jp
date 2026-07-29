
select
    nome_loja,
    cod_regional,
    nome_regional,
    cod_empresa,
    cod_loja::varchar           as cod_loja,
    uf,
    cod_empresagrupo::smallint  as cod_empresagrupo
from "gestor_magazine"."cobra_staging"."stg_filiais"