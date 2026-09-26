select
 observation_id, year as year_from, year_to, geo_code, geo_name, geo_type,
 parent_code, structure, level, grade, indicator, value as rate_pct,
 value_status, source_sha256, source_url, source_member, source_sheet, source_cell
from {{ source('education', 'observations') }}
