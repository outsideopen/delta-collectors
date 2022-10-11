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

            ip = scratch.next_ip_to_nmap()
            self.logger.debug(ip)

            if ip:
                results = nmap3.NmapScanTechniques().nmap_syn_scan(ip, "-sU")
                self.logger.info(f"Output: {results}")
                q.put(
                    {
                        "collector": self.name,
                        "content": results,
                        "collectedAt": datetime.timestamp(datetime.now()) * 1000,
                    }
                )

                ports = self.__open_ports__(results, ip)
                scratch.add_nmap_results(ip, ports)
            else:
                sleep(10)

        except Exception as e:
            self.logger.error(e, exc_info=True)
        finally:
            Nmap.semaphore.release()

    def __open_ports__(self, results, ip):
        open_ports = []

        for port_entry in results.get(ip, {}).get("ports", {}):
            if port_entry["state"] == "open":
                open_ports.append(f"{port_entry['portid']}/{port_entry['protocol']}")
        return open_ports
