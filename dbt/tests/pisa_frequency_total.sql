select country_code,indicator,sum(value) as total from {{ ref('mart_digital_evidence') }} where source_id='pisa_ch3' group by country_code,indicator having abs(sum(value)-100)>0.01 or count(*)<>4
