from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

CURRENCY_API = "https://api.exchangerate-api.com/v4/latest/"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

CITIES = {
    'Austin, USA': {'timezone': 'America/Chicago', 'currency': 'USD', 'lat': 30.27, 'lon': -97.74},
    'New York, USA': {'timezone': 'America/New_York', 'currency': 'USD', 'lat': 40.71, 'lon': -74.01},
    'Los Angeles, USA': {'timezone': 'America/Los_Angeles', 'currency': 'USD', 'lat': 34.05, 'lon': -118.24},
    'London, UK': {'timezone': 'Europe/London', 'currency': 'GBP', 'lat': 51.51, 'lon': -0.13},
    'Paris, France': {'timezone': 'Europe/Paris', 'currency': 'EUR', 'lat': 48.86, 'lon': 2.35},
    'Rome, Italy': {'timezone': 'Europe/Rome', 'currency': 'EUR', 'lat': 41.90, 'lon': 12.50},
    'Palermo, Sicily': {'timezone': 'Europe/Rome', 'currency': 'EUR', 'lat': 38.12, 'lon': 13.36},
    'Berlin, Germany': {'timezone': 'Europe/Berlin', 'currency': 'EUR', 'lat': 52.52, 'lon': 13.41},
    'Tokyo, Japan': {'timezone': 'Asia/Tokyo', 'currency': 'JPY', 'lat': 35.68, 'lon': 139.69},
    'Sydney, Australia': {'timezone': 'Australia/Sydney', 'currency': 'AUD', 'lat': -33.87, 'lon': 151.21},
    'Dubai, UAE': {'timezone': 'Asia/Dubai', 'currency': 'AED', 'lat': 25.20, 'lon': 55.27},
    'Toronto, Canada': {'timezone': 'America/Toronto', 'currency': 'CAD', 'lat': 43.65, 'lon': -79.38},
    'Mexico City, Mexico': {'timezone': 'America/Mexico_City', 'currency': 'MXN', 'lat': 19.43, 'lon': -99.13},
    'Sao Paulo, Brazil': {'timezone': 'America/Sao_Paulo', 'currency': 'BRL', 'lat': -23.55, 'lon': -46.63},
    'Mumbai, India': {'timezone': 'Asia/Kolkata', 'currency': 'INR', 'lat': 19.08, 'lon': 72.88},
    'Singapore': {'timezone': 'Asia/Singapore', 'currency': 'SGD', 'lat': 1.35, 'lon': 103.82},
    'Hong Kong': {'timezone': 'Asia/Hong_Kong', 'currency': 'HKD', 'lat': 22.32, 'lon': 114.17},
    'Amsterdam, Netherlands': {'timezone': 'Europe/Amsterdam', 'currency': 'EUR', 'lat': 52.37, 'lon': 4.90},
}


@app.route('/')
def index():
    cities = list(CITIES.keys())
    return render_template('index.html', cities=cities)


@app.route('/get_time', methods=['POST'])
def get_time():
    city1 = request.json.get('city1')
    city2 = request.json.get('city2')
    
    tz1 = pytz.timezone(CITIES[city1]['timezone'])
    tz2 = pytz.timezone(CITIES[city2]['timezone'])
    
    now = datetime.now(pytz.UTC)
    time1 = now.astimezone(tz1)
    time2 = now.astimezone(tz2)
    
    return jsonify({
        'city1': {
            'name': city1,
            'time': time1.strftime('%I:%M:%S %p'),
            'date': time1.strftime('%A, %B %d, %Y'),
            'hour': time1.hour
        },
        'city2': {
            'name': city2,
            'time': time2.strftime('%I:%M:%S %p'),
            'date': time2.strftime('%A, %B %d, %Y'),
            'hour': time2.hour
        }
    })


@app.route('/get_weather', methods=['POST'])
def get_weather():
    city1 = request.json.get('city1')
    city2 = request.json.get('city2')
    
    def fetch_weather(city):
        lat = CITIES[city]['lat']
        lon = CITIES[city]['lon']
        try:
            response = requests.get(
                WEATHER_API,
                params={
                    'latitude': lat,
                    'longitude': lon,
                    'current_weather': True
                },
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=5
            )
            data = response.json()
            temp_c = data['current_weather']['temperature']
            temp_f = round(temp_c * 9/5 + 32)
            weather_code = data['current_weather']['weathercode']
            
            weather_map = {
                0: ('☀️', 'Clear sky'),
                1: ('🌤️', 'Mainly clear'),
                2: ('⛅', 'Partly cloudy'),
                3: ('☁️', 'Overcast'),
                45: ('🌫️', 'Foggy'),
                48: ('🌫️', 'Depositing rime fog'),
                51: ('🌧️', 'Light drizzle'),
                53: ('🌧️', 'Moderate drizzle'),
                55: ('🌧️', 'Dense drizzle'),
                61: ('🌧️', 'Slight rain'),
                63: ('🌧️', 'Moderate rain'),
                65: ('🌧️', 'Heavy rain'),
                71: ('🌨️', 'Slight snow'),
                73: ('🌨️', 'Moderate snow'),
                75: ('🌨️', 'Heavy snow'),
                80: ('🌦️', 'Rain showers'),
                81: ('🌦️', 'Moderate showers'),
                82: ('🌦️', 'Violent showers'),
                95: ('⛈️', 'Thunderstorm'),
                96: ('⛈️', 'Thunderstorm with hail'),
                99: ('⛈️', 'Thunderstorm with heavy hail'),
            }
            
            emoji, description = weather_map.get(weather_code, ('🌡️', 'Unknown'))
            
            return {
                'temp_c': round(temp_c),
                'temp_f': temp_f,
                'emoji': emoji,
                'description': description
            }
        except Exception as e:
            print(f"Weather error: {e}")
            return {
                'temp_c': '--',
                'temp_f': '--',
                'emoji': '❓',
                'description': 'Unable to fetch weather'
            }
    
    return jsonify({
        'city1': fetch_weather(city1),
        'city2': fetch_weather(city2)
    })


@app.route('/convert_currency', methods=['POST'])
def convert_currency():
    city1 = request.json.get('city1')
    city2 = request.json.get('city2')
    amount = float(request.json.get('amount', 100))
    
    from_currency = CITIES[city1]['currency']
    to_currency = CITIES[city2]['currency']
    
    try:
        response = requests.get(CURRENCY_API + from_currency, timeout=5)
        data = response.json()
        rate = data['rates'][to_currency]
        converted = round(amount * rate, 2)
        
        return jsonify({
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': amount,
            'converted': converted,
            'rate': round(rate, 4)
        })
    except Exception as e:
        return jsonify({'error': 'Unable to fetch exchange rates'})


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
