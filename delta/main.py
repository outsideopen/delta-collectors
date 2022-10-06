from delta.migration import migrate_db
from delta.runner import Runner


def run():
    migrate_db()
    
    runner = Runner()
    runner.run()
