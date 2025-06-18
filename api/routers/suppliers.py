"""
SENTINEL Suppliers Router
API endpoints for supplier-related operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import logging

from models.database_connection import get_db
from models.database import Supplier, Country, SupplierProduct, Product

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def get_suppliers(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    country_id: Optional[int] = Query(None, description="Filter by country"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    tier: Optional[int] = Query(None, description="Filter by supplier tier"),
    risk_min: Optional[float] = Query(None, description="Minimum risk score"),
    risk_max: Optional[float] = Query(None, description="Maximum risk score"),
    db: Session = Depends(get_db)
):
    """Get list of suppliers with optional filtering"""
    try:
        query = db.query(Supplier)
        
        # Apply filters
        if country_id:
            query = query.filter(Supplier.country_id == country_id)
        
        if industry:
            query = query.filter(Supplier.industry == industry)
        
        if tier:
            query = query.filter(Supplier.tier == tier)
        
        if risk_min is not None:
            query = query.filter(Supplier.overall_risk_score >= risk_min)
        
        if risk_max is not None:
            query = query.filter(Supplier.overall_risk_score <= risk_max)
        
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
                "country": supplier.country.country_name if supplier.country else None,
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
            "suppliers": supplier_list,
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error fetching suppliers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information for a specific supplier"""
    try:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        # Get related products
        products = db.query(SupplierProduct).filter(
            SupplierProduct.supplier_id == supplier_id
        ).all()
        
        return {
            "id": supplier.id,
            "supplier_id": supplier.supplier_id,
            "name": supplier.name,
            "country": {
                "id": supplier.country.id,
                "name": supplier.country.country_name,
                "risk_score": supplier.country.risk_score
            } if supplier.country else None,
            "industry": supplier.industry,
            "tier": supplier.tier,
            "annual_revenue": supplier.annual_revenue,
            "employee_count": supplier.employee_count,
            "financial_health_score": supplier.financial_health_score,
            "cyber_risk_score": supplier.cyber_risk_score,
            "operational_risk_score": supplier.operational_risk_score,
            "overall_risk_score": supplier.overall_risk_score,
            "is_active": supplier.is_active,
            "products": [
                {
                    "product_id": sp.product.id,
                    "product_name": sp.product.name,
                    "capacity": sp.capacity,
                    "lead_time_days": sp.lead_time_days,
                    "cost_usd": sp.cost_usd,
                    "quality_score": sp.quality_score,
                    "reliability_score": sp.reliability_score,
                    "is_primary": sp.is_primary
                }
                for sp in products
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching supplier {supplier_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/industries/summary")
async def get_industries_summary(db: Session = Depends(get_db)):
    """Get summary statistics by industry"""
    try:
        # Get industry statistics
        industry_stats = db.query(
            Supplier.industry,
            func.count(Supplier.id).label('supplier_count'),
            func.avg(Supplier.overall_risk_score).label('avg_risk_score'),
            func.avg(Supplier.annual_revenue).label('avg_revenue'),
            func.avg(Supplier.employee_count).label('avg_employees')
        ).group_by(Supplier.industry).all()
        
        # Format response
        industries = []
        for stat in industry_stats:
            industries.append({
                "industry": stat.industry,
                "supplier_count": stat.supplier_count,
                "average_risk_score": round(stat.avg_risk_score, 2) if stat.avg_risk_score else 0,
                "average_revenue": round(stat.avg_revenue, 2) if stat.avg_revenue else 0,
                "average_employees": round(stat.avg_employees, 2) if stat.avg_employees else 0
            })
        
        return {
            "industries": industries,
            "total_industries": len(industries)
        }
    
    except Exception as e:
        logger.error(f"Error fetching industries summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/high-risk/list")
async def get_high_risk_suppliers(
    risk_threshold: float = Query(70, description="Risk score threshold"),
    limit: int = Query(50, description="Maximum number of suppliers to return"),
    db: Session = Depends(get_db)
):
    """Get list of high-risk suppliers"""
    try:
        suppliers = db.query(Supplier).filter(
            Supplier.overall_risk_score >= risk_threshold
        ).order_by(Supplier.overall_risk_score.desc()).limit(limit).all()
        
        supplier_list = []
        for supplier in suppliers:
            supplier_list.append({
                "id": supplier.id,
                "supplier_id": supplier.supplier_id,
                "name": supplier.name,
                "country": supplier.country.country_name if supplier.country else None,
                "industry": supplier.industry,
                "tier": supplier.tier,
                "overall_risk_score": supplier.overall_risk_score,
                "financial_health_score": supplier.financial_health_score,
                "cyber_risk_score": supplier.cyber_risk_score,
                "operational_risk_score": supplier.operational_risk_score
            })
        
        return {
            "high_risk_suppliers": supplier_list,
            "risk_threshold": risk_threshold,
            "total_count": len(supplier_list)
        }
    
    except Exception as e:
        logger.error(f"Error fetching high-risk suppliers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tiers/summary")
async def get_tiers_summary(db: Session = Depends(get_db)):
    """Get summary statistics by supplier tier"""
    try:
        # Get tier statistics
        tier_stats = db.query(
            Supplier.tier,
            func.count(Supplier.id).label('supplier_count'),
            func.avg(Supplier.overall_risk_score).label('avg_risk_score'),
            func.avg(Supplier.annual_revenue).label('avg_revenue')
        ).group_by(Supplier.tier).order_by(Supplier.tier).all()
        
        # Format response
        tiers = []
        for stat in tier_stats:
            tiers.append({
                "tier": stat.tier,
                "supplier_count": stat.supplier_count,
                "average_risk_score": round(stat.avg_risk_score, 2) if stat.avg_risk_score else 0,
                "average_revenue": round(stat.avg_revenue, 2) if stat.avg_revenue else 0
            })
        
        return {
            "tiers": tiers,
            "total_tiers": len(tiers)
        }
    
    except Exception as e:
        logger.error(f"Error fetching tiers summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 