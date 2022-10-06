import os
import sqlite3
import pkg_resources

from digital_hydrant import logging
from digital_hydrant.config import db_path


def migrate_db(cursor=None):
    logger = logging.getLogger(__name__)

    def get_script_version(path):
        return int(path.split("_")[0].split("/")[1])

    if not cursor:
        try:
            cursor = sqlite3.connect(db_path, timeout=10).cursor()
        except Exception as e:
            logger.critical(f"Failed to initialize database: {e}")
            exit(1)

    current_version = cursor.execute("pragma user_version").fetchone()[0]

    migrations_path = pkg_resources.resource_filename("digital_hydrant", "migrations")
    migration_files = list(os.listdir(migrations_path))
    for migration in sorted(migration_files):
        path = f"migrations/{migration}"
        migration_version = get_script_version(path)

        if migration_version > current_version:
            logger.debug(f"Applying migration {migration_version}")
            with open(f"{migrations_path}/{migration}", "r") as f:
                cursor.executescript(f.read())
                cursor.execute(f"PRAGMA user_version={migration_version}")
                logger.debug(f"Database now at version {migration_version}")
        else:
            logger.debug(f"Migration {migration_version} already applied")
