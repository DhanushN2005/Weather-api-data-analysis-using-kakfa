from flask import Flask, render_template_string, request
import psycopg2

app = Flask(__name__)

# PostgreSQL (Docker)
DB_CONFIG = {
    "dbname": "weatherdb",
    "user": "root",
    "password": "root",
    "host": "127.0.0.1",
    "port": "5433"   # keep 5433 if docker postgres is mapped to 5433
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Weather Dashboard</title>
    <style>
        body { font-family: Arial; background-color: #f2f2f2; }
        h2 { text-align: center; }
        form { text-align: center; margin-bottom: 20px; }
        table {
            margin: auto;
            border-collapse: collapse;
            width: 60%;
            background: white;
        }
        th, td {
            border: 1px solid #aaa;
            padding: 10px;
            text-align: center;
        }
        th {
            background-color: #007BFF;
            color: white;
        }
    </style>
</head>
<body>

<h2>🌦️ Live Weather Dashboard</h2>

<form method="get">
    <label><b>Select City:</b></label>
    <select name="city">
        {% for c in cities %}
            <option value="{{ c }}" {% if c == selected_city %}selected{% endif %}>
                {{ c }}
            </option>
        {% endfor %}
    </select>
    <button type="submit">Get Weather</button>
</form>

{% if data %}
<table>
<tr>
    <th>City</th>
    <th>Temperature (°C)</th>
    <th>Humidity (%)</th>
    <th>Last Updated</th>
</tr>
<tr>
    <td>{{ data[0][0] }}</td>
    <td>{{ data[0][1] }}</td>
    <td>{{ data[0][2] }}</td>
    <td>{{ data[0][3] }}</td>
</tr>
</table>
{% else %}
<p style="text-align:center;">No data available</p>
{% endif %}

</body>
</html>
"""

def ensure_table_exists():
    """Create table if it does not exist"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100),
            temperature FLOAT,
            humidity INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_all_cities():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT city FROM weather_data ORDER BY city;")
    cities = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return cities

def fetch_latest_weather(city):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT city, temperature, humidity, timestamp
        FROM weather_data
        WHERE LOWER(city) = LOWER(%s)
        ORDER BY timestamp DESC
        LIMIT 1;
    """, (city,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

@app.route("/", methods=["GET"])
def index():
    # 🔥 Ensure table always exists
    ensure_table_exists()

    cities = get_all_cities()
    selected_city = request.args.get("city", cities[0] if cities else None)
    data = fetch_latest_weather(selected_city) if selected_city else []

    return render_template_string(
        HTML,
        cities=cities,
        selected_city=selected_city,
        data=data
    )

if __name__ == "__main__":
    app.run(debug=True)
