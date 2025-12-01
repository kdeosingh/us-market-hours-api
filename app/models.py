"""
Data models and schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class MarketStatus(str, Enum):
    """Market status enum"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    EARLY_CLOSE = "EARLY_CLOSE"


class MarketHoursResponse(BaseModel):
    """Market hours response schema"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    open_time_utc: Optional[str] = Field(None, description="Market open time in UTC ISO format")
    close_time_utc: Optional[str] = Field(None, description="Market close time in UTC ISO format")
    is_open: bool = Field(..., description="Whether market is open on this date")
    is_early_close: bool = Field(False, description="Whether market closes early")
    notes: str = Field("", description="Additional notes or holiday name")
    status: MarketStatus = Field(..., description="Current market status")


class WeekScheduleResponse(BaseModel):
    """Week schedule response schema"""
    start_date: str
    end_date: str
    days: List[MarketHoursResponse]


class NextEventResponse(BaseModel):
    """Next market event response"""
    event_type: str = Field(..., description="'open' or 'close'")
    event_time_utc: str = Field(..., description="Event time in UTC ISO format")
    time_until_seconds: int = Field(..., description="Seconds until event")
    next_date: str = Field(..., description="Date of next market day")
    is_early_close: bool = Field(False, description="Whether next close is early")
    notes: str = Field("", description="Additional notes")


class MarketDay(BaseModel):
    """Internal market day representation"""
    date: date
    open_time_et: Optional[str] = None  # "09:30:00"
    close_time_et: Optional[str] = None  # "16:00:00"
    is_open: bool = True
    is_early_close: bool = False
    holiday_name: Optional[str] = None
    notes: str = ""


class RawCalendarData(BaseModel):
    """Raw scraped calendar data"""
    source: str
    last_updated: datetime
    holidays: List[dict]
    early_closes: List[dict]



