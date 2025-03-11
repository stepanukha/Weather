from flask import Flask, render_template, request, jsonify, url_for
import WeatherAPI
import numpy as np
import traceback
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the application root path from environment variable or use default
APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT', '')
logger.info(f"Starting application with APPLICATION_ROOT: '{APPLICATION_ROOT}'")

app = Flask(__name__)

# Configure the application root if needed
if APPLICATION_ROOT:
    app.config['APPLICATION_ROOT'] = APPLICATION_ROOT
    logger.info(f"Set application root to: {APPLICATION_ROOT}")

# Error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    """Return JSON instead of HTML for 404 errors"""
    path = request.path
    logger.error(f"404 error: {path}")
    
    # Log request details for debugging
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request URL: {request.url}")
    logger.info(f"Request base URL: {request.base_url}")
    
    response = jsonify({
        "success": False,
        "error": f"Endpoint not found: {path}",
        "debug_info": {
            "method": request.method,
            "url": request.url,
            "base_url": request.base_url,
            "application_root": APPLICATION_ROOT
        }
    })
    response.status_code = 404
    return response

# Error handler for all exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for any other error"""
    # Log the error and stacktrace
    logger.error(f"An error occurred: {str(e)}")
    logger.error(traceback.format_exc())
    
    # Return JSON response
    response = jsonify({
        "success": False,
        "error": f"Server error: {str(e)}",
        "debug_info": {
            "exception_type": type(e).__name__,
            "application_root": APPLICATION_ROOT
        }
    })
    response.status_code = 500
    return response

@app.route('/')
def index():
    logger.info(f"Serving index page from root route")
    return render_template('index.html')

# Add a catch-all route for the root path with any trailing segments
@app.route('/<path:path>')
def catch_all(path):
    logger.info(f"Catch-all route accessed with path: {path}")
    
    # If the path is just 'index.html', serve the index page
    if path == 'index.html':
        return render_template('index.html')
    
    # Otherwise, return a 404
    return page_not_found(Exception(f"Path not found: {path}"))

@app.route('/lookup_zip', methods=['POST'])
def lookup_zip():
    logger.info("lookup_zip endpoint called")
    try:
        data = request.get_json()
        if data is None:
            logger.warning("Invalid JSON in request")
            return jsonify({
                'success': False,
                'error': 'Invalid JSON in request'
            }), 400
            
        zip_code = data.get('zip_code', '')
        country_code = data.get('country_code', 'US')
        
        logger.info(f"Looking up zip code: {zip_code}, country: {country_code}")
        
        if not zip_code:
            logger.warning("No zip code provided")
            return jsonify({
                'success': False,
                'error': 'No zip code provided'
            }), 400
        
        result = WeatherAPI.get_coordinates_from_zip(zip_code, country_code)
        logger.info(f"Zip code lookup result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in lookup_zip: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f"Server error: {str(e)}"
        }), 500

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    logger.info("get_recommendation endpoint called")
    try:
        data = request.get_json()
        if data is None:
            logger.warning("Invalid JSON in request")
            return jsonify({
                'success': False,
                'error': 'Invalid JSON in request'
            }), 400
            
        latitude = data.get('latitude', 39.9523)
        longitude = data.get('longitude', -75.1638)
        
        logger.info(f"Getting recommendation for coordinates: {latitude}, {longitude}")
        
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
        response_data = {
            'success': True,
            'weather': weather_summary,
            'recommendation': recommendation
        }
        logger.info(f"Returning recommendation: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error in get_recommendation: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f"Server error: {str(e)}"
        }), 500

# Add OPTIONS method handlers for CORS support
@app.route('/lookup_zip', methods=['OPTIONS'])
def options_lookup_zip():
    response = app.make_default_options_response()
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/get_recommendation', methods=['OPTIONS'])
def options_get_recommendation():
    response = app.make_default_options_response()
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

if __name__ == '__main__':
    # Print the application URLs for debugging
    logger.info(f"Application root: {APPLICATION_ROOT}")
    with app.test_request_context():
        logger.info(f"Index URL: {url_for('index')}")
        logger.info(f"Lookup ZIP URL: {url_for('lookup_zip')}")
        logger.info(f"Get recommendation URL: {url_for('get_recommendation')}")
    
    # Add a message about how to set APPLICATION_ROOT
    logger.info("To set the application root in production, use:")
    logger.info("  export APPLICATION_ROOT='/your-path' before running the app")
    
    app.run(debug=True) 