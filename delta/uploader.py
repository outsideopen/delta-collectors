import os
import threading
from time import sleep

import requests

from delta import logging
from delta.collector_queue import q


class Uploader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_token = os.getenv("DELTA_API_TOKEN", default=None)
        self.api_url = os.getenv(
            "DELTA_API_URL", default="http://localhost:4000/api/upload"
        )

    def uploader(self):
        while True:
            size = q.size
            try:
                items = []
                for i in range(0, size):
                    items.append(q.get())

                self.logger.debug(items)

                self.__upload__(items)
            except Exception as e:
                self.logger.error(e)
            sleep(10)

    def run(self):
        worker_thread = threading.Thread(target=self.uploader, daemon=True)
        worker_thread.start()

    def __upload__(self, items):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        response = requests.post(self.api_url, headers=headers, json=items)
        response.raise_for_status()
