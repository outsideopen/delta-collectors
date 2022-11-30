import ipaddress
from datetime import datetime
from threading import Semaphore
from time import sleep

import nmap3

from delta import scratch
from delta.collector_queue import q
from delta.collectors.collector import Collector


class Nmap(Collector):
    semaphore = Semaphore()

    def __init__(self):
        super(Nmap, self).__init__(__name__.split(".")[-1])

    @staticmethod
    def lock():
        return Nmap.semaphore.acquire(blocking=False)

    @staticmethod
    def should_run():
        return True

    def run(self):
        try:
            self.logger.debug(f"{self.name} running...")

            results = scratch.next_nmap()
            if results:
                self.logger.debug(f"nmap input: {results}")
                (ip, protocol) = results

                nmap = nmap3.NmapScanTechniques()
                if protocol == "tcp":
                    output = nmap.nmap_tcp_scan(ip)
                if protocol == "udp":
                    output = nmap.nmap_udp_scan(ip)

                parsed_output = self.__parse_output__(output)

                self.logger.info(f"Output: {parsed_output}")

                q.put(
                    {
                        "collector": self.name,
                        "content": parsed_output,
                        "collectedAt": datetime.timestamp(datetime.now()) * 1000,
                    }
                )

                state = parsed_output['state']['state']
                ports = self.__open_ports__(output, ip)
                scratch.add_nmap_results(ip, protocol, ports, state)
            else:
                sleep(10)

        except Exception as e:
            self.logger.error(e, exc_info=True)
        finally:
            Nmap.semaphore.release()

    def __open_ports__(self, results, ip):
        open_ports = []

        for port_entry in results.get(ip, {}).get("ports", []):
            if port_entry["state"] == "open":
                open_ports.append(port_entry["portid"])
        return open_ports

    def __parse_output__(self, output):
        parsed_output = {}

        keys = output.keys()

        ips = []
        other_keys = []
        for key in keys:
            if self.__get_ip__(key):
                ips.append(key)
            else:
                other_keys.append(key)

        if len(ips) > 1:
            raise Exception("Nmap results should not contain more than 1 IP!")

        ip = ips[0] if ips else None

        if ip:
            parsed_output = output[ip]
            parsed_output["ip"] = ip

        return parsed_output

    def __get_ip__(self, maybe_ip):
        try:
            ipaddress.ip_address(maybe_ip)
            return True

        except ValueError:
            return False
