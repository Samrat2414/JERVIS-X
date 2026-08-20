import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def weather_code_to_text(code):
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Heavy drizzle",
        61: "Light rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Light snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Light rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        95: "Thunderstorm",
    }

    return weather_codes.get(
        code,
        "Unknown weather condition",
    )


def get_weather_data(city):
    city = city.strip()

    if not city:
        return {
            "success": False,
            "error": "Please tell me the city name.",
        }

    try:
        location_response = requests.get(
            GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )

        location_response.raise_for_status()
        location_data = location_response.json()

        results = location_data.get("results")

        if not results:
            return {
                "success": False,
                "error": f"I could not find the city {city}.",
            }

        location = results[0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        city_name = location.get("name", city)
        country = location.get("country", "")

        weather_response = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            },
            timeout=10,
        )

        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data.get("current", {})

        temperature = current.get("temperature_2m")
        feels_like = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        wind_speed = current.get("wind_speed_10m")
        weather_code = current.get("weather_code")

        return {
            "success": True,
            "city": city_name,
            "country": country,
            "condition": weather_code_to_text(weather_code),
            "temperature": temperature,
            "feels_like": feels_like,
            "humidity": humidity,
            "wind_speed": wind_speed,
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": (
                "I could not get live weather information. "
                f"Please check your internet connection. Details: {error}"
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "error": f"Weather error: {error}",
        }


def get_weather(city):
    data = get_weather_data(city)

    if not data.get("success"):
        return data.get(
            "error",
            "I could not get weather information.",
        )

    return (
        f"Weather in {data['city']}, {data['country']}:\n"
        f"Condition: {data['condition']}\n"
        f"Temperature: {data['temperature']}°C\n"
        f"Feels like: {data['feels_like']}°C\n"
        f"Humidity: {data['humidity']}%\n"
        f"Wind speed: {data['wind_speed']} km/h"
    )


if __name__ == "__main__":
    print(get_weather("Kolkata"))