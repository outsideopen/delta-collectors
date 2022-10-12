import os
import re
import subprocess
from datetime import datetime
from threading import Semaphore
from time import sleep

from delta import scratch
from delta.collector_queue import q
from delta.collectors.collector import Collector

INTERFACE = os.environ.get("DELTA_NETWORK_INTERFACE") or "wlan0"
PASSWORDS = "./data/hydra/common-passwords-short.txt"
USER_LIST = "./data/hydra/user-list.txt"
SNMP_WORD_LIST = "./data/hydra/snmp-word-list-short.txt"

SSH_PORTS = "22"
SNMP_PORTS = "161"


class Hydra(Collector):
    semaphore = Semaphore()

    def __init__(self):
        super(Hydra, self).__init__(__name__.split(".")[-1])

    @staticmethod
    def lock():
        return Hydra.semaphore.acquire(blocking=False)

    @staticmethod
    def should_run():
        return True

    def run(self):
        try:
            self.logger.debug(f"{self.name} running...")
            next = scratch.next_hydra()

            self.logger.debug(f"hydra input: {next}")
            if next:
                (ip, port) = next
                if not port:
                    scratch.update_hydra_last_scan(ip, port)
                    return

                self.logger.debug(f"{ip}, {port}")
                results = self.__hydra__(ip, port)
                if results is not None:
                    q.put(
                        {
                            "collector": self.name,
                            "content": results,
                            "collectedAt": datetime.timestamp(datetime.now()) * 1000,
                        }
                    )
                scratch.update_hydra_last_scan(ip, port)
            else:
                sleep(10)

        except Exception as e:
            self.logger.error(e, exc_info=True)
        finally:
            Hydra.semaphore.release()

    def __hydra__(self, ip, port):
        try:
            # connect to subnet, use X.X.X.227 because it is rarely used
            my_subnet_ip = "{}.227".format(re.sub(r"\.\d+$", "", ip))

            self.logger.debug(f"Join {ip} network, with IP {my_subnet_ip}")

            subprocess.run(
                f"ifconfig {INTERFACE}:1 {my_subnet_ip}",
                shell=True,
                stdout=subprocess.PIPE,
            )

            if port in SSH_PORTS:
                command = f"hydra -I -L {USER_LIST} -P {PASSWORDS} {ip} ssh 2>&1"
                self.logger.debug(command)
                output = subprocess.run(
                    command, shell=True, stdout=subprocess.PIPE
                ).stdout.decode("utf-8")

                parsed_output = self.parse_output(output)
                parsed_output["target"] = ip
                return parsed_output

            if port in SNMP_PORTS:
                command = f"hydra -I -P {SNMP_WORD_LIST} {ip} snmp 2>&1"
                output = subprocess.run(
                    command, shell=True, stdout=subprocess.PIPE
                ).stdout.decode("utf-8")

                parsed_output = self.parse_output(output)
                parsed_output["target"] = ip
                return parsed_output
        finally:
            # disconnect from subnet
            self.logger.debug(f"Release {ip} network, with IP {my_subnet_ip}")
            subprocess.run(
                f"ifconfig {INTERFACE}:1 down", shell=True, stdout=subprocess.PIPE
            )

    def parse_output(self, output):
        data = {}
        results = []
        for line in output.split("\n"):
            if not line.strip():
                continue

            if line.startswith("[DATA]"):
                for part in line.split(","):
                    if "login tries" in part:
                        temp = re.findall(r"\d+", part)
                        res = list(map(int, temp))
                        data["login_tries"] = res[0]
                        data["usernames_tested"] = res[1]
                        data["passwords_tested"] = res[2]
            elif line.startswith("1 of 1"):
                for part in line.split(","):
                    if "valid password" in part:
                        temp = re.findall(r"\d+", part)
                        res = list(map(int, temp))
                        data["successful_logins"] = res[0]
            elif line.startswith("[22][ssh]") or line.startswith("[161][snmp]"):
                parts = line.split()
                result = {}
                for i in range(1, len(parts), 2):
                    result[parts[i].replace(":", "")] = parts[i + 1]
                results.append(result)
            elif line.startswith("[ERROR]"):
                data["error"] = line
        data["results"] = results
        data["vulnerable"] = len(results) > 0
        return data
