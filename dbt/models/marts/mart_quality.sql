select year_from, indicator, value_status, count(*) as observations
from {{ ref('fct_education_rates') }} group by year_from, indicator, value_status
