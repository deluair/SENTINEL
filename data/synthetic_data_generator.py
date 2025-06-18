"""
SENTINEL Synthetic Data Generator
Generates realistic simulation data for geopolitical trade risk analysis
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging
from faker import Faker
import json

from config.settings import settings
from models.database import (
    Country, Supplier, Product, TradeRoute, TradeFlow, 
    RiskEvent, RiskScore, Company, EconomicIndicator
)
from models.database_connection import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Faker for realistic data
fake = Faker()

class SyntheticDataGenerator:
    """Generates comprehensive synthetic data for SENTINEL"""
    
    def __init__(self):
        self.countries_data = []
        self.suppliers_data = []
        self.products_data = []
        self.trade_routes_data = []
        self.companies_data = []
        
        # Load reference data
        self._load_reference_data()
    
    def _load_reference_data(self):
        """Load reference data for realistic generation"""
        # Country data with realistic geopolitical risk profiles
        self.country_profiles = {
            "USA": {"region": "North America", "risk_base": 0.15, "gdp": 25462700000000},
            "China": {"region": "Asia", "risk_base": 0.35, "gdp": 17963170000000},
            "Germany": {"region": "Europe", "risk_base": 0.20, "gdp": 4072191000000},
            "Japan": {"region": "Asia", "risk_base": 0.25, "gdp": 4231141000000},
            "India": {"region": "Asia", "risk_base": 0.30, "gdp": 3385089000000},
            "UK": {"region": "Europe", "risk_base": 0.25, "gdp": 3070667000000},
            "France": {"region": "Europe", "risk_base": 0.22, "gdp": 2782905000000},
            "Italy": {"region": "Europe", "risk_base": 0.28, "gdp": 2010430000000},
            "Canada": {"region": "North America", "risk_base": 0.18, "gdp": 2139840000000},
            "Brazil": {"region": "South America", "risk_base": 0.32, "gdp": 1920095000000},
            "Russia": {"region": "Europe", "risk_base": 0.45, "gdp": 2240757000000},
            "South Korea": {"region": "Asia", "risk_base": 0.28, "gdp": 1665628000000},
            "Australia": {"region": "Oceania", "risk_base": 0.20, "gdp": 1675418000000},
            "Mexico": {"region": "North America", "risk_base": 0.35, "gdp": 1411754000000},
            "Indonesia": {"region": "Asia", "risk_base": 0.30, "gdp": 1318782000000},
        }
        
        # Industry sectors with risk profiles
        self.industries = {
            "Technology": {"risk_multiplier": 0.8, "revenue_range": (1000000, 1000000000)},
            "Automotive": {"risk_multiplier": 1.2, "revenue_range": (5000000, 5000000000)},
            "Pharmaceuticals": {"risk_multiplier": 0.9, "revenue_range": (2000000, 3000000000)},
            "Electronics": {"risk_multiplier": 1.1, "revenue_range": (1000000, 2000000000)},
            "Textiles": {"risk_multiplier": 1.3, "revenue_range": (500000, 1000000000)},
            "Chemicals": {"risk_multiplier": 1.0, "revenue_range": (2000000, 4000000000)},
            "Food & Beverage": {"risk_multiplier": 0.7, "revenue_range": (1000000, 3000000000)},
            "Energy": {"risk_multiplier": 1.4, "revenue_range": (5000000, 10000000000)},
            "Aerospace": {"risk_multiplier": 1.5, "revenue_range": (10000000, 5000000000)},
            "Mining": {"risk_multiplier": 1.6, "revenue_range": (2000000, 8000000000)},
        }
        
        # Product categories with realistic characteristics
        self.product_categories = {
            "Semiconductors": {"base_price": 50, "volatility": 0.4, "criticality": 0.9},
            "Steel": {"base_price": 800, "volatility": 0.3, "criticality": 0.8},
            "Aluminum": {"base_price": 2500, "volatility": 0.25, "criticality": 0.7},
            "Copper": {"base_price": 9000, "volatility": 0.35, "criticality": 0.8},
            "Rare Earth Elements": {"base_price": 50000, "volatility": 0.6, "criticality": 0.9},
            "Pharmaceutical Ingredients": {"base_price": 1000, "volatility": 0.2, "criticality": 0.9},
            "Textiles": {"base_price": 5, "volatility": 0.15, "criticality": 0.5},
            "Electronics Components": {"base_price": 20, "volatility": 0.3, "criticality": 0.8},
            "Chemicals": {"base_price": 500, "volatility": 0.25, "criticality": 0.7},
            "Food Ingredients": {"base_price": 2, "volatility": 0.2, "criticality": 0.6},
        }
    
    def generate_countries(self, count: int = 195) -> List[Dict]:
        """Generate synthetic country data"""
        logger.info(f"Generating {count} countries...")
        
        countries = []
        country_codes = list(self.country_profiles.keys())
        
        for i in range(min(count, len(country_codes))):
            country_code = country_codes[i]
            profile = self.country_profiles[country_code]
            
            # Generate realistic risk scores with some randomness
            base_risk = profile["risk_base"]
            political_stability = max(0, min(100, (1 - base_risk) * 100 + np.random.normal(0, 10)))
            economic_freedom = max(0, min(100, (1 - base_risk) * 100 + np.random.normal(0, 15)))
            corruption_index = max(0, min(100, (1 - base_risk) * 100 + np.random.normal(0, 20)))
            
            # Calculate overall risk score
            risk_score = (
                base_risk * 0.4 + 
                (1 - political_stability/100) * 0.3 + 
                (1 - economic_freedom/100) * 0.2 + 
                (1 - corruption_index/100) * 0.1
            ) * 100
            
            country = {
                "country_code": country_code,
                "country_name": fake.country(),
                "region": profile["region"],
                "gdp_usd": int(profile["gdp"] * (1 + np.random.normal(0, 0.1))),
                "population": int(np.random.uniform(1000000, 1500000000)),
                "political_stability_index": political_stability,
                "economic_freedom_index": economic_freedom,
                "corruption_perception_index": corruption_index,
                "risk_score": risk_score
            }
            countries.append(country)
        
        return countries
    
    def generate_suppliers(self, count: int = 500000) -> List[Dict]:
        """Generate synthetic supplier data"""
        logger.info(f"Generating {count} suppliers...")
        
        suppliers = []
        industries = list(self.industries.keys())
        
        for i in range(count):
            industry = random.choice(industries)
            industry_profile = self.industries[industry]
            
            # Generate supplier characteristics
            tier = np.random.choice([1, 2, 3, 4, 5, 6], p=[0.05, 0.15, 0.25, 0.25, 0.20, 0.10])
            revenue = int(np.random.uniform(*industry_profile["revenue_range"]))
            
            # Calculate risk scores based on industry and tier
            base_risk = industry_profile["risk_multiplier"] * 0.3
            financial_health = max(0, min(100, 100 - base_risk * 100 + np.random.normal(0, 20)))
            cyber_risk = max(0, min(100, base_risk * 100 + np.random.normal(0, 15)))
            operational_risk = max(0, min(100, base_risk * 100 + np.random.normal(0, 25)))
            
            overall_risk = (
                (1 - financial_health/100) * 0.4 + 
                cyber_risk/100 * 0.3 + 
                operational_risk/100 * 0.3
            ) * 100
            
            supplier = {
                "supplier_id": f"SUP_{i:06d}",
                "name": fake.company(),
                "country_id": random.randint(1, len(self.country_profiles)),
                "industry": industry,
                "tier": tier,
                "annual_revenue": revenue,
                "employee_count": int(revenue / np.random.uniform(50000, 200000)),
                "financial_health_score": financial_health,
                "cyber_risk_score": cyber_risk,
                "operational_risk_score": operational_risk,
                "overall_risk_score": overall_risk,
                "is_active": random.choice([True, True, True, False])  # 75% active
            }
            suppliers.append(supplier)
        
        return suppliers
    
    def generate_products(self, count: int = 2800) -> List[Dict]:
        """Generate synthetic product data"""
        logger.info(f"Generating {count} products...")
        
        products = []
        categories = list(self.product_categories.keys())
        
        for i in range(count):
            category = random.choice(categories)
            category_profile = self.product_categories[category]
            
            # Generate product characteristics
            base_price = category_profile["base_price"] * (1 + np.random.normal(0, 0.2))
            volatility = category_profile["volatility"] * (1 + np.random.normal(0, 0.1))
            criticality = category_profile["criticality"] * (1 + np.random.normal(0, 0.1))
            
            product = {
                "product_code": f"PROD_{i:06d}",
                "name": f"{category} - {fake.word()}",
                "category": category,
                "subcategory": fake.word(),
                "unit": random.choice(["kg", "ton", "piece", "liter", "meter"]),
                "base_price_usd": base_price,
                "price_volatility": volatility,
                "criticality_score": criticality,
                "substitution_difficulty": np.random.uniform(0.1, 1.0)
            }
            products.append(product)
        
        return products
    
    def generate_trade_routes(self, count: int = 850) -> List[Dict]:
        """Generate synthetic trade route data"""
        logger.info(f"Generating {count} trade routes...")
        
        routes = []
        country_count = len(self.country_profiles)
        
        for i in range(count):
            origin_id = random.randint(1, country_count)
            destination_id = random.randint(1, country_count)
            
            # Avoid self-routes
            while destination_id == origin_id:
                destination_id = random.randint(1, country_count)
            
            route_type = random.choice(["sea", "air", "land"])
            
            # Generate realistic route characteristics
            if route_type == "sea":
                distance = np.random.uniform(1000, 20000)
                transit_time = int(distance / np.random.uniform(200, 500))
                cost_per_ton = np.random.uniform(50, 300)
            elif route_type == "air":
                distance = np.random.uniform(500, 15000)
                transit_time = int(distance / np.random.uniform(800, 1200))
                cost_per_ton = np.random.uniform(2000, 8000)
            else:  # land
                distance = np.random.uniform(100, 5000)
                transit_time = int(distance / np.random.uniform(50, 150))
                cost_per_ton = np.random.uniform(100, 800)
            
            # Calculate vulnerability based on route characteristics
            vulnerability = (
                (distance / 20000) * 0.3 +  # Longer routes more vulnerable
                (cost_per_ton / 8000) * 0.2 +  # Higher cost routes more vulnerable
                np.random.uniform(0, 0.5)  # Random factor
            )
            
            chokepoint_risk = np.random.uniform(0, 1.0) if route_type == "sea" else np.random.uniform(0, 0.3)
            
            route = {
                "route_id": f"ROUTE_{i:06d}",
                "origin_country_id": origin_id,
                "destination_country_id": destination_id,
                "route_type": route_type,
                "distance_km": distance,
                "transit_time_days": transit_time,
                "cost_per_ton": cost_per_ton,
                "capacity_utilization": np.random.uniform(0.3, 0.95),
                "vulnerability_score": vulnerability * 100,
                "chokepoint_risk": chokepoint_risk * 100,
                "is_active": random.choice([True, True, True, False])
            }
            routes.append(route)
        
        return routes
    
    def generate_companies(self, count: int = 500) -> List[Dict]:
        """Generate Fortune 500 company data"""
        logger.info(f"Generating {count} companies...")
        
        companies = []
        sectors = ["Technology", "Healthcare", "Financial", "Energy", "Consumer", "Industrial", "Materials"]
        
        for i in range(count):
            sector = random.choice(sectors)
            revenue = int(np.random.uniform(10000000000, 500000000000))  # 10B to 500B
            
            company = {
                "company_id": f"COMP_{i:06d}",
                "name": fake.company(),
                "ticker": fake.lexify(text="????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                "sector": sector,
                "industry": fake.word(),
                "revenue_usd": revenue,
                "market_cap_usd": int(revenue * np.random.uniform(0.5, 3.0)),
                "employee_count": int(revenue / np.random.uniform(200000, 500000)),
                "headquarters_country_id": random.randint(1, len(self.country_profiles)),
                "supply_chain_risk_score": np.random.uniform(0, 100)
            }
            companies.append(company)
        
        return companies
    
    def generate_risk_events(self, count: int = 1000) -> List[Dict]:
        """Generate synthetic risk events"""
        logger.info(f"Generating {count} risk events...")
        
        events = []
        event_types = ["geopolitical", "economic", "cyber", "regulatory", "environmental", "supply_chain"]
        
        for i in range(count):
            event_type = random.choice(event_types)
            severity = np.random.uniform(10, 90)
            
            # Generate realistic event descriptions
            event_templates = {
                "geopolitical": [
                    "Trade tensions escalate between {country} and major trading partners",
                    "Political instability in {country} affects business operations",
                    "New sanctions imposed on {country} by international community"
                ],
                "economic": [
                    "Currency devaluation in {country} impacts trade flows",
                    "Economic recession in {country} reduces demand",
                    "Inflation surge in {country} increases operational costs"
                ],
                "cyber": [
                    "Major cyber attack targets supply chain systems in {country}",
                    "Data breach affects multiple suppliers in {country}",
                    "Ransomware attack disrupts logistics operations in {country}"
                ]
            }
            
            templates = event_templates.get(event_type, ["Risk event detected in {country}"])
            description = random.choice(templates).format(country=fake.country())
            
            event = {
                "event_id": f"EVENT_{i:06d}",
                "country_id": random.randint(1, len(self.country_profiles)),
                "event_type": event_type,
                "severity": severity,
                "title": f"{event_type.title()} Risk Event",
                "description": description,
                "source": random.choice(["Reuters", "Bloomberg", "Internal", "Government"]),
                "impact_score": severity * np.random.uniform(0.5, 1.5),
                "confidence_score": np.random.uniform(0.3, 0.9),
                "event_date": fake.date_between(start_date="-1y", end_date="today"),
                "is_active": random.choice([True, True, False])
            }
            events.append(event)
        
        return events
    
    def generate_all_data(self):
        """Generate all synthetic data"""
        logger.info("Starting comprehensive data generation...")
        
        # Generate core entities
        self.countries_data = self.generate_countries()
        self.suppliers_data = self.generate_suppliers()
        self.products_data = self.generate_products()
        self.trade_routes_data = self.generate_trade_routes()
        self.companies_data = self.generate_companies()
        self.risk_events_data = self.generate_risk_events()
        
        logger.info("Data generation completed successfully")
        
        return {
            "countries": self.countries_data,
            "suppliers": self.suppliers_data,
            "products": self.products_data,
            "trade_routes": self.trade_routes_data,
            "companies": self.companies_data,
            "risk_events": self.risk_events_data
        }
    
    def save_to_database(self, data: Dict):
        """Save generated data to database"""
        logger.info("Saving data to database...")
        
        with db_manager.get_session() as session:
            try:
                # Save countries
                for country_data in data["countries"]:
                    country = Country(**country_data)
                    session.add(country)
                
                # Save suppliers
                for supplier_data in data["suppliers"]:
                    supplier = Supplier(**supplier_data)
                    session.add(supplier)
                
                # Save products
                for product_data in data["products"]:
                    product = Product(**product_data)
                    session.add(product)
                
                # Save trade routes
                for route_data in data["trade_routes"]:
                    route = TradeRoute(**route_data)
                    session.add(route)
                
                # Save companies
                for company_data in data["companies"]:
                    company = Company(**company_data)
                    session.add(company)
                
                # Save risk events
                for event_data in data["risk_events"]:
                    event = RiskEvent(**event_data)
                    session.add(event)
                
                session.commit()
                logger.info("Data saved to database successfully")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to save data to database: {e}")
                raise
    
    def save_to_files(self, data: Dict, output_dir: str = "data/synthetic"):
        """Save generated data to CSV files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Saving data to files in {output_dir}...")
        
        for entity_name, entity_data in data.items():
            if entity_data:
                df = pd.DataFrame(entity_data)
                file_path = os.path.join(output_dir, f"{entity_name}.csv")
                df.to_csv(file_path, index=False)
                logger.info(f"Saved {len(entity_data)} {entity_name} to {file_path}")

# Main execution function
def generate_sentinel_data():
    """Main function to generate all SENTINEL data"""
    generator = SyntheticDataGenerator()
    
    # Generate all data
    data = generator.generate_all_data()
    
    # Save to files
    generator.save_to_files(data)
    
    # Save to database (if available)
    try:
        generator.save_to_database(data)
    except Exception as e:
        logger.warning(f"Could not save to database: {e}")
    
    return data

if __name__ == "__main__":
    generate_sentinel_data() 