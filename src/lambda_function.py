import os
import json
import urllib.request
from datetime import datetime, timezone
import boto3

# Inicializa o cliente fora do handler para reaproveitar conexão TCP
s3_client = boto3.client('s3')

# Leitura via Variáveis de Ambiente com fallback seguro
BUCKET_NAME = os.getenv('BUCKET_NAME', 'datalake-clima-raw-lucas-2026')
LATITUDE = float(os.getenv('LATITUDE', '-23.5505'))
LONGITUDE = float(os.getenv('LONGITUDE', '-46.6333'))


def lambda_handler(event, context):
    """
    Extrai dados climáticos da API Open-Meteo, adiciona metadados de linhagem (UTC)
    e armazena o objeto JSON bruto particionado em formato Hive no Amazon S3.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        f"&timezone=America/Sao_Paulo"
    )

    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'AWS-Lambda-DataPipeline/1.0'}
    )

    with urllib.request.urlopen(req) as response:
        if response.status != 200:
            raise RuntimeError(f"Falha na API Open-Meteo. HTTP Status: {response.status}")
        data = json.loads(response.read().decode('utf-8'))

    now_utc = datetime.now(timezone.utc)
    current = data.get('current', {})

    payload = {
        'latitude': data.get('latitude'),
        'longitude': data.get('longitude'),
        'collected_at_utc': now_utc.isoformat(),
        'weather_time': current.get('time'),
        'temperature_celsius': current.get('temperature_2m'),
        'relative_humidity': current.get('relative_humidity_2m'),
        'precipitation_mm': current.get('precipitation'),
        'wind_speed_kmh': current.get('wind_speed_10m')
    }

    # Particionamento Hive-Style para otimização de leitura
    year = now_utc.strftime('%Y')
    month = now_utc.strftime('%m')
    day = now_utc.strftime('%d')
    file_timestamp = now_utc.strftime('%H%M%S')

    s3_key = f"raw/year={year}/month={month}/day={day}/weather_{file_timestamp}.json"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(payload),
        ContentType='application/json'
    )

    print(f"Sucesso: Arquivo gravado em s3://{BUCKET_NAME}/{s3_key}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Ingestao concluida com sucesso',
            's3_uri': f"s3://{BUCKET_NAME}/{s3_key}"
        })
    }