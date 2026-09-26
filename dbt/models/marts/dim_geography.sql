select distinct geo_code, geo_name, geo_type, parent_code from {{ ref('stg_observations') }}
