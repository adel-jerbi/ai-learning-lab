import os
import urllib.parse
import json
import time
import urllib.request
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# client = OpenAI(
#     base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
#     api_key="ollama",  # required by the client; Ollama ignores it
# )
_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}
def _http_get_json(url: str) -> dict:
    
    started = time.perf_counter()
    req = urllib.request.Request(url, headers={"User-Agent": "first-agent/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            elapsed_ms = (time.perf_counter() - started) * 1000
            
            return json.loads(body)
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
       
        raise

def get_weather(city: str) -> dict:
    """Get current weather and this day's forecast from 9am to 10pm for a city (Open-Meteo, no API key)."""
    from datetime import datetime

    city = city.strip()
    if not city:
        return {"error": "City name is required."}

    try:
        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search?"
            + urllib.parse.urlencode({"name": city, "count": 1, "language": "en", "format": "json"})
        )
        geo = _http_get_json(geo_url)
        results = geo.get("results") or []
        if not results:
            return {"error": f"City not found: {city}"}

        place = results[0]
        lat = place["latitude"]
        lon = place["longitude"]
        label = place.get("name", city)
        country = place.get("country", "")

        weather_url = (
            "https://api.open-meteo.com/v1/forecast?"
            + urllib.parse.urlencode(
                {
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "hourly": "temperature_2m,weather_code,wind_speed_10m",
                    "forecast_days": 1,
                    "timezone": "auto",
                }
            )
        )
        data = _http_get_json(weather_url)
        current = data.get("current") or {}
        code = current.get("weather_code")
        condition = _WEATHER_CODES.get(code, f"Unknown (code {code})")

        hourly = data.get("hourly") or {}
        times = hourly.get("time") or []
        temps = hourly.get("temperature_2m") or []
        codes = hourly.get("weather_code") or []
        winds = hourly.get("wind_speed_10m") or []

        # Select only hours between 9am and 10pm of "today" (based on metadata/first hourly value)
        desired_hours = set(str(h).zfill(2) + ":00" for h in range(9, 23))  # 09:00 to 22:00 inclusive

        today_date = None
        if times:
            # Extract date (YYYY-MM-DD) from first hourly value as "today"
            today_date = times[0].split("T")[0]

        next_hours = []
        for i, t in enumerate(times):
            if today_date is not None and not t.startswith(today_date):
                continue  # Only keep today's values
            # t is ISO8601 like "2024-06-03T09:00"
            hour_part = t.split("T")[1] if "T" in t else None
            if hour_part not in desired_hours:
                continue
            h_code = codes[i] if i < len(codes) else None
            next_hours.append(
                {
                    "time": t,
                    "temperature_c": temps[i] if i < len(temps) else None,
                    "condition": _WEATHER_CODES.get(h_code, f"Unknown (code {h_code})"),
                    "wind_speed_kmh": winds[i] if i < len(winds) else None,
                }
            )

        return {
            "city": label,
            "country": country,
            "temperature_c": current.get("temperature_2m"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "condition": condition,
            "weather_code": code,
            "hourly_forecast": next_hours,
        }
    except urllib.error.URLError as exc:
        return {"error": f"Network error fetching weather: {exc}"}
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        return {"error": f"Unexpected weather response: {exc}"}

#get the city name from the user
city = input("Enter the city name: ")
report = get_weather(city)
date_time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
prompt = """
You are a local weather and outdoor-activity advisor.
Write a news script for the weather forecast for morning, noon , afternoon and evening report using the following data structure:

the report data structure is:

    "city": "City name",
    "country": "Country name",
    "temperature_c": "Temperature in Celsius",
    "humidity_percent": "Humidity percentage",
    "wind_speed_kmh": "Wind speed in km/h",
    "condition": "Weather condition",
    "weather_code": "Weather code",
    "hourly_forecast": "List of hourly forecasts"


and the hourly_forecast is a list of 15 hourly forecasts from 9am to 10pm of "today" (based on metadata/first hourly value).
the hourly_forecast structure is:

    "time": "Time in ISO8601 format",
    "temperature_c": "Temperature in Celsius",
    "condition": "Weather condition",
    "wind_speed_kmh": "Wind speed in km/h"

code weather is:
{_WEATHER_CODES}

date time now is {date_time_now}

the forecast data for the next 15 hours data:
```
{report}
```


use mast use maximum 8 sentences in one paragraph for the full forcast news.
focus on temperature, weather conditions and wind speed.
"""
r = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt.format(report=report, date_time_now=date_time_now, _WEATHER_CODES=_WEATHER_CODES)}],
)
print(r.choices[0].message.content)