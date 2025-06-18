"""
SENTINEL Database Models
SQLAlchemy models for the Geopolitical Trade Risk Navigator
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, 
    ForeignKey, JSON, Index, BigInteger, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class Country(Base):
    """Country information and risk metrics"""
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(3), unique=True, index=True, nullable=False)
    country_name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    gdp_usd = Column(BigInteger)
    population = Column(BigInteger)
    political_stability_index = Column(Float)
    economic_freedom_index = Column(Float)
    corruption_perception_index = Column(Float)
    risk_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=func.now())
    
    # Relationships
    suppliers = relationship("Supplier", back_populates="country")
    trade_routes = relationship("TradeRoute", foreign_keys="[TradeRoute.origin_country_id]", back_populates="origin_country")
    risk_events = relationship("RiskEvent", back_populates="country")

class Supplier(Base):
    """Supplier information and financial health"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"))
    industry = Column(String(100))
    tier = Column(Integer, default=1)  # 1-6 tier system
    annual_revenue = Column(BigInteger)
    employee_count = Column(Integer)
    financial_health_score = Column(Float, default=0.0)
    cyber_risk_score = Column(Float, default=0.0)
    operational_risk_score = Column(Float, default=0.0)
    overall_risk_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_updated = Column(DateTime, default=func.now())
    
    # Relationships
    country = relationship("Country", back_populates="suppliers")
    products = relationship("SupplierProduct", back_populates="supplier")
    relationships = relationship("SupplierRelationship", foreign_keys="[SupplierRelationship.supplier_id]", back_populates="supplier")

class Product(Base):
    """Product information and commodity data"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(100))
    subcategory = Column(String(100))
    unit = Column(String(20))
    base_price_usd = Column(Float)
    price_volatility = Column(Float, default=0.0)
    criticality_score = Column(Float, default=0.0)
    substitution_difficulty = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    suppliers = relationship("SupplierProduct", back_populates="product")
    trade_flows = relationship("TradeFlow", back_populates="product")

class SupplierProduct(Base):
    """Many-to-many relationship between suppliers and products"""
    __tablename__ = "supplier_products"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    capacity = Column(Float)
    lead_time_days = Column(Integer)
    cost_usd = Column(Float)
    quality_score = Column(Float, default=0.0)
    reliability_score = Column(Float, default=0.0)
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    product = relationship("Product", back_populates="suppliers")

class TradeRoute(Base):
    """Trade route information and vulnerability data"""
    __tablename__ = "trade_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String(50), unique=True, index=True, nullable=False)
    origin_country_id = Column(Integer, ForeignKey("countries.id"))
    destination_country_id = Column(Integer, ForeignKey("countries.id"))
    route_type = Column(String(20))  # sea, air, land
    distance_km = Column(Float)
    transit_time_days = Column(Integer)
    cost_per_ton = Column(Float)
    capacity_utilization = Column(Float, default=0.0)
    vulnerability_score = Column(Float, default=0.0)
    chokepoint_risk = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    origin_country = relationship("Country", foreign_keys=[origin_country_id], back_populates="trade_routes")
    trade_flows = relationship("TradeFlow", back_populates="route")

class TradeFlow(Base):
    """Trade flow data and volume metrics"""
    __tablename__ = "trade_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("trade_routes.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    date = Column(Date, nullable=False)
    volume = Column(Float)
    value_usd = Column(BigInteger)
    tariff_rate = Column(Float, default=0.0)
    disruption_level = Column(Float, default=0.0)
    
    # Relationships
    route = relationship("TradeRoute", back_populates="trade_flows")
    product = relationship("Product", back_populates="trade_flows")

class SupplierRelationship(Base):
    """Supplier relationship network"""
    __tablename__ = "supplier_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    related_supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    relationship_type = Column(String(50))  # parent, subsidiary, partner
    dependency_level = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    supplier = relationship("Supplier", foreign_keys=[supplier_id], back_populates="relationships")

class RiskEvent(Base):
    """Risk events and incidents"""
    __tablename__ = "risk_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True, nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"))
    event_type = Column(String(50))  # geopolitical, economic, cyber, etc.
    severity = Column(Float, default=0.0)  # 0-100 scale
    title = Column(String(200), nullable=False)
    description = Column(Text)
    source = Column(String(100))
    impact_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    event_date = Column(DateTime)
    detected_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    country = relationship("Country", back_populates="risk_events")

class RiskScore(Base):
    """Historical risk scores for tracking"""
    __tablename__ = "risk_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50))  # country, supplier, route, product
    entity_id = Column(Integer)
    risk_category = Column(String(50))
    score = Column(Float, nullable=False)
    score_date = Column(DateTime, default=func.now())
    factors = Column(JSON)  # Detailed breakdown of risk factors

class Company(Base):
    """Fortune 500 company information"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    ticker = Column(String(10))
    sector = Column(String(100))
    industry = Column(String(100))
    revenue_usd = Column(BigInteger)
    market_cap_usd = Column(BigInteger)
    employee_count = Column(Integer)
    headquarters_country_id = Column(Integer, ForeignKey("countries.id"))
    supply_chain_risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())

class EconomicIndicator(Base):
    """Economic indicators and metrics"""
    __tablename__ = "economic_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"))
    indicator_name = Column(String(100))
    value = Column(Float)
    unit = Column(String(20))
    date = Column(Date, nullable=False)
    source = Column(String(100))
    last_updated = Column(DateTime, default=func.now())

# Indexes for performance
Index("idx_suppliers_country", Supplier.country_id)
Index("idx_suppliers_risk", Supplier.overall_risk_score)
Index("idx_risk_events_country_date", RiskEvent.country_id, RiskEvent.event_date)
Index("idx_trade_flows_date", TradeFlow.date)
Index("idx_risk_scores_entity", RiskScore.entity_type, RiskScore.entity_id) 