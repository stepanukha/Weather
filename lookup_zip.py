from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback

# Add the parent directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the WeatherAPI functions
import WeatherAPI

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
            
            # Extract the zip code and country code
            zip_code = data.get('zip_code', '')
            country_code = data.get('country_code', 'US')
            
            if not zip_code:
                self._send_error_response('No zip code provided', 400)
                return
            
            # Call the WeatherAPI function
            result = WeatherAPI.get_coordinates_from_zip(zip_code, country_code)
            
            # Send the response
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            print(f"Error in lookup_zip: {str(e)}")
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