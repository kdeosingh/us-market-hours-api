"""
Business logic for market hours calculations
"""
from datetime import datetime, date, time, timedelta
from typing import Optional, Tuple
import pytz
import logging

from app.models import MarketDay, MarketHoursResponse, MarketStatus
from app.database import db

logger = logging.getLogger(__name__)

# Eastern timezone
ET = pytz.timezone('America/New_York')
UTC = pytz.utc


class MarketHoursLogic:
    """Business logic for market hours"""
    
    @staticmethod
    def et_to_utc(date_obj: date, time_str: str) -> datetime:
        """Convert Eastern time to UTC"""
        time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
        et_dt = ET.localize(datetime.combine(date_obj, time_obj))
        return et_dt.astimezone(UTC)
    
    @staticmethod
    def get_market_hours_for_date(target_date: date) -> MarketHoursResponse:
        """Get market hours for a specific date"""
        market_day = db.get_market_day(target_date)
        
        if not market_day:
            # Default for future dates without data
            if target_date.weekday() >= 5:
                is_open = False
                notes = "Weekend"
            else:
                is_open = True
                notes = "Regular trading hours (estimated)"
                market_day = MarketDay(
                    date=target_date,
                    open_time_et="09:30:00",
                    close_time_et="16:00:00",
                    is_open=True,
                    is_early_close=False,
                    notes=notes
                )
        
        if market_day and market_day.is_open:
            open_utc = MarketHoursLogic.et_to_utc(target_date, market_day.open_time_et)
            close_utc = MarketHoursLogic.et_to_utc(target_date, market_day.close_time_et)
            
            # Determine current status
            now = datetime.now(UTC)
            if now.date() == target_date:
                if now < open_utc:
                    status = MarketStatus.CLOSED
                elif now > close_utc:
                    status = MarketStatus.CLOSED
                else:
                    status = MarketStatus.EARLY_CLOSE if market_day.is_early_close else MarketStatus.OPEN
            else:
                status = MarketStatus.CLOSED
            
            return MarketHoursResponse(
                date=target_date.isoformat(),
                open_time_utc=open_utc.isoformat(),
                close_time_utc=close_utc.isoformat(),
                is_open=True,
                is_early_close=market_day.is_early_close,
                notes=market_day.notes,
                status=status
            )
        else:
            notes = market_day.notes if market_day else "Market closed"
            if market_day and market_day.holiday_name:
                notes = f"Market closed for {market_day.holiday_name}"
            
            return MarketHoursResponse(
                date=target_date.isoformat(),
                open_time_utc=None,
                close_time_utc=None,
                is_open=False,
                is_early_close=False,
                notes=notes,
                status=MarketStatus.CLOSED
            )
    
    @staticmethod
    def is_market_open(dt: datetime = None) -> Tuple[bool, str]:
        """Check if market is currently open"""
        if dt is None:
            dt = datetime.now(UTC)
        
        target_date = dt.date()
        market_day = db.get_market_day(target_date)
        
        if not market_day or not market_day.is_open:
            return False, "Market closed"
        
        open_utc = MarketHoursLogic.et_to_utc(target_date, market_day.open_time_et)
        close_utc = MarketHoursLogic.et_to_utc(target_date, market_day.close_time_et)
        
        if open_utc <= dt <= close_utc:
            return True, "Market open"
        else:
            return False, "Outside trading hours"
    
    @staticmethod
    def next_market_event() -> Optional[dict]:
        """Get next market open or close event"""
        now = datetime.now(UTC)
        today = now.date()
        
        # Check if market is open today
        market_day = db.get_market_day(today)
        
        if market_day and market_day.is_open:
            open_utc = MarketHoursLogic.et_to_utc(today, market_day.open_time_et)
            close_utc = MarketHoursLogic.et_to_utc(today, market_day.close_time_et)
            
            if now < open_utc:
                # Next event is today's open
                return {
                    'event_type': 'open',
                    'event_time_utc': open_utc.isoformat(),
                    'time_until_seconds': int((open_utc - now).total_seconds()),
                    'next_date': today.isoformat(),
                    'is_early_close': market_day.is_early_close,
                    'notes': market_day.notes
                }
            elif now < close_utc:
                # Next event is today's close
                return {
                    'event_type': 'close',
                    'event_time_utc': close_utc.isoformat(),
                    'time_until_seconds': int((close_utc - now).total_seconds()),
                    'next_date': today.isoformat(),
                    'is_early_close': market_day.is_early_close,
                    'notes': market_day.notes
                }
        
        # Look for next open day
        search_date = today + timedelta(days=1)
        for _ in range(30):  # Search next 30 days
            market_day = db.get_market_day(search_date)
            if market_day and market_day.is_open:
                open_utc = MarketHoursLogic.et_to_utc(search_date, market_day.open_time_et)
                return {
                    'event_type': 'open',
                    'event_time_utc': open_utc.isoformat(),
                    'time_until_seconds': int((open_utc - now).total_seconds()),
                    'next_date': search_date.isoformat(),
                    'is_early_close': market_day.is_early_close,
                    'notes': market_day.notes
                }
            search_date += timedelta(days=1)
        
        return None
    
    @staticmethod
    def get_week_schedule(start_date: date = None) -> list:
        """Get 7-day schedule starting from date"""
        if start_date is None:
            start_date = date.today()
        
        end_date = start_date + timedelta(days=6)
        
        schedule = []
        current = start_date
        
        while current <= end_date:
            schedule.append(MarketHoursLogic.get_market_hours_for_date(current))
            current += timedelta(days=1)
        
        return schedule


# Singleton instance
market_logic = MarketHoursLogic()




