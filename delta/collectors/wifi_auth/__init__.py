import os
import time
import traceback
from datetime import datetime, timedelta
from threading import Semaphore

from delta.collector_queue import q
from delta.collectors.collector import Collector
from delta.util.iwd import Iwd

LAST_RUN_FILE = ".wifi_auth_last_run"

SHOULD_RUN = os.getenv("DELTA_WIFI_AUTH_SHOULD_RUN", default=True) in [
    True,
    "True",
    "true",
    "1",
]

WIFI_SSID = os.getenv("DELTA_WIFI_AUTH_SSID", default=None)


class WifiAuth(Collector):
    semaphore = Semaphore()

    def __init__(self):
        super(WifiAuth, self).__init__(__name__.split(".")[-1])

    @staticmethod
    def lock():
        return WifiAuth.semaphore.acquire(blocking=False)

    @staticmethod
    def should_run():
        if not WIFI_SSID:
            return False

        last_run = WifiAuth.get_last_run(LAST_RUN_FILE)
        minutes_ago = (datetime.now() - timedelta(minutes=5)).timestamp()

        if last_run < minutes_ago:
            return SHOULD_RUN
        else:
            return False

    def run(self):
        try:
            ssid = WIFI_SSID
            self.logger.debug(f"Connecting to wifi network: {ssid}")
            tic = time.perf_counter()
            Iwd.connect(ssid)
            toc = time.perf_counter()
            Iwd.disconnect(ssid)

            self.logger.debug(f"Disconnecting from wifi network: {ssid}")

            WifiAuth.update_last_run(LAST_RUN_FILE)
            q.put(
                {
                    "collector": "wifi_auth",
                    "content": {"ssid": ssid, "auth_time": toc - tic},
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
            WifiAuth.semaphore.release()
