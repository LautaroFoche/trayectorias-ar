select year_from, level, count(*) as jurisdictions
from {{ ref('mart_continuity') }} where geo_type='provincia'
group by year_from,level having count(*)<>24
