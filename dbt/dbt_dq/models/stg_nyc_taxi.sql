SELECT 
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    passenger_count,
    trip_distance,
    PULocationID AS pickup_location_id,
    DOLocationID AS dropoff_location_id,
    fare_amount,
    tip_amount,
    total_amount
FROM {{ ref('nyc_taxi_data') }}