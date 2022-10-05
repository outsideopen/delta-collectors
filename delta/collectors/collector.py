from abc import ABC, abstractmethod

from delta import logging


class Collector(ABC):
    def __init__(self, name):
        # create all variables
        self.name = str(name)
        self.logger = logging.getLogger(f"delta.{self.name}")

    @abstractmethod
    def lock(self):
        pass

    @abstractmethod
    def should_run(self):
        pass

    @abstractmethod
    def run(self):
        pass
