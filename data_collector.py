from sustainability_collectors import SustainabilityCollector
from typing import Dict, Any
import logging
import json
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FashionDataCollector:
    def __init__(self):
        self.collector = SustainabilityCollector()
        self.logger = logging.getLogger(__name__)
        self.cache_file = "brand_cache.json"
        self.cache_duration = timedelta(hours=24)
        self.base_brands = self.initialize_brands()

    def _load_cache(self) -> Dict[str, Any]:
        """Load cached brand data if available and fresh"""
        try:
            cache_path = os.path.join(os.path.dirname(__file__), self.cache_file)
            logging.debug(f"Attempting to load cache from: {cache_path}")
            
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    logging.debug("Cache file found, reading contents...")
                    cache_data = json.load(f)
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    logging.debug(f"Cache timestamp: {cache_time}")
                    
                    if cache_time + self.cache_duration > datetime.now():
                        logging.info("Using cached data")
                        return cache_data['brands']
                    else:
                        logging.debug("Cache is stale, will fetch fresh data")
            else:
                logging.debug("No cache file found")
        except Exception as e:
            logging.error(f"Error loading cache: {str(e)}")
        return None

    def _save_cache(self, brands: Dict[str, Any]) -> None:
        """Save brand data to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'brands': brands
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            self.logger.error(f"Error saving cache: {str(e)}")

    def get_sustainability_data(self, brand: str) -> Dict[str, Any]:
        """Get sustainability data for a specific brand"""
        try:
            return {
                "brand_specific": self.collector.get_brand_specific_data(brand),
                "transparency": self.collector.get_fashion_revolution_data(brand),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error collecting sustainability data for {brand}: {str(e)}")
            return {
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }

    def initialize_brands(self) -> Dict[str, Any]:
        # Try to load from cache first
        cached_brands = self._load_cache()
        if cached_brands:
            return cached_brands

        brands = {
            "Patagonia": {
                "items": {"jacket": 200, "pants": 100, "shirt": 50},
                "rating": "A",
                "focus": "Both materials and labor"
            },
            "H&M Conscious": {
                "items": {"dress": 50, "shirt": 30, "pants": 40},
                "rating": "B+",
                "focus": "Materials"
            },
            "Levi's": {
                "items": {"jeans": 98, "jacket": 108, "shirt": 45},
                "rating": "B",
                "focus": "Materials"
            },
            "Nike": {
                "items": {"shoes": 120, "shirt": 35, "pants": 55},
                "rating": "B+",
                "focus": "Both materials and labor"
            },
            "Adidas": {
                "items": {"shoes": 100, "shirt": 30, "pants": 50},
                "rating": "B+",
                "focus": "Materials"
            },
            "The North Face": {
                "items": {"jacket": 180, "backpack": 89, "shirt": 40},
                "rating": "B+",
                "focus": "Both materials and labor"
            }
        }

        # Enrich with sustainability data
        for brand in brands:
            try:
                brands[brand]["sustainability_data"] = self.get_sustainability_data(brand)
            except Exception as e:
                self.logger.error(f"Failed to initialize data for {brand}: {str(e)}")
                brands[brand]["sustainability_data"] = {
                    "error": str(e),
                    "last_updated": datetime.now().isoformat()
                }

        # Save to cache
        self._save_cache(brands)
        return brands

    def update_brand_database(self) -> Dict[str, Any]:
        """Update brand database with fresh sustainability data"""
        try:
            updated_brands = self.initialize_brands()
            self._save_cache(updated_brands)
            return updated_brands
        except Exception as e:
            self.logger.error(f"Failed to update brand database: {str(e)}")
            # Fall back to cached data if available
            cached_brands = self._load_cache()
            return cached_brands if cached_brands else self.base_brands

    def validate_data_quality(self) -> Dict[str, Any]:
        """Validate data quality and completeness"""
        validation = {
            "missing_data": [],
            "price_outliers": [],
            "data_coverage": {}
        }
        
        required_fields = ["items", "rating", "focus", "sustainability_data"]
        
        for brand, data in self.base_brands.items():
            # Check for missing required fields
            missing = [field for field in required_fields if field not in data]
            if missing:
                validation["missing_data"].append({"brand": brand, "missing_fields": missing})
                
            # Check for price outliers (prices that deviate significantly from mean)
            for item, price in data["items"].items():
                all_prices = [b["items"].get(item) for b in self.base_brands.values() 
                             if item in b["items"]]
                mean_price = sum(all_prices) / len(all_prices)
                if abs(price - mean_price) / mean_price > 0.5:  # 50% deviation
                    validation["price_outliers"].append({
                        "brand": brand,
                        "item": item,
                        "price": price,
                        "mean_price": mean_price
                    })
            
            # Calculate data coverage
            if "sustainability_data" in data:
                coverage = {
                    "brand_specific": bool(data["sustainability_data"].get("brand_specific")),
                    "transparency": bool(data["sustainability_data"].get("transparency")),
                    "last_updated": data["sustainability_data"].get("last_updated")
                }
                validation["data_coverage"][brand] = coverage
        
        return validation