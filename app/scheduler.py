"""
APScheduler setup for daily scraping
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from app.scraper import scraper
from app.config import settings

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def scheduled_scraper_job():
    """Job to run scraper"""
    logger.info("Running scheduled scraper job")
    try:
        scraper.run_scraper()
    except Exception as e:
        logger.error(f"Scheduled scraper job failed: {e}")


def start_scheduler():
    """Start the scheduler"""
    if not settings.SCRAPER_ENABLED:
        logger.info("Scraper disabled in config")
        return
    
    # Run scraper immediately on startup
    logger.info("Running initial scraper on startup")
    try:
        scraper.run_scraper()
    except Exception as e:
        logger.error(f"Initial scraper run failed: {e}")
    
    # Schedule daily at configured hour (UTC)
    scheduler.add_job(
        scheduled_scraper_job,
        CronTrigger(hour=settings.SCRAPER_SCHEDULE_HOUR, minute=0),
        id='daily_scraper',
        name='Daily market hours scraper',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"Scheduler started. Daily scraper will run at {settings.SCRAPER_SCHEDULE_HOUR}:00 UTC")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")



