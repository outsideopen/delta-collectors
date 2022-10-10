import importlib
import pkgutil
import queue
import threading
from time import sleep

import delta.collectors
from delta import logging


class Runner:
    def __init__(self):
        self.__nr_of_threads__ = 3
        self.threads = []
        self.collector_names = []
        self.logger = logging.getLogger(f"{__name__}")
        self.logger.debug("Start Runner")

        self.jobqueue = queue.Queue()

        for importer, modname, ispkg in pkgutil.iter_modules(delta.collectors.__path__):
            if ispkg:
                self.collector_names.append(modname)

    def get_class(self, name):
        __module__ = importlib.import_module(
            f".{name}", package=delta.collectors.__name__
        )
        __class__ = getattr(__module__, name.capitalize())
        return __class__

    def runner(self):
        while True:
            job_func = self.jobqueue.get()
            job_func()
            self.jobqueue.task_done()

    def run(self):
        for i in range(0, self.__nr_of_threads__):
            worker_thread = threading.Thread(target=self.runner, daemon=True)
            worker_thread.start()
            self.threads.append(worker_thread)

        try:
            while True:
                self.logger.debug(f"Queue: {list(self.jobqueue.queue)}")
                for collector_name in self.collector_names:
                    Klass = self.get_class(collector_name)

                    if Klass.should_run() and Klass.lock():
                        instance = Klass()
                        self.jobqueue.put(instance.run)

                sleep(1)
        except KeyboardInterrupt as e:
            self.logger.info("Bye!")
