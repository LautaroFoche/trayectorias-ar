select year_from,geo_code,level,count(*) as n
from {{ ref('mart_continuity') }} group by year_from,geo_code,level having count(*)<>1
