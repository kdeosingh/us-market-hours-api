"""
Market hours API endpoints
"""
from fastapi import APIRouter, HTTPException, Header, Request
from datetime import date, datetime, timedelta
from typing import Optional
import logging

from app.models import (
    MarketHoursResponse, 
    WeekScheduleResponse, 
    NextEventResponse
)
from app.business_logic import market_logic
from app.database import db
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key if authentication is enabled"""
    if not settings.ENABLE_API_AUTH:
        return True
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if x_api_key not in settings.API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


@router.get("/today", response_model=MarketHoursResponse)
async def get_today_market_hours(
    x_api_key: Optional[str] = Header(None)
):
    """
    Get market hours for today
    
    Returns opening time, closing time, and current status
    """
    verify_api_key(x_api_key)
    
    try:
        today = date.today()
        return market_logic.get_market_hours_for_date(today)
    except Exception as e:
        logger.error(f"Error getting today's market hours: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/week", response_model=WeekScheduleResponse)
async def get_week_schedule(
    start_date: Optional[str] = None,
    x_api_key: Optional[str] = Header(None)
):
    """
    Get 7-day market schedule
    
    - **start_date**: Optional start date (YYYY-MM-DD). Defaults to today.
    """
    verify_api_key(x_api_key)
    
    try:
        if start_date:
            start = date.fromisoformat(start_date)
        else:
            start = date.today()
        
        end = start + timedelta(days=6)
        
        schedule = market_logic.get_week_schedule(start)
        
        return WeekScheduleResponse(
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            days=schedule
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error getting week schedule: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/next", response_model=NextEventResponse)
async def get_next_event(
    x_api_key: Optional[str] = Header(None)
):
    """
    Get next market open or close event
    
    Returns the next upcoming market event (open or close)
    """
    verify_api_key(x_api_key)
    
    try:
        event = market_logic.next_market_event()
        
        if not event:
            raise HTTPException(
                status_code=404, 
                detail="No upcoming market events found in next 30 days"
            )
        
        return NextEventResponse(**event)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next event: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/date/{target_date}", response_model=MarketHoursResponse)
async def get_market_hours_for_date(
    target_date: str,
    x_api_key: Optional[str] = Header(None)
):
    """
    Get market hours for a specific date
    
    - **target_date**: Date in YYYY-MM-DD format
    """
    verify_api_key(x_api_key)
    
    try:
        date_obj = date.fromisoformat(target_date)
        return market_logic.get_market_hours_for_date(date_obj)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error(f"Error getting market hours for {target_date}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/raw")
async def get_raw_data(
    x_api_key: Optional[str] = Header(None)
):
    """
    Get raw scraped calendar data
    
    Returns the last scraper run information and raw data
    """
    verify_api_key(x_api_key)
    
    try:
        scraper_info = db.get_last_scraper_run()
        
        if not scraper_info:
            return {
                "message": "No scraper data available yet",
                "data": None
            }
        
        return {
            "last_updated": scraper_info['last_run'],
            "status": scraper_info['status'],
            "source": scraper_info['source'],
            "data": scraper_info['raw_data']
        }
    except Exception as e:
        logger.error(f"Error getting raw data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/is-open")
async def check_market_open(
    x_api_key: Optional[str] = Header(None)
):
    """
    Check if market is currently open
    
    Returns simple boolean status
    """
    verify_api_key(x_api_key)
    
    try:
        is_open, message = market_logic.is_market_open()
        return {
            "is_open": is_open,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking market status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


