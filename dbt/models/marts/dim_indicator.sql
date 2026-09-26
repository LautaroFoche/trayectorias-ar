select distinct indicator,
 case indicator when 'abandono' then 'Abandono interanual'
 when 'promocion' then 'Promoción efectiva' else 'Repitencia' end as indicator_name,
 'porcentaje' as unit
from {{ ref('stg_observations') }}
