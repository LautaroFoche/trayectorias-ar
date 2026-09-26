select 1 as failure where (select count(*) from {{ ref('mart_national_context') }}) <> 832 or (select count(*) from {{ ref('mart_digital_evidence') }}) <> 142
