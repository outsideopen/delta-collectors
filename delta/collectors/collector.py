import os
from abc import ABC, abstractmethod
from datetime import datetime

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

    @staticmethod
    def get_last_run(file_name):
        if not os.path.isfile(file_name):
            return 0
        else:
            with open(file_name, "r") as f:
                last_run = f.read()
                f.close()
                return float(last_run)

    @staticmethod
    def update_last_run(file_name):
        with open(file_name, "w") as f:
            f.write(str(datetime.now().timestamp()))
            f.close()
