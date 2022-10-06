from time import sleep

from threading import Semaphore
from delta.collectors.collector import Collector


class Netdiscover(Collector):
    semaphore = Semaphore()

    def __init__(self):
        super(Netdiscover, self).__init__(__name__)

    @staticmethod
    def lock():
        return Netdiscover.semaphore.acquire(blocking=False)

        return False

    @staticmethod
    def should_run():
        return True

    def run(self):
        try:
            self.logger.info("!!!! Netdiscover running...")
            sleep(2)
            self.logger.info("!!!! Netdiscover done")
        except Exception as e:
            self.logger.error(e, exc_info=True)
        finally:
            Netdiscover.semaphore.release()
