from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qsl
import sys
import os
from datetime import datetime

# Add the root directory to sys.path so we can import from backend/
# Vercel's root is usually one level up from /api
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now import the modules from the backend folder
from backend.modules.flood     import predict_flood
from backend.modules.climate   import predict_climate
from backend.modules.crop      import predict_crop_yield
from backend.modules.wildfire  import predict_wildfire
from backend.modules.traffic   import predict_traffic, predict_urban_growth

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query = dict(parse_qsl(parsed_url.query))
        
        module = query.get('module')
        lat = float(query.get('lat', 0))
        lon = float(query.get('lon', 0))
        location = query.get('location', '')
        extra = query.get('extra', '')

        try:
            if module == "flood":
                result = predict_flood(lat, lon, location)
            elif module == "climate":
                result = predict_climate(lat, lon, "", location)
            elif module == "crop":
                crop_type = extra if extra else "Rice"
                result = predict_crop_yield(lat, lon, crop_type, location)
            elif module == "wildfire":
                result = predict_wildfire(lat, lon, location)
            elif module == "traffic":
                hour = datetime.now().hour
                day_type = "Weekday" if datetime.now().weekday() < 5 else "Weekend"
                result = predict_traffic(lat, lon, location, hour, day_type)
            elif module == "urban":
                years = int(extra) if extra.isdigit() else 5
                result = predict_urban_growth(lat, lon, location, years)
            elif module == "status":
                result = {"status": "GaiaOS Prediction Engine Online", "bridge": "Vercel Serverless"}
            else:
                result = {"error": f"Unknown module: {module}"}
            
            output = json.dumps(result, default=str)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(output.encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
