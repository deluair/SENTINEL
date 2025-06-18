"""
SENTINEL API Main Application
FastAPI application for the Geopolitical Trade Risk Navigator
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from config.settings import settings
from models.database_connection import get_db
from models.risk_scoring import i_score_engine
from models.database import Country, Supplier, Product, TradeRoute, Company, RiskEvent, SupplierProduct
from api.routers import countries, suppliers, products, trade_routes, companies, risk_events, analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Fortune 500 Geopolitical Trade Risk Navigator API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(countries.router, prefix=f"{settings.API_PREFIX}/countries", tags=["Countries"])
app.include_router(suppliers.router, prefix=f"{settings.API_PREFIX}/suppliers", tags=["Suppliers"])
app.include_router(products.router, prefix=f"{settings.API_PREFIX}/products", tags=["Products"])
app.include_router(trade_routes.router, prefix=f"{settings.API_PREFIX}/trade-routes", tags=["Trade Routes"])
app.include_router(companies.router, prefix=f"{settings.API_PREFIX}/companies", tags=["Companies"])
app.include_router(risk_events.router, prefix=f"{settings.API_PREFIX}/risk-events", tags=["Risk Events"])
app.include_router(analytics.router, prefix=f"{settings.API_PREFIX}/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/api/v1/risk-score/{entity_type}/{entity_id}")
async def get_risk_score(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db)
):
    """Get risk score for a specific entity"""
    try:
        if entity_type == "country":
            # Get country data and calculate risk score
            country = db.query(Country).filter(Country.id == entity_id).first()
            if not country:
                raise HTTPException(status_code=404, detail="Country not found")
            
            risk_score = i_score_engine.calculate_country_risk_score({
                'political_stability_index': country.political_stability_index,
                'economic_freedom_index': country.economic_freedom_index,
                'corruption_perception_index': country.corruption_perception_index,
                'gdp_usd': country.gdp_usd,
                'population': country.population
            })
            
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "risk_score": risk_score,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        elif entity_type == "supplier":
            # Get supplier data and calculate risk score
            supplier = db.query(Supplier).filter(Supplier.id == entity_id).first()
            if not supplier:
                raise HTTPException(status_code=404, detail="Supplier not found")
            
            # Get country risk for supplier
            country_risk = supplier.country.risk_score if supplier.country else 50.0
            
            risk_scores = i_score_engine.calculate_supplier_risk_score({
                'financial_health_score': supplier.financial_health_score,
                'cyber_risk_score': supplier.cyber_risk_score,
                'operational_risk_score': supplier.operational_risk_score,
                'tier': supplier.tier,
                'annual_revenue': supplier.annual_revenue
            }, country_risk)
            
            return {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "risk_scores": risk_scores,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported entity type")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating risk score: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/supply-chain-risk/{company_id}")
async def get_supply_chain_risk(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive supply chain risk for a company"""
    try:
        # Get company data
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get related suppliers, routes, and products
        suppliers = db.query(Supplier).filter(Supplier.id.in_(
            db.query(SupplierProduct.supplier_id).distinct()
        )).all()
        
        routes = db.query(TradeRoute).filter(TradeRoute.is_active.is_(True)).all()
        products = db.query(Product).all()
        
        # Calculate supply chain risk
        risk_assessment = i_score_engine.calculate_company_supply_chain_risk(
            company_data={
                'id': company.id,
                'name': company.name,
                'sector': company.sector
            },
            suppliers=[{
                'overall_risk_score': s.overall_risk_score,
                'country_id': s.country_id
            } for s in suppliers],
            routes=[{
                'vulnerability_score': r.vulnerability_score
            } for r in routes],
            products=[{
                'criticality_score': p.criticality_score
            } for p in products]
        )
        
        return {
            "company_id": company_id,
            "company_name": company.name,
            "risk_assessment": risk_assessment,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating supply chain risk: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/risk-alerts")
async def get_risk_alerts(
    severity_min: float = Query(50, description="Minimum severity threshold"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    country_id: Optional[int] = Query(None, description="Filter by country"),
    limit: int = Query(100, description="Maximum number of alerts"),
    db: Session = Depends(get_db)
):
    """Get active risk alerts"""
    try:
        query = db.query(RiskEvent).filter(RiskEvent.is_active.is_(True))
        
        if severity_min:
            query = query.filter(RiskEvent.severity >= severity_min)
        
        if event_type:
            query = query.filter(RiskEvent.event_type == event_type)
        
        if country_id:
            query = query.filter(RiskEvent.country_id == country_id)
        
        events = query.order_by(RiskEvent.severity.desc()).limit(limit).all()
        
        alerts = []
        for event in events:
            alerts.append({
                "event_id": event.event_id,
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type,
                "severity": event.severity,
                "impact_score": event.impact_score,
                "confidence_score": event.confidence_score,
                "event_date": event.event_date.isoformat() if event.event_date else None,
                "country": event.country.country_name if event.country else None,
                "source": event.source
            })
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error fetching risk alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/dashboard-summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get summary data for dashboard"""
    try:
        # Get counts
        total_countries = db.query(Country).count()
        total_suppliers = db.query(Supplier).filter(Supplier.is_active.is_(True)).count()
        total_products = db.query(Product).count()
        total_routes = db.query(TradeRoute).filter(TradeRoute.is_active.is_(True)).count()
        total_companies = db.query(Company).count()
        active_events = db.query(RiskEvent).filter(RiskEvent.is_active.is_(True)).count()
        
        # Get average risk scores
        avg_country_risk = db.query(func.avg(Country.risk_score)).scalar() or 0
        avg_supplier_risk = db.query(func.avg(Supplier.overall_risk_score)).scalar() or 0
        avg_route_vulnerability = db.query(func.avg(TradeRoute.vulnerability_score)).scalar() or 0
        
        # Get high-risk entities
        high_risk_countries = db.query(Country).filter(Country.risk_score >= 70).count()
        high_risk_suppliers = db.query(Supplier).filter(Supplier.overall_risk_score >= 70).count()
        
        return {
            "summary": {
                "total_countries": total_countries,
                "total_suppliers": total_suppliers,
                "total_products": total_products,
                "total_routes": total_routes,
                "total_companies": total_companies,
                "active_risk_events": active_events
            },
            "risk_metrics": {
                "average_country_risk": round(avg_country_risk, 2),
                "average_supplier_risk": round(avg_supplier_risk, 2),
                "average_route_vulnerability": round(avg_route_vulnerability, 2),
                "high_risk_countries": high_risk_countries,
                "high_risk_suppliers": high_risk_suppliers
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    ) 