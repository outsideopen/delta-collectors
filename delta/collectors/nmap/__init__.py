from threading import Semaphore
from time import sleep

from delta.collectors.collector import Collector


class Nmap(Collector):
    semaphore = Semaphore()

    def __init__(self):
        super(Nmap, self).__init__(__name__)

    def lock():
        return Nmap.semaphore.acquire(blocking=False)

    def should_run():
        return True

    def run(self):
        try:
            self.logger.info("%%%% Nmap running...")
            sleep(3)
            self.logger.info("%%%% Nmap done")
        except Exception as e:
            self.logger.error(e, exc_info=True)
        finally:
            Nmap.semaphore.release()
