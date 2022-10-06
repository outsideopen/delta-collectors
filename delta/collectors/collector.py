from abc import ABC, abstractmethod

from delta import logging


class Collector(ABC):
    def __init__(self, name):
        # create all variables
        self.name = str(name)
        self.logger = logging.getLogger(f"delta.{self.name}")

    @staticmethod
    @abstractmethod
    def lock():
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def should_run():
        raise NotImplementedError()

    @abstractmethod
    def run(self):
        pass
