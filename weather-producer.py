import json
import requests
import time
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

API_KEY = "6fdexxxxxxxxxxxxxxxxxxxx262101"
CITY = "COIMBATORE"

URL = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}&aqi=no"

# 🔁 Retry until Kafka is available
while True:
    try:
        producer = KafkaProducer(
            bootstrap_servers="kafka:9092",
            value_serializer=lambda x: json.dumps(x).encode("utf-8")
        )
        print("✅ Connected to Kafka")
        break
    except NoBrokersAvailable:
        print("❌ Kafka not available, retrying in 5 seconds...")
        time.sleep(5)

# 🔁 Fetch weather data continuously
while True:
    try:
        response = requests.get(URL, timeout=10)
        data = response.json()

        producer.send("weather", value=data)
        producer.flush()

        print("🌦️ Sent weather data to Kafka:", data)
        time.sleep(10)

    except Exception as e:
        print("⚠️ Error sending data:", e)
        time.sleep(5)

