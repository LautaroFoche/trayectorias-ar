select *,
 case when year_from between 2019 and 2021 then 1 else 0 end as pandemic_context,
 case when year_from = 2024 and level = 'secundaria'
   and geo_code in ('00','06','06C','06R') then 1 else 0 end as methodology_break,
 case when rate_pct < 0 or rate_pct > 100 then 1 else 0 end as outside_theoretical_range
from {{ ref('stg_observations') }}
