-- Criação da base de dados lógica
CREATE DATABASE IF NOT EXISTS weather_analytics_db;

-- Criação da tabela externa mapeada sobre o Amazon S3
CREATE EXTERNAL TABLE IF NOT EXISTS weather_analytics_db.raw_weather (
    latitude DOUBLE,
    longitude DOUBLE,
    collected_at_utc STRING,
    weather_time STRING,
    temperature_celsius DOUBLE,
    relative_humidity DOUBLE,
    precipitation_mm DOUBLE,
    wind_speed_kmh DOUBLE
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
    'ignore.malformed.json' = 'true'
)
LOCATION 's3://datalake-clima-raw-lucas-2026/raw/'
TBLPROPERTIES (
    'has_encrypted_data'='false'
);

-- Sincronização do catálogo com as pastas criadas no S3
MSCK REPAIR TABLE weather_analytics_db.raw_weather;