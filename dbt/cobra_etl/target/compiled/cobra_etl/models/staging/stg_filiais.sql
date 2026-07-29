
select
    cod_loja::int           as cod_loja,
    nome_loja,
    cod_regional::int       as cod_regional,
    nome_regional,
    cod_empresagrupo::int   as cod_empresagrupo,
    cod_empresa::int        as cod_empresa,
    uf,
    cnpj_cpf,
    dt_carga
from cobra.tb_filiais
where cod_loja is not null