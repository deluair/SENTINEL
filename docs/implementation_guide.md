# SENTINEL Implementation Guide
## Fortune 500 Geopolitical Trade Risk Navigator

### Overview
SENTINEL is a comprehensive geopolitical trade risk assessment platform designed for Fortune 500 companies. This guide provides detailed instructions for implementing and deploying the system.

### Architecture Overview

#### Core Components
1. **Database Layer**: PostgreSQL with comprehensive schema for countries, suppliers, products, trade routes, companies, and risk events
2. **API Layer**: FastAPI-based REST API with modular routers
3. **Risk Scoring Engine**: Proprietary i-Score methodology for risk assessment
4. **Dashboard**: Interactive web dashboard built with Dash and Plotly
5. **Data Generation**: Synthetic data generator for realistic simulation data

#### Technology Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Database**: PostgreSQL 15, Redis
- **Frontend**: Dash, Plotly, Bootstrap
- **ML/Analytics**: Scikit-learn, TensorFlow, Pandas, NumPy
- **Deployment**: Docker, Docker Compose

### Installation & Setup

#### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL (if not using Docker)
- Redis (if not using Docker)

#### Quick Start with Docker
```bash
# Clone the repository
git clone <repository-url>
cd SENTINEL

# Start all services
docker-compose up -d

# Generate sample data
docker-compose exec sentinel_api python scripts/generate_data.py --sample

# Access the application
# API: http://localhost:8000
# Dashboard: http://localhost:8050
# API Docs: http://localhost:8000/docs
```

#### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
python scripts/setup_database.py

# Generate data
python scripts/generate_data.py --sample

# Start API
python api/main.py

# Start Dashboard (in another terminal)
python dashboard/app.py
```

### Data Model

#### Core Entities

**Countries**
- Country information and geopolitical risk metrics
- Political stability, economic freedom, corruption indices
- Risk scores calculated using i-Score methodology

**Suppliers**
- Multi-tier supplier network (Tier 1-6)
- Financial health, cyber risk, operational risk scores
- Industry classification and revenue data

**Products**
- Product categories with criticality scores
- Price volatility and substitution difficulty metrics
- Base pricing and unit information

**Trade Routes**
- Origin-destination country pairs
- Route types (sea, air, land)
- Vulnerability scores and chokepoint risk

**Companies**
- Fortune 500 company profiles
- Supply chain risk assessments
- Sector and industry classification

**Risk Events**
- Real-time risk event tracking
- Event types: geopolitical, economic, cyber, regulatory
- Severity and impact scoring

### API Endpoints

#### Core Endpoints
- `GET /api/v1/countries` - List countries with filtering
- `GET /api/v1/suppliers` - List suppliers with filtering
- `GET /api/v1/products` - List products
- `GET /api/v1/trade-routes` - List trade routes
- `GET /api/v1/companies` - List companies
- `GET /api/v1/risk-events` - List risk events

#### Risk Assessment Endpoints
- `GET /api/v1/risk-score/{entity_type}/{entity_id}` - Get risk score for entity
- `GET /api/v1/supply-chain-risk/{company_id}` - Get company supply chain risk
- `GET /api/v1/risk-alerts` - Get active risk alerts
- `GET /api/v1/dashboard-summary` - Get dashboard summary data

#### Analytics Endpoints
- `GET /api/v1/analytics/risk-summary` - Overall risk summary
- `GET /api/v1/analytics/trends` - Risk trends over time
- `GET /api/v1/analytics/predictions` - Risk predictions

### Risk Scoring Methodology

#### i-Score Engine
The proprietary i-Score methodology calculates comprehensive risk scores using:

1. **Country Risk Factors**
   - Political stability index
   - Economic freedom index
   - Corruption perception index
   - GDP per capita

2. **Supplier Risk Factors**
   - Financial health score
   - Cyber risk score
   - Operational risk score
   - Tier level (1-6)
   - Country risk influence

3. **Trade Route Risk Factors**
   - Distance and transit time
   - Route type vulnerability
   - Chokepoint risk
   - Origin/destination country risk

4. **Product Risk Factors**
   - Criticality score
   - Price volatility
   - Substitution difficulty
   - Market conditions

#### Risk Score Calculation
```python
# Example risk score calculation
risk_score = (
    political_risk * 0.4 +
    economic_risk * 0.3 +
    corruption_risk * 0.2 +
    development_risk * 0.1
) * 100
```

### Dashboard Features

#### Overview Dashboard
- Key metrics cards (countries, suppliers, risk events)
- Global risk heatmap
- Risk score distribution
- Recent risk events table
- Risk trends by region

#### Interactive Features
- Country selector with detailed risk analysis
- Supplier filtering by industry, tier, and risk level
- Trade route vulnerability mapping
- Company supply chain risk assessment

#### Visualizations
- Choropleth maps for global risk
- Bar charts for risk distributions
- Line charts for trends
- Tables for detailed data

### Data Generation

#### Synthetic Data
The system generates realistic synthetic data including:

- **195 Countries** with realistic geopolitical profiles
- **500,000 Suppliers** across 6 tiers and 10 industries
- **2,800 Products** in various categories
- **850 Trade Routes** with vulnerability scores
- **500 Companies** representing Fortune 500
- **1,000 Risk Events** with realistic scenarios

#### Data Generation Commands
```bash
# Generate full dataset
python scripts/generate_data.py

# Generate sample dataset
python scripts/generate_data.py --sample

# Clear existing data
python scripts/generate_data.py --clear

# Check data status
python scripts/generate_data.py --status
```

### Configuration

#### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/db
REDIS_URL=redis://host:port/db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Dashboard Settings
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8050

# Security
SECRET_KEY=your-secret-key
```

#### Risk Score Weights
```python
RISK_SCORE_WEIGHTS = {
    "geopolitical": 0.25,
    "economic": 0.20,
    "supply_chain": 0.20,
    "cyber": 0.15,
    "regulatory": 0.10,
    "environmental": 0.10
}
```

### Deployment

#### Production Deployment
1. **Database Setup**
   ```bash
   # Set up PostgreSQL
   createdb sentinel_db
   python scripts/setup_database.py
   ```

2. **Data Population**
   ```bash
   # Generate production data
   python scripts/generate_data.py
   ```

3. **Service Deployment**
   ```bash
   # Using Docker Compose
   docker-compose -f docker-compose.prod.yml up -d
   
   # Or using Kubernetes
   kubectl apply -f k8s/
   ```

#### Monitoring & Logging
- Application logs: `/app/logs/`
- Database monitoring: PostgreSQL metrics
- API monitoring: FastAPI built-in metrics
- Health checks: `/health` endpoint

### Testing

#### API Testing
```bash
# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/dashboard-summary
curl http://localhost:8000/api/v1/countries
```

#### Data Validation
```bash
# Check data integrity
python scripts/setup_database.py --status
python scripts/generate_data.py --status
```

### Performance Optimization

#### Database Optimization
- Indexes on frequently queried columns
- Connection pooling
- Query optimization

#### API Optimization
- Response caching with Redis
- Pagination for large datasets
- Async processing for heavy operations

#### Dashboard Optimization
- Lazy loading of visualizations
- Data caching
- Responsive design

### Security Considerations

#### API Security
- Input validation
- Rate limiting
- CORS configuration
- Authentication (to be implemented)

#### Data Security
- Database encryption
- Secure connection strings
- Audit logging

### Troubleshooting

#### Common Issues
1. **Database Connection Errors**
   - Check DATABASE_URL configuration
   - Verify PostgreSQL is running
   - Check network connectivity

2. **Data Generation Issues**
   - Ensure sufficient disk space
   - Check database permissions
   - Verify Python dependencies

3. **Dashboard Loading Issues**
   - Check API connectivity
   - Verify data availability
   - Check browser console for errors

#### Log Analysis
```bash
# View application logs
docker-compose logs sentinel_api
docker-compose logs sentinel_dashboard

# Check database logs
docker-compose logs postgres
```

### Future Enhancements

#### Planned Features
1. **Real-time Data Integration**
   - News API integration
   - Economic indicators
   - Shipping data feeds

2. **Advanced Analytics**
   - Machine learning predictions
   - Scenario modeling
   - Trend analysis

3. **User Management**
   - Authentication system
   - Role-based access
   - User preferences

4. **Mobile Application**
   - React Native app
   - Push notifications
   - Offline capabilities

### Support & Maintenance

#### Regular Maintenance
- Database backups
- Log rotation
- Dependency updates
- Performance monitoring

#### Monitoring
- Application health checks
- Database performance
- API response times
- Error rates

### Conclusion

SENTINEL provides a comprehensive solution for geopolitical trade risk assessment. The modular architecture allows for easy extension and customization based on specific business requirements. The synthetic data generation ensures realistic testing scenarios while the i-Score methodology provides accurate risk assessments.

For additional support or customization requests, please refer to the project documentation or contact the development team. 