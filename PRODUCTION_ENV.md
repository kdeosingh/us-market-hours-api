# Production Environment Variables for Railway

## Copy these to Railway Dashboard

```bash
# ===================================
# PRODUCTION CONFIGURATION
# ===================================

# Application
DEBUG=False

# CORS - Update with your frontend URL
CORS_ORIGINS=https://yourfrontend.vercel.app,https://www.yourdomain.com

# API Documentation Access
DOCS_PASSWORD=YourSecurePassword123!
DOCS_SESSION_SECRET=your-random-secret-key-32-chars-long

# Data Storage (Railway defaults work, but you can customize)
DATA_DIR=/app/data
DB_PATH=/app/data/market_hours.db

# Scraper Configuration
SCRAPER_ENABLED=True
SCRAPER_SCHEDULE_HOUR=6
SCRAPER_TIMEOUT=30

# API Authentication (Optional)
ENABLE_API_AUTH=False
API_KEYS=["key1","key2"]

# Rate Limiting (Optional)
RATE_LIMIT_ENABLED=False
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

## ⚠️ IMPORTANT: Update These Before Deploy

1. **CORS_ORIGINS** - Replace with your actual frontend URL
2. **DOCS_PASSWORD** - Change from default to secure password
3. **DOCS_SESSION_SECRET** - Generate random 32+ character string
4. **API_KEYS** - If enabling auth, add your keys

## 🔐 Generate Secure Secrets

```bash
# Generate random session secret (32 chars)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use online generator:
# https://randomkeygen.com/
```

## 📋 How to Set in Railway

1. Go to Railway Dashboard
2. Select your project
3. Click on your service
4. Go to "Variables" tab
5. Click "New Variable"
6. Add each variable above
7. Click "Deploy"

Railway will automatically restart your app with new variables.



