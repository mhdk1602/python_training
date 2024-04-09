WITH taxi_data AS (
    SELECT 
        *,
        DATE_PART('hour', tpep_pickup_datetime) AS pickup_hour,
        CASE 
            WHEN DATE_PART('dow', tpep_pickup_datetime) IN (0, 6) THEN 'Y'
            ELSE 'N'
        END AS weekend_flag
    FROM {{ ref('nyc_taxi_data') }} AS n
),
pickup_location AS (
    SELECT 
        *
    FROM {{ ref('taxi_zone_lookup') }} AS pc
),
dropoff_location AS (
    SELECT 
        *
    FROM {{ ref('taxi_zone_lookup') }} AS dc
),
calendar_data AS (
    SELECT 
        *
    FROM {{ ref('calendar') }} AS c
)
SELECT
    t.*,
    pc."Borough" AS pickup_borough,
    pc."Zone" AS pickup_zone,
    pc.service_zone AS pickup_service_zone,
    dc."Borough" AS dropoff_borough,
    dc."Zone" AS dropoff_zone,
    dc.service_zone AS dropoff_service_zone,
    cd.weekend,
    cd.holiday
FROM taxi_data AS t
LEFT JOIN pickup_location AS pc
    ON t.pulocationid = pc."LocationID"
LEFT JOIN dropoff_location AS dc
    ON t.dolocationid = dc."LocationID"
LEFT JOIN calendar_data AS cd
    ON t.tpep_pickup_datetime::date = cd.cal_date