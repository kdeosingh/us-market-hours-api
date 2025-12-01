"""
Database operations using SQLite
"""
import sqlite3
import json
from datetime import date, datetime
from typing import List, Optional
import logging
from contextlib import contextmanager

from app.config import settings
from app.models import MarketDay

logger = logging.getLogger(__name__)


class MarketHoursDB:
    """Database manager for market hours data"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DB_PATH
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Market days table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_days (
                    date TEXT PRIMARY KEY,
                    open_time_et TEXT,
                    close_time_et TEXT,
                    is_open INTEGER,
                    is_early_close INTEGER,
                    holiday_name TEXT,
                    notes TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # Scraper metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraper_metadata (
                    id INTEGER PRIMARY KEY,
                    last_run TEXT,
                    status TEXT,
                    source TEXT,
                    raw_data TEXT
                )
            """)
            
            logger.info("Database initialized")
    
    def save_market_day(self, market_day: MarketDay):
        """Save or update a market day"""
        now = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO market_days 
                (date, open_time_et, close_time_et, is_open, is_early_close, 
                 holiday_name, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 
                        COALESCE((SELECT created_at FROM market_days WHERE date = ?), ?), ?)
            """, (
                market_day.date.isoformat(),
                market_day.open_time_et,
                market_day.close_time_et,
                1 if market_day.is_open else 0,
                1 if market_day.is_early_close else 0,
                market_day.holiday_name,
                market_day.notes,
                market_day.date.isoformat(),
                now,
                now
            ))
    
    def save_market_days(self, market_days: List[MarketDay]):
        """Batch save market days"""
        for day in market_days:
            self.save_market_day(day)
        logger.info(f"Saved {len(market_days)} market days")
    
    def get_market_day(self, target_date: date) -> Optional[MarketDay]:
        """Get market day for a specific date"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM market_days WHERE date = ?
            """, (target_date.isoformat(),))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return MarketDay(
                date=date.fromisoformat(row['date']),
                open_time_et=row['open_time_et'],
                close_time_et=row['close_time_et'],
                is_open=bool(row['is_open']),
                is_early_close=bool(row['is_early_close']),
                holiday_name=row['holiday_name'],
                notes=row['notes'] or ""
            )
    
    def get_market_days_range(self, start_date: date, end_date: date) -> List[MarketDay]:
        """Get market days in a date range"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM market_days 
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            """, (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            return [
                MarketDay(
                    date=date.fromisoformat(row['date']),
                    open_time_et=row['open_time_et'],
                    close_time_et=row['close_time_et'],
                    is_open=bool(row['is_open']),
                    is_early_close=bool(row['is_early_close']),
                    holiday_name=row['holiday_name'],
                    notes=row['notes'] or ""
                )
                for row in rows
            ]
    
    def save_scraper_run(self, status: str, source: str, raw_data: dict = None):
        """Save scraper run metadata"""
        now = datetime.utcnow().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scraper_metadata (last_run, status, source, raw_data)
                VALUES (?, ?, ?, ?)
            """, (now, status, source, json.dumps(raw_data) if raw_data else None))
    
    def get_last_scraper_run(self) -> Optional[dict]:
        """Get last scraper run info"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scraper_metadata 
                ORDER BY last_run DESC LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'last_run': row['last_run'],
                'status': row['status'],
                'source': row['source'],
                'raw_data': json.loads(row['raw_data']) if row['raw_data'] else None
            }


# Singleton instance
db = MarketHoursDB()



