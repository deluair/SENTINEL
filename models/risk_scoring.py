"""
SENTINEL i-Score Risk Scoring Engine
Implements the proprietary i-Score methodology for geopolitical trade risk assessment
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import json

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IScoreEngine:
    """
    i-Score Risk Scoring Engine
    Proprietary methodology for quantifying geopolitical trade risk
    """
    
    def __init__(self):
        self.weights = settings.RISK_SCORE_WEIGHTS
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        
    def calculate_country_risk_score(self, country_data: Dict) -> float:
        """
        Calculate comprehensive country risk score using i-Score methodology
        
        Args:
            country_data: Dictionary containing country metrics
            
        Returns:
            float: Risk score (0-100, higher = more risky)
        """
        try:
            # Extract risk factors
            political_stability = country_data.get('political_stability_index', 50) / 100
            economic_freedom = country_data.get('economic_freedom_index', 50) / 100
            corruption_index = country_data.get('corruption_perception_index', 50) / 100
            gdp_per_capita = country_data.get('gdp_usd', 0) / max(country_data.get('population', 1), 1)
            
            # Normalize GDP per capita (log scale for better distribution)
            gdp_per_capita_normalized = np.log1p(gdp_per_capita) / np.log1p(100000)
            
            # Calculate individual risk components
            political_risk = (1 - political_stability) * self.weights['geopolitical']
            economic_risk = (1 - economic_freedom) * self.weights['economic']
            corruption_risk = (1 - corruption_index) * self.weights['regulatory']
            development_risk = (1 - gdp_per_capita_normalized) * self.weights['economic']
            
            # Combine into overall risk score
            total_risk = (political_risk + economic_risk + corruption_risk + development_risk) * 100
            
            # Apply sigmoid function for smooth scaling
            risk_score = 100 / (1 + np.exp(-(total_risk - 50) / 10))
            
            return min(100, max(0, risk_score))
            
        except Exception as e:
            logger.error(f"Error calculating country risk score: {e}")
            return 50.0  # Default neutral score
    
    def calculate_supplier_risk_score(self, supplier_data: Dict, country_risk: float) -> Dict[str, float]:
        """
        Calculate comprehensive supplier risk score
        
        Args:
            supplier_data: Dictionary containing supplier metrics
            country_risk: Country risk score (0-100)
            
        Returns:
            Dict: Risk scores for different categories
        """
        try:
            # Extract supplier metrics
            financial_health = supplier_data.get('financial_health_score', 50) / 100
            cyber_risk = supplier_data.get('cyber_risk_score', 50) / 100
            operational_risk = supplier_data.get('operational_risk_score', 50) / 100
            tier = supplier_data.get('tier', 1)
            revenue = supplier_data.get('annual_revenue', 1000000)
            
            # Normalize revenue (log scale)
            revenue_normalized = np.log1p(revenue) / np.log1p(1000000000)
            
            # Calculate tier risk (higher tiers = higher risk)
            tier_risk = (tier - 1) / 5 * 0.3
            
            # Calculate country-adjusted risk
            country_risk_normalized = country_risk / 100
            
            # Calculate individual risk components
            financial_risk = (1 - financial_health) * 0.4
            cyber_risk_score = cyber_risk * 0.3
            operational_risk_score = operational_risk * 0.3
            
            # Combine with country and tier risk
            overall_risk = (
                financial_risk * 0.3 +
                cyber_risk_score * 0.2 +
                operational_risk_score * 0.2 +
                country_risk_normalized * 0.2 +
                tier_risk * 0.1
            ) * 100
            
            return {
                'financial_risk': financial_risk * 100,
                'cyber_risk': cyber_risk_score * 100,
                'operational_risk': operational_risk_score * 100,
                'country_risk': country_risk,
                'tier_risk': tier_risk * 100,
                'overall_risk': min(100, max(0, overall_risk))
            }
            
        except Exception as e:
            logger.error(f"Error calculating supplier risk score: {e}")
            return {
                'financial_risk': 50.0,
                'cyber_risk': 50.0,
                'operational_risk': 50.0,
                'country_risk': country_risk,
                'tier_risk': 20.0,
                'overall_risk': 50.0
            }
    
    def calculate_trade_route_risk_score(self, route_data: Dict, origin_risk: float, dest_risk: float) -> float:
        """
        Calculate trade route vulnerability score
        
        Args:
            route_data: Dictionary containing route metrics
            origin_risk: Origin country risk score
            dest_risk: Destination country risk score
            
        Returns:
            float: Route vulnerability score (0-100)
        """
        try:
            # Extract route metrics
            distance = route_data.get('distance_km', 1000)
            transit_time = route_data.get('transit_time_days', 10)
            cost_per_ton = route_data.get('cost_per_ton', 500)
            route_type = route_data.get('route_type', 'sea')
            chokepoint_risk = route_data.get('chokepoint_risk', 0) / 100
            
            # Normalize metrics
            distance_normalized = min(1.0, distance / 20000)
            transit_normalized = min(1.0, transit_time / 30)
            cost_normalized = min(1.0, cost_per_ton / 8000)
            
            # Route type risk multipliers
            type_multipliers = {
                'sea': 1.2,  # Sea routes more vulnerable
                'air': 0.8,  # Air routes less vulnerable
                'land': 1.0   # Land routes neutral
            }
            type_multiplier = type_multipliers.get(route_type, 1.0)
            
            # Calculate route-specific risks
            distance_risk = distance_normalized * 0.2
            transit_risk = transit_normalized * 0.15
            cost_risk = cost_normalized * 0.1
            chokepoint_risk_score = chokepoint_risk * 0.25
            
            # Country risk contribution
            country_risk = (origin_risk + dest_risk) / 200 * 0.3
            
            # Combine all factors
            total_risk = (
                distance_risk +
                transit_risk +
                cost_risk +
                chokepoint_risk_score +
                country_risk
            ) * type_multiplier * 100
            
            return min(100, max(0, total_risk))
            
        except Exception as e:
            logger.error(f"Error calculating trade route risk score: {e}")
            return 50.0
    
    def calculate_product_risk_score(self, product_data: Dict, market_conditions: Dict) -> float:
        """
        Calculate product-specific risk score
        
        Args:
            product_data: Dictionary containing product metrics
            market_conditions: Current market conditions
            
        Returns:
            float: Product risk score (0-100)
        """
        try:
            # Extract product metrics
            criticality = product_data.get('criticality_score', 0.5)
            volatility = product_data.get('price_volatility', 0.2)
            substitution_difficulty = product_data.get('substitution_difficulty', 0.5)
            base_price = product_data.get('base_price_usd', 100)
            
            # Normalize price
            price_normalized = np.log1p(base_price) / np.log1p(100000)
            
            # Market condition factors
            market_volatility = market_conditions.get('overall_volatility', 0.2)
            supply_demand_imbalance = market_conditions.get('supply_demand_imbalance', 0.0)
            
            # Calculate risk components
            criticality_risk = criticality * 0.4
            volatility_risk = (volatility + market_volatility) * 0.3
            substitution_risk = substitution_difficulty * 0.2
            price_risk = price_normalized * 0.1
            
            # Combine into total risk
            total_risk = (
                criticality_risk +
                volatility_risk +
                substitution_risk +
                price_risk
            ) * 100
            
            # Adjust for supply-demand imbalance
            if supply_demand_imbalance > 0:
                total_risk *= (1 + supply_demand_imbalance)
            
            return min(100, max(0, total_risk))
            
        except Exception as e:
            logger.error(f"Error calculating product risk score: {e}")
            return 50.0
    
    def calculate_company_supply_chain_risk(self, company_data: Dict, 
                                          suppliers: List[Dict],
                                          routes: List[Dict],
                                          products: List[Dict]) -> Dict[str, float]:
        """
        Calculate comprehensive supply chain risk for a company
        
        Args:
            company_data: Company information
            suppliers: List of supplier data
            routes: List of trade route data
            products: List of product data
            
        Returns:
            Dict: Comprehensive risk assessment
        """
        try:
            # Calculate supplier concentration risk
            supplier_risks = [s.get('overall_risk_score', 50) for s in suppliers]
            supplier_concentration = len(suppliers) / 1000  # Normalize by expected supplier count
            
            # Calculate route vulnerability
            route_risks = [r.get('vulnerability_score', 50) for r in routes]
            
            # Calculate product criticality
            product_risks = [p.get('criticality_score', 0.5) * 100 for p in products]
            
            # Calculate risk metrics
            avg_supplier_risk = np.mean(supplier_risks) if supplier_risks else 50
            avg_route_risk = np.mean(route_risks) if route_risks else 50
            avg_product_risk = np.mean(product_risks) if product_risks else 50
            
            # Concentration risk (fewer suppliers = higher risk)
            concentration_risk = max(0, (1 - supplier_concentration) * 100)
            
            # Geographic concentration risk
            supplier_countries = set(s.get('country_id') for s in suppliers)
            geographic_concentration = max(0, (1 - len(supplier_countries) / 20) * 100)
            
            # Calculate overall supply chain risk
            overall_risk = (
                avg_supplier_risk * 0.3 +
                avg_route_risk * 0.25 +
                avg_product_risk * 0.2 +
                concentration_risk * 0.15 +
                geographic_concentration * 0.1
            )
            
            return {
                'supplier_risk': avg_supplier_risk,
                'route_risk': avg_route_risk,
                'product_risk': avg_product_risk,
                'concentration_risk': concentration_risk,
                'geographic_concentration': geographic_concentration,
                'overall_supply_chain_risk': min(100, max(0, overall_risk))
            }
            
        except Exception as e:
            logger.error(f"Error calculating company supply chain risk: {e}")
            return {
                'supplier_risk': 50.0,
                'route_risk': 50.0,
                'product_risk': 50.0,
                'concentration_risk': 50.0,
                'geographic_concentration': 50.0,
                'overall_supply_chain_risk': 50.0
            }
    
    def train_predictive_models(self, historical_data: pd.DataFrame):
        """
        Train machine learning models for risk prediction
        
        Args:
            historical_data: Historical risk data with features and targets
        """
        try:
            # Prepare features and targets
            feature_columns = [
                'political_stability', 'economic_freedom', 'corruption_index',
                'gdp_per_capita', 'trade_volume', 'tariff_rate', 'cyber_incidents'
            ]
            
            target_column = 'risk_score'
            
            # Filter data with required columns
            available_features = [col for col in feature_columns if col in historical_data.columns]
            if not available_features:
                logger.warning("No suitable features found for model training")
                return
            
            X = historical_data[available_features].fillna(0)
            y = historical_data[target_column].fillna(50)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train Random Forest model
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X_train, y_train)
            
            # Train Gradient Boosting model
            gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            gb_model.fit(X_train, y_train)
            
            # Store models
            self.models['random_forest'] = rf_model
            self.models['gradient_boosting'] = gb_model
            
            # Store feature importance
            self.feature_importance = dict(zip(available_features, rf_model.feature_importances_))
            
            # Evaluate models
            rf_score = rf_model.score(X_test, y_test)
            gb_score = gb_model.score(X_test, y_test)
            
            logger.info(f"Model training completed - RF R²: {rf_score:.3f}, GB R²: {gb_score:.3f}")
            
        except Exception as e:
            logger.error(f"Error training predictive models: {e}")
    
    def predict_risk_score(self, features: Dict) -> float:
        """
        Predict risk score using trained models
        
        Args:
            features: Dictionary of feature values
            
        Returns:
            float: Predicted risk score
        """
        try:
            if not self.models:
                logger.warning("No trained models available for prediction")
                return 50.0
            
            # Prepare feature vector
            feature_vector = []
            feature_names = list(self.feature_importance.keys())
            
            for feature in feature_names:
                feature_vector.append(features.get(feature, 0))
            
            # Make prediction using ensemble
            predictions = []
            for model_name, model in self.models.items():
                pred = model.predict([feature_vector])[0]
                predictions.append(pred)
            
            # Return ensemble average
            return np.mean(predictions)
            
        except Exception as e:
            logger.error(f"Error predicting risk score: {e}")
            return 50.0
    
    def save_models(self, filepath: str):
        """Save trained models to disk"""
        try:
            model_data = {
                'models': self.models,
                'feature_importance': self.feature_importance,
                'weights': self.weights
            }
            joblib.dump(model_data, filepath)
            logger.info(f"Models saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self, filepath: str):
        """Load trained models from disk"""
        try:
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.feature_importance = model_data['feature_importance']
            self.weights = model_data.get('weights', self.weights)
            logger.info(f"Models loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")

# Global i-Score engine instance
i_score_engine = IScoreEngine() 