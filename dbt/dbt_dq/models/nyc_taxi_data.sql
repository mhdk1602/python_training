{{ config(materialized='table') }}

SELECT 
    NULL::INT AS VendorID,
    NULL::TIMESTAMP AS tpep_pickup_datetime,
    NULL::TIMESTAMP AS tpep_dropoff_datetime,
    NULL::FLOAT AS passenger_count,
    NULL::FLOAT AS trip_distance,
    NULL::FLOAT AS RatecodeID,
    NULL::VARCHAR AS store_and_fwd_flag,
    NULL::INT AS PULocationID,
    NULL::INT AS DOLocationID,
    NULL::INT AS payment_type,
    NULL::FLOAT AS fare_amount,
    NULL::FLOAT AS extra,
    NULL::FLOAT AS mta_tax,
    NULL::FLOAT AS tip_amount,
    NULL::FLOAT AS tolls_amount,
    NULL::FLOAT AS improvement_surcharge,
    NULL::FLOAT AS total_amount,
    NULL::FLOAT AS congestion_surcharge,
    NULL::FLOAT AS Airport_fee
WHERE FALSE