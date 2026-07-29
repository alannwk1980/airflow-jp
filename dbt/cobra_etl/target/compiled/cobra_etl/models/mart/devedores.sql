

select
    cgc_cpf                 as cpf_cnpj,
    nome                    as nome_cliente,
    data_nascimento         as data_nasc,
    case genero
        when 'Masculino' then 'M'::bpchar
        when 'Feminino'  then 'F'::bpchar
        else null
    end                     as sexo,
    conjuge_nome            as nome_conjuge,
    emp_empresa             as nome_empresa,
    emp_cargo               as funcao_cargo,
    emp_salario             as renda_devedor,
    dt_carga                as data_atualizacao
from "gestor_magazine"."cobra_staging"."stg_cadastro"