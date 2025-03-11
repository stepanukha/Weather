from flask import Flask, request, jsonify, Response
import sys
import os
import json
import traceback
import numpy as np

# Add the parent directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the WeatherAPI functions directly
import WeatherAPI

# Create a simple Flask app for the API endpoints
app = Flask(__name__)

@app.route('/api/lookup_zip', methods=['POST', 'OPTIONS'])
def api_lookup_zip():
    """API endpoint for looking up zip codes"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        # Get the request data
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
        
        # Call the WeatherAPI function
        result = WeatherAPI.get_coordinates_from_zip(zip_code, country_code)
        
        # Create a response with CORS headers
        response = jsonify(result)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"Error in lookup_zip: {str(e)}")
        print(traceback.format_exc())
        
        # Return error response with CORS headers
        response = jsonify({
            'success': False,
            'error': f"Server error: {str(e)}"
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500

@app.route('/api/get_recommendation', methods=['POST', 'OPTIONS'])
def api_get_recommendation():
    """API endpoint for getting clothing recommendations"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight request
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    try:
        # Get the request data
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
        
        # Convert NumPy values to Python native types
        weather_summary = {
            'avg_temp': float(round(weather_data['temperature'].mean(), 1)),
            'max_precip': float(round(max(weather_data['precipitation']), 2)),
            'max_wind': float(round(max(weather_data['windspeed']), 1))
        }
        
        # Convert any NumPy arrays in recommendation to lists
        for key, value in recommendation.items():
            if isinstance(value, np.ndarray):
                recommendation[key] = value.tolist()
        
        # Create a response with CORS headers
        response = jsonify({
            'success': True,
            'weather': weather_summary,
            'recommendation': recommendation
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        print(f"Error in get_recommendation: {str(e)}")
        print(traceback.format_exc())
        
        # Return error response with CORS headers
        response = jsonify({
            'success': False,
            'error': f"Server error: {str(e)}"
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500

# For local development
if __name__ == '__main__':
    app.run(debug=True) 