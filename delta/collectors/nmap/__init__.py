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
                if protocol == 'tcp':
                    output = nmap.nmap_tcp_scan(ip)
                if protocol == 'udp':
                    output = nmap.nmap_udp_scan(ip)

                self.logger.info(f"Output: {output}")

                q.put(
                    {
                        "collector": self.name,
                        "content": output,
                        "collectedAt": datetime.timestamp(datetime.now()) * 1000,
                    }
                )

                ports = self.__open_ports__(output, ip)
                scratch.add_nmap_results(ip, protocol, ports)
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
                open_ports.append(port_entry['portid'])
        return open_ports
