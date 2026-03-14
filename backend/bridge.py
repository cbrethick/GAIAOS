import sys
import json
import os
from datetime import datetime

# Add the current directory to sys.path so we can import modules/utils
sys.path.insert(0, os.path.dirname(__file__))

from modules.flood     import predict_flood
from modules.climate   import predict_climate
from modules.crop      import predict_crop_yield
from modules.wildfire  import predict_wildfire
from modules.traffic   import predict_traffic, predict_urban_growth

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Insufficient arguments. Usage: bridge.py <module> <lat> <lon> [location] [extra]"}))
        return

    module = sys.argv[1]
    lat = float(sys.argv[2])
    lon = float(sys.argv[3])
    location = sys.argv[4] if len(sys.argv) > 4 else ""
    extra = sys.argv[5] if len(sys.argv) > 5 else ""

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
        else:
            result = {"error": f"Unknown module: {module}"}
        
        # Ensure result is JSON serializable
        print(json.dumps(result, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
