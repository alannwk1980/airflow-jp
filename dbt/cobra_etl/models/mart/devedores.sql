{{
    config(
        materialized='incremental',
        unique_key='cpf_cnpj',
        incremental_strategy='merge',
        merge_update_columns=[
            'nome_cliente','data_nasc','sexo','nome_conjuge',
            'nome_empresa','funcao_cargo','renda_devedor','data_atualizacao'
        ],
        alias='devedores',
        schema='public'
    )
}}

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
from {{ ref('stg_cadastro') }}
