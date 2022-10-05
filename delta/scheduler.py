import importlib
import pkgutil
import queue
import threading
from time import sleep
import delta.collectors
from delta import logging


class Scheduler:
    def __init__(self):
        self.collector_names = []
        self.logger = logging.getLogger(f"{__name__}")
        self.logger.info("Start Scheduler")

        self.jobqueue = queue.Queue()

        for importer, modname, ispkg in pkgutil.iter_modules(delta.collectors.__path__):
            if ispkg:
                self.collector_names.append(modname)

    def instantiate_collector(self, name):
        __module__ = importlib.import_module(
            f".{name}", package=delta.collectors.__name__
        )
        __class__ = getattr(__module__, name.capitalize())
        return __class__()

    def worker_main(self):
        while True:
            job_func = self.jobqueue.get()
            job_func()
            self.jobqueue.task_done()

    def schedule(self):
        for i in range(0, 3):
            worker_thread = threading.Thread(target=self.worker_main)
            worker_thread.start()

        while True:
            self.logger.info(f"Queue: {list(self.jobqueue.queue)}")
            for collector_name in self.collector_names:
                collector = self.instantiate_collector(collector_name)

                if collector.should_run() and collector.lock():
                    self.jobqueue.put(collector.run)

            sleep(1)
