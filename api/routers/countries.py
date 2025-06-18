"""
SENTINEL Countries Router
API endpoints for country-related operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from models.database_connection import get_db
from models.database import Country, RiskEvent, Supplier
from models.risk_scoring import i_score_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def get_countries(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    region: Optional[str] = Query(None, description="Filter by region"),
    risk_min: Optional[float] = Query(None, description="Minimum risk score"),
    risk_max: Optional[float] = Query(None, description="Maximum risk score"),
    db: Session = Depends(get_db)
):
    """Get list of countries with optional filtering"""
    try:
        query = db.query(Country)
        
        # Apply filters
        if region:
            query = query.filter(Country.region == region)
        
        if risk_min is not None:
            query = query.filter(Country.risk_score >= risk_min)
        
        if risk_max is not None:
            query = query.filter(Country.risk_score <= risk_max)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        countries = query.offset(skip).limit(limit).all()
        
        # Format response
        country_list = []
        for country in countries:
            country_list.append({
                "id": country.id,
                "country_code": country.country_code,
                "country_name": country.country_name,
                "region": country.region,
                "gdp_usd": country.gdp_usd,
                "population": country.population,
                "political_stability_index": country.political_stability_index,
                "economic_freedom_index": country.economic_freedom_index,
                "corruption_perception_index": country.corruption_perception_index,
                "risk_score": country.risk_score,
                "last_updated": country.last_updated.isoformat() if country.last_updated else None
            })
        
        return {
            "countries": country_list,
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error fetching countries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{country_id}")
async def get_country(
    country_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific country"""
    try:
        country = db.query(Country).filter(Country.id == country_id).first()
        
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        
        # Get related data
        supplier_count = db.query(Supplier).filter(Supplier.country_id == country_id).count()
        active_events = db.query(RiskEvent).filter(
            RiskEvent.country_id == country_id,
            RiskEvent.is_active == True
        ).count()
        
        return {
            "id": country.id,
            "country_code": country.country_code,
            "country_name": country.country_name,
            "region": country.region,
            "gdp_usd": country.gdp_usd,
            "population": country.population,
            "political_stability_index": country.political_stability_index,
            "economic_freedom_index": country.economic_freedom_index,
            "corruption_perception_index": country.corruption_perception_index,
            "risk_score": country.risk_score,
            "last_updated": country.last_updated.isoformat() if country.last_updated else None,
            "statistics": {
                "supplier_count": supplier_count,
                "active_risk_events": active_events
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching country {country_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{country_id}/risk-events")
async def get_country_risk_events(
    country_id: int,
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(50, description="Maximum number of records to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    db: Session = Depends(get_db)
):
    """Get risk events for a specific country"""
    try:
        # Verify country exists
        country = db.query(Country).filter(Country.id == country_id).first()
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        
        query = db.query(RiskEvent).filter(RiskEvent.country_id == country_id)
        
        if event_type:
            query = query.filter(RiskEvent.event_type == event_type)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        events = query.order_by(RiskEvent.event_date.desc()).offset(skip).limit(limit).all()
        
        # Format response
        event_list = []
        for event in events:
            event_list.append({
                "event_id": event.event_id,
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type,
                "severity": event.severity,
                "impact_score": event.impact_score,
                "confidence_score": event.confidence_score,
                "event_date": event.event_date.isoformat() if event.event_date else None,
                "source": event.source,
                "is_active": event.is_active
            })
        
        return {
            "country_id": country_id,
            "country_name": country.country_name,
            "events": event_list,
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching risk events for country {country_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{country_id}/suppliers")
async def get_country_suppliers(
    country_id: int,
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    tier: Optional[int] = Query(None, description="Filter by supplier tier"),
    risk_min: Optional[float] = Query(None, description="Minimum risk score"),
    db: Session = Depends(get_db)
):
    """Get suppliers for a specific country"""
    try:
        # Verify country exists
        country = db.query(Country).filter(Country.id == country_id).first()
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        
        query = db.query(Supplier).filter(Supplier.country_id == country_id)
        
        # Apply filters
        if industry:
            query = query.filter(Supplier.industry == industry)
        
        if tier:
            query = query.filter(Supplier.tier == tier)
        
        if risk_min is not None:
            query = query.filter(Supplier.overall_risk_score >= risk_min)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        suppliers = query.offset(skip).limit(limit).all()
        
        # Format response
        supplier_list = []
        for supplier in suppliers:
            supplier_list.append({
                "id": supplier.id,
                "supplier_id": supplier.supplier_id,
                "name": supplier.name,
                "industry": supplier.industry,
                "tier": supplier.tier,
                "annual_revenue": supplier.annual_revenue,
                "employee_count": supplier.employee_count,
                "financial_health_score": supplier.financial_health_score,
                "cyber_risk_score": supplier.cyber_risk_score,
                "operational_risk_score": supplier.operational_risk_score,
                "overall_risk_score": supplier.overall_risk_score,
                "is_active": supplier.is_active
            })
        
        return {
            "country_id": country_id,
            "country_name": country.country_name,
            "suppliers": supplier_list,
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching suppliers for country {country_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/regions/summary")
async def get_regions_summary(db: Session = Depends(get_db)):
    """Get summary statistics by region"""
    try:
        # Get region statistics
        region_stats = db.query(
            Country.region,
            func.count(Country.id).label('country_count'),
            func.avg(Country.risk_score).label('avg_risk_score'),
            func.avg(Country.gdp_usd).label('avg_gdp'),
            func.sum(Country.population).label('total_population')
        ).group_by(Country.region).all()
        
        # Format response
        regions = []
        for stat in region_stats:
            regions.append({
                "region": stat.region,
                "country_count": stat.country_count,
                "average_risk_score": round(stat.avg_risk_score, 2) if stat.avg_risk_score else 0,
                "average_gdp_usd": round(stat.avg_gdp, 2) if stat.avg_gdp else 0,
                "total_population": stat.total_population
            })
        
        return {
            "regions": regions,
            "total_regions": len(regions)
        }
    
    except Exception as e:
        logger.error(f"Error fetching regions summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/high-risk/list")
async def get_high_risk_countries(
    risk_threshold: float = Query(70, description="Risk score threshold"),
    limit: int = Query(20, description="Maximum number of countries to return"),
    db: Session = Depends(get_db)
):
    """Get list of high-risk countries"""
    try:
        countries = db.query(Country).filter(
            Country.risk_score >= risk_threshold
        ).order_by(Country.risk_score.desc()).limit(limit).all()
        
        country_list = []
        for country in countries:
            country_list.append({
                "id": country.id,
                "country_code": country.country_code,
                "country_name": country.country_name,
                "region": country.region,
                "risk_score": country.risk_score,
                "political_stability_index": country.political_stability_index,
                "economic_freedom_index": country.economic_freedom_index,
                "corruption_perception_index": country.corruption_perception_index
            })
        
        return {
            "high_risk_countries": country_list,
            "risk_threshold": risk_threshold,
            "total_count": len(country_list)
        }
    
    except Exception as e:
        logger.error(f"Error fetching high-risk countries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 