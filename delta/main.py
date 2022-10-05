from delta import logging
from delta.migration import migrate_db
from delta.scheduler import Scheduler


def run():
    migrate_db()
    
    logger = logging.getLogger(__name__)
    scheduler = Scheduler()
    scheduler.schedule()
