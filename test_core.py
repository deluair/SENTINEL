#!/usr/bin/env python3
"""
SENTINEL Core Functionality Test
Tests the basic functionality without external dependencies
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_imports():
    """Test that core modules can be imported"""
    print("Testing core imports...")
    
    try:
        # Test config import
        from config.settings import settings
        print("✅ Config settings imported successfully")
        
        # Test data generator import
        from data.synthetic_data_generator import SyntheticDataGenerator
        print("✅ Data generator imported successfully")
        
        # Test risk scoring import
        from models.risk_scoring import IScoreEngine
        print("✅ Risk scoring engine imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_generation():
    """Test synthetic data generation"""
    print("\nTesting data generation...")
    
    try:
        from data.synthetic_data_generator import SyntheticDataGenerator
        
        # Create generator
        generator = SyntheticDataGenerator()
        print("✅ Data generator created successfully")
        
        # Generate sample data
        sample_countries = generator.generate_countries(5)
        print(f"✅ Generated {len(sample_countries)} sample countries")
        
        sample_suppliers = generator.generate_suppliers(10)
        print(f"✅ Generated {len(sample_suppliers)} sample suppliers")
        
        sample_products = generator.generate_products(5)
        print(f"✅ Generated {len(sample_products)} sample products")
        
        return True
    except Exception as e:
        print(f"❌ Data generation error: {e}")
        return False

def test_risk_scoring():
    """Test risk scoring functionality"""
    print("\nTesting risk scoring...")
    
    try:
        from models.risk_scoring import IScoreEngine
        
        # Create engine
        engine = IScoreEngine()
        print("✅ Risk scoring engine created successfully")
        
        # Test country risk calculation
        country_data = {
            'political_stability_index': 75.0,
            'economic_freedom_index': 80.0,
            'corruption_perception_index': 70.0,
            'gdp_usd': 2000000000000,
            'population': 100000000
        }
        
        risk_score = engine.calculate_country_risk_score(country_data)
        print(f"✅ Country risk score calculated: {risk_score:.2f}")
        
        # Test supplier risk calculation
        supplier_data = {
            'financial_health_score': 85.0,
            'cyber_risk_score': 30.0,
            'operational_risk_score': 40.0,
            'tier': 2,
            'annual_revenue': 50000000
        }
        
        supplier_risks = engine.calculate_supplier_risk_score(supplier_data, 25.0)
        print(f"✅ Supplier risk scores calculated: {supplier_risks['overall_risk']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Risk scoring error: {e}")
        return False

def test_api_structure():
    """Test API structure"""
    print("\nTesting API structure...")
    
    try:
        # Test API main import
        from api.main import app
        print("✅ FastAPI app created successfully")
        
        # Check if app has expected attributes
        if hasattr(app, 'routes'):
            print("✅ API has routes configured")
        
        return True
    except Exception as e:
        print(f"❌ API structure error: {e}")
        return False

def test_dashboard_structure():
    """Test dashboard structure"""
    print("\nTesting dashboard structure...")
    
    try:
        # Test dashboard import
        from dashboard.app import app
        print("✅ Dash app created successfully")
        
        # Check if app has expected attributes
        if hasattr(app, 'layout'):
            print("✅ Dashboard has layout configured")
        
        return True
    except Exception as e:
        print(f"❌ Dashboard structure error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 SENTINEL Core Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Core Imports", test_imports),
        ("Data Generation", test_data_generation),
        ("Risk Scoring", test_risk_scoring),
        ("API Structure", test_api_structure),
        ("Dashboard Structure", test_dashboard_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SENTINEL core functionality is working.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 