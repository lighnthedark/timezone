from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# Free currency API
CURRENCY_API = "https://api.exchangerate-api.com/v4/latest/"

# Major cities with their timezones and currencies
CITIES = {
    'Austin, USA': {'timezone': 'America/Chicago', 'currency': 'USD'},
    'New York, USA': {'timezone': 'America/New_York', 'currency': 'USD'},
    'Los Angeles, USA': {'timezone': 'America/Los_Angeles', 'currency': 'USD'},
    'London, UK': {'timezone': 'Europe/London', 'currency': 'GBP'},
    'Paris, France': {'timezone': 'Europe/Paris', 'currency': 'EUR'},
    'Rome, Italy': {'timezone': 'Europe/Rome', 'currency': 'EUR'},
    'Palermo, Sicily': {'timezone': 'Europe/Rome', 'currency': 'EUR'},
    'Berlin, Germany': {'timezone': 'Europe/Berlin', 'currency': 'EUR'},
    'Tokyo, Japan': {'timezone': 'Asia/Tokyo', 'currency': 'JPY'},
    'Sydney, Australia': {'timezone': 'Australia/Sydney', 'currency': 'AUD'},
    'Dubai, UAE': {'timezone': 'Asia/Dubai', 'currency': 'AED'},
    'Toronto, Canada': {'timezone': 'America/Toronto', 'currency': 'CAD'},
    'Mexico City, Mexico': {'timezone': 'America/Mexico_City', 'currency': 'MXN'},
    'Sao Paulo, Brazil': {'timezone': 'America/Sao_Paulo', 'currency': 'BRL'},
    'Mumbai, India': {'timezone': 'Asia/Kolkata', 'currency': 'INR'},
    'Singapore': {'timezone': 'Asia/Singapore', 'currency': 'SGD'},
    'Hong Kong': {'timezone': 'Asia/Hong_Kong', 'currency': 'HKD'},
    'Amsterdam, Netherlands': {'timezone': 'Europe/Amsterdam', 'currency': 'EUR'},
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
    
    now = datetime.now()
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

@app.route('/convert_currency', methods=['POST'])
def convert_currency():
    city1 = request.json.get('city1')
    city2 = request.json.get('city2')
    amount = float(request.json.get('amount', 1))
    
    currency1 = CITIES[city1]['currency']
    currency2 = CITIES[city2]['currency']
    
    try:
        response = requests.get(f"{CURRENCY_API}{currency1}")
        data = response.json()
        rate = data['rates'][currency2]
        converted = amount * rate
        
        return jsonify({
            'from_currency': currency1,
            'to_currency': currency2,
            'amount': amount,
            'converted': round(converted, 2),
            'rate': round(rate, 4)
        })
    except:
        return jsonify({'error': 'Could not fetch exchange rate'}), 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)