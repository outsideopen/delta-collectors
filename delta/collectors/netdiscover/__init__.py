import os
import re
import subprocess
import traceback
from datetime import datetime, timedelta
from threading import Semaphore

from delta import scratch
from delta.collector_queue import q
from delta.collectors.collector import Collector

SUBNET_INDEX_FILENAME = ".netdiscover_subnet_index"
LAST_RUN_FILE = ".netdiscover_subnet_last_run"
INTERVAL = 100
SUBNETS = [
    "10.0.0.0/24",
    "10.0.1.0/24",
    "10.10.0.0/24",
    "192.168.0.0/24",
    "192.168.1.0/24",
    "192.168.2.0/24",
    "192.168.100.0/24",
    "192.168.168.0/24",
    "192.168.254.0/24",
]

SHOULD_RUN = os.getenv("DELTA_NETDISCOVER_SHOULD_RUN", default=True) in [
    True,
    "True",
    "true",
    "1",
]


class Netdiscover(Collector):
    semaphore = Semaphore()

    def __init__(self):
        super(Netdiscover, self).__init__(__name__.split(".")[-1])

    @staticmethod
    def lock():
        return Netdiscover.semaphore.acquire(blocking=False)

    @staticmethod
    def should_run():
        last_run = Netdiscover.get_last_run(LAST_RUN_FILE)
        2_days_ago = (datetime.now() - timedelta(days=2)).timestamp()

        if last_run < 2_days_ago:
            return SHOULD_RUN
        else:
            return False

    def run(self):
        try:
            self.logger.debug(f"{self.name} running...")
            subnet_index = self.get_subnet_index()

            subnet = SUBNETS[subnet_index]

            cmd = f"arp-scan {subnet}"
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

            self.update_subnet_index((subnet_index + 1) % len(SUBNETS))

            if (subnet_index + 1) % len(SUBNETS) == 0:
                Netdiscover.update_last_run(LAST_RUN_FILE)

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
            Netdiscover.semaphore.release()

    def get_subnet_index(self):
        if not os.path.isfile(SUBNET_INDEX_FILENAME):
            return 0
        else:
            with open(SUBNET_INDEX_FILENAME, "r") as f:
                subnet_index = f.read()
                f.close()
                return int(subnet_index)

    def update_subnet_index(self, subnet_index):
        with open(SUBNET_INDEX_FILENAME, "w") as f:
            f.write(str(subnet_index))
            f.close()

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
