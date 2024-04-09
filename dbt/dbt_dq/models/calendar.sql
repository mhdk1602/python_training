{{
  config(
    materialized='table'
  )
}}

SELECT 
  NULL::DATE as cal_date,
  NULL::VARCHAR(1) as weekend,
  NULL::VARCHAR(1) as holiday
WHERE FALSE