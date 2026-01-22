import json
import time
import psycopg2
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

# 🔁 Connect to Kafka
while True:
    try:
        consumer = KafkaConsumer(
            "weather",
            bootstrap_servers="kafka:9092",

            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="weather-group",
            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )
        print("✅ Connected to Kafka")
        break
    except NoBrokersAvailable:
        print("❌ Kafka not available, retrying in 5 seconds...")
        time.sleep(5)

# 🔁 Connect to PostgreSQL
while True:
    try:
        conn = psycopg2.connect(
            dbname="weatherdb",
            user="root",
            password="root",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        print("✅ Connected to PostgreSQL")
        break
    except Exception as e:
        print("❌ PostgreSQL not available, retrying in 5 seconds...", e)
        time.sleep(5)

# 🧱 Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    temperature FLOAT,
    humidity INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

print("📥 Waiting for weather data...")

# 🔁 Consume Kafka messages
for message in consumer:
    try:
        data = message.value

        city = data["location"]["name"]
        temperature = data["current"]["temp_c"]
        humidity = data["current"]["humidity"]

        cur.execute(
            """
            INSERT INTO weather_data (city, temperature, humidity)
            VALUES (%s, %s, %s)
            """,
            (city, temperature, humidity)
        )
        conn.commit()

        print(f"🌦️ Inserted: {city} | {temperature}°C | {humidity}%")

    except Exception as e:
        print("⚠️ Failed to process message:", e)
