# Technology Stack

## Backend

- **Framework**: FastAPI 0.109.0 - Modern async web framework
- **ORM**: SQLAlchemy 2.0+ - Database abstraction layer
- **Database**: SQLite (dev) / PostgreSQL 12+ (prod)
- **Migration**: Alembic 1.13.1 - Database schema versioning
- **Data Processing**: Pandas 2.2.0, NumPy 1.26.3
- **Data Source**: AkShare 1.18.0+ - A-share market data provider
- **Validation**: Pydantic 2.5.0+ - Request/response validation
- **Cache**: Redis 5.0+ (optional, in-memory fallback)
- **Server**: Uvicorn with standard extras
- **Testing**: Pytest 7.4.4, Pytest-asyncio, Hypothesis

## Frontend

- **Framework**: Vue 3.4.15 - Composition API
- **Build Tool**: Vite 5.0.11 - Fast dev server and bundler
- **UI Library**: Element Plus 2.5.4 - Vue 3 component library
- **Charts**: ECharts 5.4.3 - Data visualization
- **HTTP Client**: Axios 1.6.5
- **State Management**: Pinia 2.1.7
- **Router**: Vue Router 4.2.5
- **CSS**: Sass 1.70.0
- **Testing**: Vitest 1.2.1, @vue/test-utils 2.4.3

## Development Tools

- **Python**: 3.9+ required
- **Node.js**: 16+ required
- **Package Manager**: npm (frontend), pip (backend)
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (production frontend)

## Common Commands

### Backend

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Database
alembic upgrade head              # Run migrations
alembic revision -m "description" # Create migration
python scripts/init_db.py         # Initialize database

# Development
python main.py                    # Start dev server (port 8000)
uvicorn main:app --reload         # Alternative start

# Testing
pytest                            # Run all tests
pytest --cov=. --cov-report=html  # With coverage
pytest tests/test_api_endpoints.py # Specific test file

# Scripts
python scripts/verify_indexes.py  # Verify DB indexes
python scripts/demo_indicator_calculator.py # Demo features
```

### Frontend

```bash
# Setup
cd frontend
npm install

# Development
npm run dev      # Start dev server (port 5173)
npm run build    # Production build
npm run preview  # Preview production build

# Testing
npm run test         # Run tests once
npm run test:watch   # Watch mode
```

### Docker

```bash
# Development
make build    # Build images
make up       # Start all services
make down     # Stop services
make logs     # View logs
make test     # Run tests

# Production
make prod-build  # Build production images
make prod-up     # Start production environment

# Database
make db-migrate  # Run migrations in container
```

## Environment Configuration

Backend uses `.env` file (see `.env.example`):
- `DATABASE_URL` - Database connection string
- `CORS_ORIGINS` - Allowed frontend origins
- `REDIS_URL` - Redis connection (optional)
- `RATE_LIMIT_PER_MINUTE` - API rate limiting

Frontend uses `.env` file:
- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000)

## API Documentation

When backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
