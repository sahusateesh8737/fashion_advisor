from flask import Flask, render_template, request, jsonify
from data_collector import FashionDataCollector
import threading
import time

app = Flask(__name__)

# Initialize data collector
collector = FashionDataCollector()
fashion_brands = collector.base_brands

def update_brands_periodically():
    """Update brands data every 24 hours"""
    while True:
        global fashion_brands
        fashion_brands = collector.update_brand_database()
        time.sleep(86400)  # 24 hours

# Start background data updates
update_thread = threading.Thread(target=update_brands_periodically)
update_thread.daemon = True
update_thread.start()

# Home route to serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# API route to handle recommendations
@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    clothing_type = data['clothing_type'].lower()
    budget = float(data['budget'])
    priority = data['priority'].lower()

    # Find recommendations
    recommendations = []
    for brand, info in fashion_brands.items():
        if clothing_type in info["items"] and info["items"][clothing_type] <= budget:
            if (priority == "no-preference" or 
                (priority in info["focus"].lower()) or 
                (priority == "both" and "materials" in info["focus"] and "labor" in info["focus"])):
                recommendations.append({
                    "brand": brand,
                    "price": info["items"][clothing_type],
                    "rating": info["rating"],
                    "focus": info["focus"]
                })

    # Sort by rating
    rating_order = {"A": 4, "B+": 3, "B": 2, "C": 1}
    recommendations.sort(key=lambda x: rating_order.get(x["rating"], 0), reverse=True)

    return jsonify(recommendations)

@app.route('/debug/brands', methods=['GET'])
def debug_brands():
    """Debug endpoint to check available brand data"""
    return jsonify({
        "total_brands": len(fashion_brands),
        "available_items": list(set(item for brand in fashion_brands.values() 
                                  for item in brand["items"].keys())),
        "brands_detail": fashion_brands
    })

if __name__ == '__main__':
    # Local development
    app.run(debug=True)
else:
    # Vercel deployment
    app = app