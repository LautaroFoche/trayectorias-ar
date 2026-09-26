select f.observation_id from {{ ref('fct_context_indicators') }} f join {{ source('education','source_catalog') }} s on f.source_id=s.source_id where f.source_sha256<>s.sha256
