with source as (
    select * from cobra.tb_crm_cadastro
),
renamed as (
    select
        cgc_cpf,
        nome,
        estado_civil,
        genero,
        data_nascimento::date as data_nascimento,
        end_cep,
        end_rua,
        end_numero,
        end_complemento,
        end_bairro,
        end_cidade,
        end_uf,
        email,
        email2,
        telefone_fixo,
        celular,
        whatsapp,
        conjuge_nome,
        conjuge_cpf,
        emp_empresa,
        emp_cargo,
        emp_salario::numeric as emp_salario,
        emp_telefone,
        emp_end_logradouro,
        emp_end_numero,
        emp_end_cep,
        emp_end_bairro,
        emp_end_cidade,
        ref1_nome,
        ref1_grau,
        ref1_telefone,
        ref2_nome,
        ref2_grau,
        ref2_telefone,
        dt_carga
    from source
    where cgc_cpf is not null
)
select * from renamed
