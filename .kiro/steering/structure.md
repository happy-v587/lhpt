# Project Structure and Architecture

## Repository Layout

```
.
├── backend/              # Python FastAPI backend
├── frontend/             # Vue 3 frontend
├── docs/                 # Project-wide documentation
├── docker-compose.yml    # Development environment
├── docker-compose.prod.yml # Production environment
├── Makefile             # Docker management commands
└── README.md            # Main project documentation
```

## Backend Architecture (Layered)

```
backend/
├── api/                 # API Layer - HTTP endpoints, request/response handling
├── services/            # Service Layer - Business logic, core algorithms
├── repositories/        # Data Access Layer - Database operations
├── models/              # ORM Models - Database table definitions
├── validators/          # Validation Layer - Data validation and business rules
├── middleware/          # Middleware - Rate limiting, CORS, logging
├── alembic/             # Database migrations
├── tests/               # Test suite
├── scripts/             # Utility scripts
├── docs/                # Backend-specific documentation
├── data/                # SQLite database files (gitignored)
├── main.py              # Application entry point
├── config.py            # Configuration management
├── database.py          # Database connection and session
└── exceptions.py        # Custom exception classes
```

### Backend Layer Responsibilities

**API Layer** (`api/`):
- Define HTTP endpoints using FastAPI routers
- Handle request/response serialization with Pydantic
- Route prefix: `/api/{resource}`
- Files: `stocks.py`, `indicators.py`, `strategies.py`, `backtests.py`, `custom_indicators.py`

**Service Layer** (`services/`):
- Implement core business logic
- No direct database access (use repositories)
- Files: `data_provider.py`, `indicator_calculator.py`, `backtest_engine.py`, `custom_indicator_engine.py`, `cache_service.py`

**Repository Layer** (`repositories/`):
- Encapsulate all database operations
- Manage transactions and sessions
- Handle cache invalidation
- Files: `data_repository.py`

**Models** (`models/`):
- SQLAlchemy ORM models
- One model per file
- Define indexes and relationships
- Files: `stock.py`, `kline_data.py`, `strategy.py`, `backtest.py`, `custom_indicator.py`

**Dependency Flow**: API → Services → Repositories → Models → Database

## Frontend Architecture (Component-Based)

```
frontend/
├── src/
│   ├── components/      # Reusable Vue components
│   ├── views/           # Page-level components (routes)
│   ├── services/        # API client modules
│   ├── router/          # Vue Router configuration
│   ├── stores/          # Pinia state management
│   ├── utils/           # Utility functions and constants
│   ├── assets/          # Static assets (images, fonts)
│   ├── App.vue          # Root component
│   └── main.js          # Application entry point
├── docs/                # Frontend-specific documentation
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
├── package.json         # Dependencies and scripts
└── nginx.conf           # Production Nginx config
```

### Frontend Organization

**Components** (`components/`):
- Reusable UI components
- Files: `IndicatorConfig.vue`, `KLineChart.vue`, `StockSelector.vue`, `StrategyManager.vue`

**Views** (`views/`):
- Page-level components mapped to routes
- Files: `HomeView.vue`, `ChartView.vue`, `BacktestView.vue`, `StrategyView.vue`, `CustomIndicatorView.vue`, `IndicatorConfigView.vue`

**Services** (`services/`):
- API client modules using Axios
- One service per backend resource
- Files: `api.js` (base config), `stocks.js`, `indicators.js`, `strategies.js`, `backtests.js`, `customIndicators.js`

## Naming Conventions

### Backend (Python)

- **Files**: `snake_case.py` (e.g., `indicator_calculator.py`)
- **Classes**: `PascalCase` (e.g., `IndicatorCalculator`)
- **Functions**: `snake_case()` (e.g., `calculate_ma()`)
- **Variables**: `snake_case` (e.g., `stock_code`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- **Private**: `_leading_underscore` (e.g., `_internal_method()`)

### Frontend (JavaScript/Vue)

- **Files**: `PascalCase.vue` for components, `camelCase.js` for modules
- **Components**: `PascalCase` (e.g., `StockSelector.vue`)
- **Functions**: `camelCase()` (e.g., `fetchStockData()`)
- **Variables**: `camelCase` (e.g., `stockCode`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)

## Code Style Guidelines

### Backend

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Include docstrings for classes and public methods
- Use async/await for I/O operations
- Handle exceptions explicitly, use custom exception classes
- Log important operations and errors

### Frontend

- Use Vue 3 Composition API (not Options API)
- Follow ESLint rules
- Use `<script setup>` syntax
- Destructure props and emits
- Keep components focused and single-purpose

## Database Conventions

- **Table names**: Lowercase, plural (e.g., `stocks`, `kline_data`)
- **Column names**: Lowercase, snake_case (e.g., `stock_code`, `created_at`)
- **Primary keys**: Use appropriate type (String for codes, Integer for IDs)
- **Indexes**: Define on frequently queried columns
- **Migrations**: Sequential numbering `001_`, `002_`, etc.

## API Conventions

- **Endpoints**: RESTful, plural nouns (e.g., `/api/stocks`, `/api/strategies`)
- **Methods**: GET (read), POST (create), PUT (update), DELETE (delete)
- **Response format**: JSON with consistent error structure
- **Error codes**: Custom error codes in responses (e.g., `VALIDATION_ERROR`, `DATA_NOT_FOUND`)
- **Timestamps**: ISO 8601 format with UTC timezone

## Documentation Structure

- **Root docs/**: Project-wide guides and summaries
- **backend/docs/**: Backend architecture and API documentation
- **frontend/docs/**: Frontend components and updates
- **README files**: Each major directory has its own README
- **Inline comments**: Chinese for business logic, English for technical details

## Testing Organization

### Backend Tests

- **Location**: `backend/tests/`
- **Naming**: `test_*.py` (e.g., `test_api_endpoints.py`)
- **Fixtures**: Defined in `conftest.py`
- **Coverage**: Aim for >80%
- **Types**: Unit tests, integration tests, API tests

### Frontend Tests

- **Location**: Colocated with components or in `__tests__/`
- **Naming**: `*.test.js` or `*.spec.js`
- **Framework**: Vitest with Vue Test Utils

## Key Architectural Patterns

1. **Separation of Concerns**: Clear boundaries between layers
2. **Dependency Injection**: FastAPI's `Depends()` for loose coupling
3. **Repository Pattern**: Centralized data access
4. **Service Layer**: Business logic isolation
5. **Validation Layer**: Separate data validation from business logic
6. **Caching Strategy**: Redis with in-memory fallback
7. **Error Handling**: Custom exceptions with consistent error responses
