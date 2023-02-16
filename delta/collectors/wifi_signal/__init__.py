import os
import time
import traceback
from datetime import datetime, timedelta
from threading import Semaphore

import dbus

from delta.collector_queue import q
from delta.collectors.collector import Collector
from delta.util.iwd import Iwd

LAST_RUN_FILE = ".wifi_signal_last_run"

SHOULD_RUN = os.getenv("DELTA_WIFI_SIGNAL_SHOULD_RUN", default=True) in [
    True,
    "True",
    "true",
    "1",
]


class WifiSignal(Collector):
    semaphore = Semaphore()

    def __init__(self):
        super(WifiSignal, self).__init__(__name__.split(".")[-1])

    @staticmethod
    def lock():
        return WifiSignal.semaphore.acquire(blocking=False)

    @staticmethod
    def should_run():
        last_run = WifiSignal.get_last_run(LAST_RUN_FILE)
        minutes_ago = (datetime.now() - timedelta(minutes=5)).timestamp()

        if last_run < minutes_ago:
            return SHOULD_RUN
        else:
            return False

    def run(self):
        try:
            self.logger.debug("Scanning wifi networks")
            response = Iwd.list_networks()
            parsed_response = [
                {
                    "ssid": x["ssid"],
                    "signal_strength": x["signal_strength"],
                    "security": x["security"],
                }
                for x in response
            ]
            self.logger.debug("Done scanning wifi networks")

            WifiSignal.update_last_run(LAST_RUN_FILE)
            q.put(
                {
                    "collector": self.name,
                    "content": parsed_response,
                    "collectedAt": datetime.timestamp(datetime.now()) * 1000,
                }
            )

        except Exception as e:
            tb = traceback.format_exc()
            q.put(
                {
                    "collector": "error",
                    "content": {
                        "collector": self.name,
                        "message": str(e),
                        "stacktrace": tb,
                    },
                    "collectedAt": datetime.timestamp(datetime.now()) * 1000,
                }
            )
            self.logger.error(e, exc_info=True)
        finally:
            WifiSignal.semaphore.release()
