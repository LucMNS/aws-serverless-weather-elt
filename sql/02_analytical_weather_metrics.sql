WITH metricas_base AS (
    SELECT 
        weather_time,
        temperature_celsius,
        relative_humidity,
        wind_speed_kmh,
        year,
        month,
        day,
        -- Busca a temperatura do registo cronológico anterior
        LAG(temperature_celsius, 1) OVER (
            ORDER BY weather_time ASC
        ) AS temp_anterior,
        
        -- Média móvel das últimas leituras horárias
        AVG(temperature_celsius) OVER (
            ORDER BY weather_time ASC 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS media_movel_temp_3h,

        -- Ranking diário das maiores rajadas de vento
        DENSE_RANK() OVER (
            PARTITION BY year, month, day 
            ORDER BY wind_speed_kmh DESC
        ) AS rank_vento_diario
    FROM 
        weather_analytics_db.raw_weather
)
SELECT 
    weather_time,
    temperature_celsius,
    ROUND(temperature_celsius - temp_anterior, 2) AS variacao_temp_horaria,
    ROUND(media_movel_temp_3h, 2) AS media_movel_temp,
    relative_humidity,
    wind_speed_kmh,
    rank_vento_diario
FROM 
    metricas_base
ORDER BY 
    weather_time DESC;