"""
SENTINEL Database Setup Script
Initialize database tables and basic configuration
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from models.database_connection import db_manager
from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Set up the SENTINEL database"""
    try:
        logger.info("Starting database setup...")
        
        # Test database connection
        if not db_manager.test_connection():
            logger.error("Database connection failed. Please check your configuration.")
            return False
        
        # Create tables
        logger.info("Creating database tables...")
        db_manager.create_tables()
        
        logger.info("Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def reset_database():
    """Reset the database (drop and recreate all tables)"""
    try:
        logger.info("Resetting database...")
        
        # Drop all tables
        db_manager.drop_tables()
        logger.info("All tables dropped.")
        
        # Create tables
        db_manager.create_tables()
        logger.info("Tables recreated successfully.")
        
        return True
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False

def check_database_status():
    """Check database status and table counts"""
    try:
        logger.info("Checking database status...")
        
        with db_manager.get_session() as session:
            # Check if tables exist and get counts
            from models.database import Country, Supplier, Product, TradeRoute, Company, RiskEvent
            
            tables = {
                "countries": Country,
                "suppliers": Supplier,
                "products": Product,
                "trade_routes": TradeRoute,
                "companies": Company,
                "risk_events": RiskEvent
            }
            
            for table_name, model in tables.items():
                try:
                    count = session.query(model).count()
                    logger.info(f"{table_name}: {count} records")
                except Exception as e:
                    logger.warning(f"Could not count {table_name}: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SENTINEL Database Setup")
    parser.add_argument("--reset", action="store_true", help="Reset database (drop and recreate)")
    parser.add_argument("--status", action="store_true", help="Check database status")
    
    args = parser.parse_args()
    
    if args.reset:
        if reset_database():
            logger.info("Database reset completed successfully!")
        else:
            logger.error("Database reset failed!")
            sys.exit(1)
    elif args.status:
        if check_database_status():
            logger.info("Database status check completed!")
        else:
            logger.error("Database status check failed!")
            sys.exit(1)
    else:
        if setup_database():
            logger.info("Database setup completed successfully!")
        else:
            logger.error("Database setup failed!")
            sys.exit(1) 