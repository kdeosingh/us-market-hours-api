# US Market Hours Calendar - Backend

FastAPI backend for US stock market hours and holiday schedules.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run server
python main.py
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Components

- **main.py** - FastAPI application entry point
- **app/routers/** - API endpoint definitions
- **app/scraper.py** - Market hours scraper
- **app/scheduler.py** - Daily scraping scheduler
- **app/business_logic.py** - Market hours calculations
- **app/database.py** - SQLite database operations
- **app/models.py** - Pydantic data models
- **app/config.py** - Configuration management

## Data Storage

Market hours data is stored in `data/market_hours.db` (SQLite).

The scraper runs daily at 6 AM UTC by default.

## Testing

```bash
# Test API endpoints
curl http://localhost:8000/market-hours/today

# Manual scraper run
python -c "from app.scraper import scraper; scraper.run_scraper()"
```

## Docker

```bash
# Build image
docker build -t market-hours-backend .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data market-hours-backend
```



