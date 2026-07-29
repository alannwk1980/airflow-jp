
with email1 as (
    select
        cgc_cpf                     as cpf_cnpj,
        lower(trim(email))          as email,
        true                        as prioritario,
        false                       as blacklist,
        dt_carga                    as data_atualizacao
    from "gestor_magazine"."cobra_staging"."stg_cadastro"
    where email is not null
      and trim(email) != ''
      and email like '%@%'
),
email2 as (
    select
        cgc_cpf                     as cpf_cnpj,
        lower(trim(email2))         as email,
        false                       as prioritario,
        false                       as blacklist,
        dt_carga                    as data_atualizacao
    from "gestor_magazine"."cobra_staging"."stg_cadastro"
    where email2 is not null
      and trim(email2) != ''
      and email2 like '%@%'
      and lower(trim(email2)) != lower(trim(email))
),
todos as (
    select * from email1
    union all
    select * from email2
)
select distinct on (cpf_cnpj, email)
    cpf_cnpj, email, prioritario, blacklist, data_atualizacao
from todos
order by cpf_cnpj, email, prioritario desc