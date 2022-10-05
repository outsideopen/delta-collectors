from threading import Semaphore
from time import sleep

from delta.collectors.collector import Collector


class Hydra(Collector):
    semaphore = Semaphore()

    def __init__(self):
        super(Hydra, self).__init__(__name__)

    def lock(self):
        return Hydra.semaphore.acquire(blocking=False)

    def should_run(self):
        return True

    def run(self):
        try:
            self.logger.info("**** Hydra running...")
            sleep(5)
            # raise Exception()
            self.logger.info("**** Hydra done")

        except Exception as e:
            self.logger.error(e, exc_info=True)
        finally:
            Hydra.semaphore.release()
