#!/usr/bin/env python3
"""
SENTINEL Quick Start Script
Automated setup and launch for the Geopolitical Trade Risk Navigator
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description, check=True):
    """Run a shell command with logging"""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            logger.info(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running '{description}': {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        return False

def check_docker():
    """Check if Docker is available"""
    logger.info("Checking Docker installation...")
    return run_command("docker --version", "Docker version check", check=False)

def check_docker_compose():
    """Check if Docker Compose is available"""
    logger.info("Checking Docker Compose installation...")
    return run_command("docker-compose --version", "Docker Compose version check", check=False)

def start_services():
    """Start all SENTINEL services using Docker Compose"""
    logger.info("Starting SENTINEL services...")
    
    # Build and start services
    if not run_command("docker-compose up -d --build", "Starting services"):
        logger.error("Failed to start services")
        return False
    
    # Wait for services to be ready
    logger.info("Waiting for services to be ready...")
    time.sleep(30)
    
    return True

def generate_sample_data():
    """Generate sample data for the system"""
    logger.info("Generating sample data...")
    
    # Wait a bit more for database to be fully ready
    time.sleep(10)
    
    if not run_command(
        "docker-compose exec -T sentinel_api python scripts/generate_data.py --sample",
        "Generating sample data"
    ):
        logger.error("Failed to generate sample data")
        return False
    
    return True

def check_services():
    """Check if all services are running"""
    logger.info("Checking service status...")
    
    services = ["sentinel_postgres", "sentinel_redis", "sentinel_api", "sentinel_dashboard"]
    
    for service in services:
        if not run_command(f"docker-compose ps {service}", f"Checking {service}", check=False):
            logger.warning(f"Service {service} may not be running properly")
    
    return True

def print_access_info():
    """Print access information"""
    print("\n" + "="*60)
    print("🎯 SENTINEL - Fortune 500 Geopolitical Trade Risk Navigator")
    print("="*60)
    print("\n📊 Access Information:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Interactive Dashboard: http://localhost:8050")
    print("   • API Health Check: http://localhost:8000/health")
    print("   • Dashboard Health: http://localhost:8050")
    
    print("\n🔧 Management Commands:")
    print("   • View logs: docker-compose logs -f")
    print("   • Stop services: docker-compose down")
    print("   • Restart services: docker-compose restart")
    print("   • Generate more data: docker-compose exec sentinel_api python scripts/generate_data.py --sample")
    
    print("\n📈 Sample API Endpoints:")
    print("   • Dashboard summary: http://localhost:8000/api/v1/dashboard-summary")
    print("   • Countries list: http://localhost:8000/api/v1/countries")
    print("   • Risk alerts: http://localhost:8000/api/v1/risk-alerts")
    print("   • High-risk countries: http://localhost:8000/api/v1/countries/high-risk/list")
    
    print("\n🚀 Quick Start Complete!")
    print("   Open your browser and navigate to http://localhost:8050")
    print("   to start exploring the SENTINEL dashboard.")
    print("="*60)

def main():
    """Main quick start function"""
    print("🚀 SENTINEL Quick Start")
    print("Fortune 500 Geopolitical Trade Risk Navigator")
    print("="*50)
    
    # Check prerequisites
    logger.info("Checking prerequisites...")
    
    if not check_docker():
        logger.error("Docker is not installed or not accessible")
        print("\n❌ Please install Docker first:")
        print("   https://docs.docker.com/get-docker/")
        return False
    
    if not check_docker_compose():
        logger.error("Docker Compose is not installed or not accessible")
        print("\n❌ Please install Docker Compose first:")
        print("   https://docs.docker.com/compose/install/")
        return False
    
    # Check if docker-compose.yml exists
    if not Path("docker-compose.yml").exists():
        logger.error("docker-compose.yml not found in current directory")
        print("\n❌ Please run this script from the SENTINEL project root directory")
        return False
    
    # Start services
    if not start_services():
        logger.error("Failed to start services")
        return False
    
    # Generate sample data
    if not generate_sample_data():
        logger.warning("Failed to generate sample data - you can try manually later")
    
    # Check service status
    check_services()
    
    # Print access information
    print_access_info()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        print("\n⚠️  Setup was interrupted. You can run this script again to continue.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error occurred: {e}")
        sys.exit(1) 