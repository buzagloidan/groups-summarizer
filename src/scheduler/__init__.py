import asyncio
import logging
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel.ext.asyncio.session import AsyncSession

from summarize_and_send_to_groups import send_daily_summaries_to_monitor
from whatsapp import WhatsAppClient

logger = logging.getLogger(__name__)


class DailySummaryScheduler:
    def __init__(self, session_factory, whatsapp: WhatsAppClient, monitor_phone: str):
        self.session_factory = session_factory
        self.whatsapp = whatsapp
        self.monitor_phone = monitor_phone
        self.scheduler = AsyncIOScheduler()

    async def send_daily_summaries_job(self):
        """Job function that gets executed daily at 22:00"""
        logger.info("Starting daily summary job")
        try:
            async with self.session_factory() as session:
                await send_daily_summaries_to_monitor(session, self.whatsapp, self.monitor_phone)
            logger.info("Daily summary job completed successfully")
        except Exception as e:
            logger.error(f"Error in daily summary job: {e}")

    def start(self):
        """Start the scheduler with daily job at 22:00"""
        self.scheduler.add_job(
            self.send_daily_summaries_job,
            CronTrigger(hour=22, minute=0),  # 22:00 every day
            id='daily_summaries',
            name='Daily Group Summaries',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Daily summary scheduler started - will run at 22:00 every day")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Daily summary scheduler stopped")

    async def trigger_manual_summary(self):
        """Manually trigger the daily summary (for testing or manual execution)"""
        logger.info("Manually triggering daily summary")
        await self.send_daily_summaries_job()