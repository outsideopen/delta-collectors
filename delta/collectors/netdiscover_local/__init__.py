import os
import re
import subprocess
import traceback
from datetime import datetime
from threading import Semaphore

from delta import scratch
from delta.collector_queue import q
from delta.collectors.collector import Collector

INTERVAL = 100

SHOULD_RUN = os.getenv("DELTA_NETDISCOVER_LOCAL_SHOULD_RUN", default=True) in [
    True,
    "True",
    "true",
    "1",
]


class NetdiscoverLocal(Collector):
    semaphore = Semaphore()

    def __init__(self):
        super(NetdiscoverLocal, self).__init__(__name__.split(".")[-1])

    @staticmethod
    def lock():
        return NetdiscoverLocal.semaphore.acquire(blocking=False)

    @staticmethod
    def should_run():
        return SHOULD_RUN

    def run(self):
        try:
            self.logger.debug(f"{self.name} running...")

            cmd = f"arp-scan --local"
            cmd += f" --interval={INTERVAL}"
            self.logger.debug(f"Command: {cmd}")

            output = subprocess.run(
                cmd, shell=True, stdout=subprocess.PIPE, check=True
            ).stdout.decode("utf-8")

            for line in output.split("\n"):
                parsed_output = self.parse_line(line)
                self.logger.info(f"Output: {parsed_output}")

                if parsed_output:
                    q.put(
                        {
                            "collector": self.name,
                            "content": parsed_output,
                            "collectedAt": datetime.timestamp(datetime.now()) * 1000,
                        }
                    )
                    scratch.add_ip(parsed_output["ip"])

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
            NetdiscoverLocal.semaphore.release()

    def parse_line(self, line):
        regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
        parsed_output = {}

        parts = line.split("\t")
        parts = list(filter(("").__ne__, parts))

        if (
            len(parts) < 3
            or not re.search(regex, parts[0])
            or parts[0].startswith("0.0.0")
        ):
            return

        # IP Address
        parsed_output["ip"] = parts[0]

        # MAC Address
        parsed_output["mac_address"] = parts[1]

        # Hostname
        name = ""
        max_index = len(parts)
        for ii in range(2, max_index):
            name += parts[ii] + " "
        if name != "":
            name = name[:-1]
        parsed_output["vendor"] = name

        if "DUP" in name:
            return
        return parsed_output
