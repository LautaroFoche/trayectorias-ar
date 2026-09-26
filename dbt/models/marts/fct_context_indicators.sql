select * from {{ source('education', 'context_observations') }}
