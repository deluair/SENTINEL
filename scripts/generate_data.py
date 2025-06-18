"""
SENTINEL Data Generation Script
Generate and populate synthetic data for the system
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from data.synthetic_data_generator import SyntheticDataGenerator
from models.database_connection import db_manager
from models.database import Country, Supplier, Product, TradeRoute, Company, RiskEvent
from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_and_save_data():
    """Generate synthetic data and save to database"""
    try:
        logger.info("Starting synthetic data generation...")
        
        # Initialize data generator
        generator = SyntheticDataGenerator()
        
        # Generate all data
        data = generator.generate_all_data()
        
        logger.info("Data generation completed. Saving to database...")
        
        # Save to database
        with db_manager.get_session() as session:
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
        
        logger.info("Data saved to database successfully!")
        
        # Print summary
        print_data_summary(data)
        
        return True
        
    except Exception as e:
        logger.error(f"Data generation failed: {e}")
        return False

def print_data_summary(data):
    """Print summary of generated data"""
    logger.info("=== DATA GENERATION SUMMARY ===")
    logger.info(f"Countries: {len(data['countries'])}")
    logger.info(f"Suppliers: {len(data['suppliers'])}")
    logger.info(f"Products: {len(data['products'])}")
    logger.info(f"Trade Routes: {len(data['trade_routes'])}")
    logger.info(f"Companies: {len(data['companies'])}")
    logger.info(f"Risk Events: {len(data['risk_events'])}")
    logger.info("================================")

def generate_sample_data():
    """Generate a smaller sample dataset for testing"""
    try:
        logger.info("Generating sample data...")
        
        # Initialize data generator
        generator = SyntheticDataGenerator()
        
        # Generate smaller datasets
        sample_data = {
            "countries": generator.generate_countries(50),
            "suppliers": generator.generate_suppliers(1000),
            "products": generator.generate_products(500),
            "trade_routes": generator.generate_trade_routes(200),
            "companies": generator.generate_companies(100),
            "risk_events": generator.generate_risk_events(200)
        }
        
        logger.info("Sample data generation completed. Saving to database...")
        
        # Save to database
        with db_manager.get_session() as session:
            # Save countries
            for country_data in sample_data["countries"]:
                country = Country(**country_data)
                session.add(country)
            
            # Save suppliers
            for supplier_data in sample_data["suppliers"]:
                supplier = Supplier(**supplier_data)
                session.add(supplier)
            
            # Save products
            for product_data in sample_data["products"]:
                product = Product(**product_data)
                session.add(product)
            
            # Save trade routes
            for route_data in sample_data["trade_routes"]:
                route = TradeRoute(**route_data)
                session.add(route)
            
            # Save companies
            for company_data in sample_data["companies"]:
                company = Company(**company_data)
                session.add(company)
            
            # Save risk events
            for event_data in sample_data["risk_events"]:
                event = RiskEvent(**event_data)
                session.add(event)
            
            session.commit()
        
        logger.info("Sample data saved to database successfully!")
        print_data_summary(sample_data)
        
        return True
        
    except Exception as e:
        logger.error(f"Sample data generation failed: {e}")
        return False

def clear_existing_data():
    """Clear all existing data from database"""
    try:
        logger.info("Clearing existing data...")
        
        with db_manager.get_session() as session:
            # Delete in reverse order of dependencies
            session.query(RiskEvent).delete()
            session.query(Company).delete()
            session.query(TradeRoute).delete()
            session.query(Product).delete()
            session.query(Supplier).delete()
            session.query(Country).delete()
            
            session.commit()
        
        logger.info("Existing data cleared successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to clear existing data: {e}")
        return False

def check_data_status():
    """Check current data status in database"""
    try:
        logger.info("Checking data status...")
        
        with db_manager.get_session() as session:
            tables = {
                "countries": Country,
                "suppliers": Supplier,
                "products": Product,
                "trade_routes": TradeRoute,
                "companies": Company,
                "risk_events": RiskEvent
            }
            
            for table_name, model in tables.items():
                count = session.query(model).count()
                logger.info(f"{table_name}: {count} records")
        
        return True
        
    except Exception as e:
        logger.error(f"Data status check failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SENTINEL Data Generation")
    parser.add_argument("--sample", action="store_true", help="Generate sample data only")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before generation")
    parser.add_argument("--status", action="store_true", help="Check current data status")
    
    args = parser.parse_args()
    
    if args.status:
        if check_data_status():
            logger.info("Data status check completed!")
        else:
            logger.error("Data status check failed!")
            sys.exit(1)
    else:
        # Clear data if requested
        if args.clear:
            if not clear_existing_data():
                logger.error("Failed to clear existing data!")
                sys.exit(1)
        
        # Generate data
        if args.sample:
            if generate_sample_data():
                logger.info("Sample data generation completed successfully!")
            else:
                logger.error("Sample data generation failed!")
                sys.exit(1)
        else:
            if generate_and_save_data():
                logger.info("Data generation completed successfully!")
            else:
                logger.error("Data generation failed!")
                sys.exit(1) 