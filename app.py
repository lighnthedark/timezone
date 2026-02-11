from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

CURRENCY_API = "https://api.exchangerate-api.com/v4/latest/"
WEATHER_API_KEY = "afc7bdc2a8464e63bf5201444262601"

CITIES = {
    'Austin, USA': {'timezone': 'America/Chicago', 'currency': 'USD', 'lat': 30.27, 'lon': -97.74},
    'New York, USA': {'timezone': 'America/New_York', 'currency': 'USD', 'lat': 40.71, 'lon': -74.01},
    'Los Angeles, USA': {'timezone': 'America/Los_Angeles', 'currency': 'USD', 'lat': 34.05, 'lon': -118.24},
    'Toronto, Canada': {'timezone': 'America/Toronto', 'currency': 'CAD', 'lat': 43.65, 'lon': -79.38},
    'Mexico City, Mexico': {'timezone': 'America/Mexico_City', 'currency': 'MXN', 'lat': 19.43, 'lon': -99.13},
    'Sao Paulo, Brazil': {'timezone': 'America/Sao_Paulo', 'currency': 'BRL', 'lat': -23.55, 'lon': -46.63},
    'London, UK': {'timezone': 'Europe/London', 'currency': 'GBP', 'lat': 51.51, 'lon': -0.13},
    'Paris, France': {'timezone': 'Europe/Paris', 'currency': 'EUR', 'lat': 48.86, 'lon': 2.35},
    'Lisbon, Portugal': {'timezone': 'Europe/Lisbon', 'currency': 'EUR', 'lat': 38.72, 'lon': -9.14},
    'Rome, Italy': {'timezone': 'Europe/Rome', 'currency': 'EUR', 'lat': 41.90, 'lon': 12.50},
    'Palermo, Sicily': {'timezone': 'Europe/Rome', 'currency': 'EUR', 'lat': 38.12, 'lon': 13.36},
    'Berlin, Germany': {'timezone': 'Europe/Berlin', 'currency': 'EUR', 'lat': 52.52, 'lon': 13.41},
    'Amsterdam, Netherlands': {'timezone': 'Europe/Amsterdam', 'currency': 'EUR', 'lat': 52.37, 'lon': 4.90},
    'Sarajevo, Bosnia': {'timezone': 'Europe/Sarajevo', 'currency': 'BAM', 'lat': 43.86, 'lon': 18.41},
    'Dubai, UAE': {'timezone': 'Asia/Dubai', 'currency': 'AED', 'lat': 25.20, 'lon': 55.27},
    'Mumbai, India': {'timezone': 'Asia/Kolkata', 'currency': 'INR', 'lat': 19.08, 'lon': 72.88},
    'Singapore': {'timezone': 'Asia/Singapore', 'currency': 'SGD', 'lat': 1.35, 'lon': 103.82},
    'Hong Kong': {'timezone': 'Asia/Hong_Kong', 'currency': 'HKD', 'lat': 22.32, 'lon': 114.17},
    'Tokyo, Japan': {'timezone': 'Asia/Tokyo', 'currency': 'JPY', 'lat': 35.68, 'lon': 139.69},
    'Sydney, Australia': {'timezone': 'Australia/Sydney', 'currency': 'AUD', 'lat': -33.87, 'lon': 151.21},
}


@app.route('/')
def index():
    cities = list(CITIES.keys())
    return render_template('index.html', cities=cities)


@app.route('/test_weather')
def test_weather():
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q=30.27,-97.74",
            timeout=10
        )
        return jsonify({'status': 'success', 'data': response.json()})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


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
                f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={lat},{lon}",
                timeout=10
            )
            data = response.json()
            
            temp_c = data['current']['temp_c']
            temp_f = data['current']['temp_f']
            condition = data['current']['condition']['text']
            
            # Map conditions to emojis
            condition_lower = condition.lower()
            if 'sun' in condition_lower or 'clear' in condition_lower:
                emoji = '☀️'
            elif 'cloud' in condition_lower or 'overcast' in condition_lower:
                emoji = '☁️'
            elif 'rain' in condition_lower or 'drizzle' in condition_lower:
                emoji = '🌧️'
            elif 'snow' in condition_lower:
                emoji = '🌨️'
            elif 'thunder' in condition_lower or 'storm' in condition_lower:
                emoji = '⛈️'
            elif 'fog' in condition_lower or 'mist' in condition_lower:
                emoji = '🌫️'
            elif 'partly' in condition_lower:
                emoji = '⛅'
            else:
                emoji = '🌤️'
            
            return {
                'temp_c': round(temp_c),
                'temp_f': round(temp_f),
                'emoji': emoji,
                'description': condition
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