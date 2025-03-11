from flask import Flask, render_template, request, jsonify, url_for
import WeatherAPI
import numpy as np
import traceback
import os

# Get the application root path from environment variable or use default
APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT', '')

app = Flask(__name__)

# Configure the application root if needed
if APPLICATION_ROOT:
    app.config['APPLICATION_ROOT'] = APPLICATION_ROOT

# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    """Return JSON instead of HTML for 404 errors"""
    print(f"404 error: {request.path}")
    response = jsonify({
        "success": False,
        "error": f"Endpoint not found: {request.path}"
    })
    response.status_code = 404
    return response

# Error handler for all exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for any other error"""
    # Log the error and stacktrace
    print(f"An error occurred: {str(e)}")
    print(traceback.format_exc())
    
    # Return JSON response
    response = jsonify({
        "success": False,
        "error": f"Server error: {str(e)}"
    })
    response.status_code = 500
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup_zip', methods=['POST'])
def lookup_zip():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON in request'
            }), 400
            
        zip_code = data.get('zip_code', '')
        country_code = data.get('country_code', 'US')
        
        if not zip_code:
            return jsonify({
                'success': False,
                'error': 'No zip code provided'
            }), 400
        
        result = WeatherAPI.get_coordinates_from_zip(zip_code, country_code)
        return jsonify(result)
    except Exception as e:
        print(f"Error in lookup_zip: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f"Server error: {str(e)}"
        }), 500

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON in request'
            }), 400
            
        latitude = data.get('latitude', 39.9523)
        longitude = data.get('longitude', -75.1638)
        
        # Get weather data and recommendation
        weather_data = WeatherAPI.get_weather_data(latitude, longitude)
        recommendation = WeatherAPI.get_clothing_recommendation(weather_data)
        
        # Convert NumPy values to Python native types and ensure proper rounding
        weather_summary = {
            'avg_temp': float(round(weather_data['temperature'].mean(), 1)),  # Round to 1 decimal place
            'max_precip': float(round(max(weather_data['precipitation']), 2)),
            'max_wind': float(round(max(weather_data['windspeed']), 1))
        }
        
        # Convert any NumPy arrays in recommendation to lists
        for key, value in recommendation.items():
            if isinstance(value, np.ndarray):
                recommendation[key] = value.tolist()
        
        # Return JSON response
        return jsonify({
            'success': True,
            'weather': weather_summary,
            'recommendation': recommendation
        })
    except Exception as e:
        print(f"Error in get_recommendation: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f"Server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Print the application URLs for debugging
    print(f"Application root: {APPLICATION_ROOT}")
    with app.test_request_context():
        print(f"Index URL: {url_for('index')}")
        print(f"Lookup ZIP URL: {url_for('lookup_zip')}")
        print(f"Get recommendation URL: {url_for('get_recommendation')}")
    
    app.run(debug=True) 