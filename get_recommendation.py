from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback

# Add the parent directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the WeatherAPI functions directly
try:
    import WeatherAPI
    import numpy as np
except ImportError as e:
    print(f"Import error: {str(e)}")
    # If import fails, create a mock response for debugging
    class WeatherAPI:
        @staticmethod
        def get_weather_data(latitude, longitude):
            return {
                'temperature': [70.0, 71.0, 72.0],
                'precipitation': [0.0, 0.0, 0.0],
                'windspeed': [5.0, 5.5, 6.0]
            }
        
        @staticmethod
        def get_clothing_recommendation(weather_data):
            return {
                'top': 'Light long-sleeve shirt',
                'bottom': 'Light pants or jeans',
                'outer_layer': '',
                'accessories': []
            }
    
    # Mock numpy if not available
    class np:
        @staticmethod
        def mean(values):
            return sum(values) / len(values)
        
        @staticmethod
        def ndarray(values):
            return False

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
    def do_POST(self):
        try:
            # Get the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse the JSON data
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract the coordinates
            latitude = data.get('latitude', 39.9523)
            longitude = data.get('longitude', -75.1638)
            
            # Get weather data and recommendation
            weather_data = WeatherAPI.get_weather_data(latitude, longitude)
            recommendation = WeatherAPI.get_clothing_recommendation(weather_data)
            
            # Calculate weather summary
            try:
                # Try to use numpy if available
                avg_temp = float(round(np.mean(weather_data['temperature']), 1))
                max_precip = float(round(max(weather_data['precipitation']), 2))
                max_wind = float(round(max(weather_data['windspeed']), 1))
            except:
                # Fallback to manual calculation
                avg_temp = round(sum(weather_data['temperature']) / len(weather_data['temperature']), 1)
                max_precip = round(max(weather_data['precipitation']), 2)
                max_wind = round(max(weather_data['windspeed']), 1)
            
            weather_summary = {
                'avg_temp': avg_temp,
                'max_precip': max_precip,
                'max_wind': max_wind
            }
            
            # Convert any numpy arrays in recommendation to lists
            for key, value in recommendation.items():
                try:
                    if isinstance(value, np.ndarray):
                        recommendation[key] = value.tolist()
                except:
                    # If numpy isn't available, just use the value as is
                    pass
            
            # Prepare the response data
            response_data = {
                'success': True,
                'weather': weather_summary,
                'recommendation': recommendation
            }
            
            # Send the response
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            print(f"Error in get_recommendation: {str(e)}")
            print(traceback.format_exc())
            self._send_error_response(f"Server error: {str(e)}", 500)
    
    def _send_error_response(self, error_message, status_code=500):
        """Helper method to send an error response"""
        self.send_response(status_code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_data = {
            'success': False,
            'error': error_message
        }
        
        self.wfile.write(json.dumps(error_data).encode('utf-8')) 