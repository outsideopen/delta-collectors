import json
from datetime import datetime
from os import path
from threading import Semaphore

from delta import logging

FILE_NAME = "scratch.json"
lock = Semaphore()
logger = logging.getLogger(__name__)


def add_ip(ip):
    results = read_file()
    ips = get_ips()

    if ip not in ips:
        results.append(
            {
                "ip": ip,
                "ip_last_found": datetime.timestamp(datetime.now()) * 1000,
                "tcp": {"nmap_last_scanned": 0, "hydra_last_scanned": 0},
                "udp": {"nmap_last_scanned": 0, "hydra_last_scanned": 0},
            }
        )
    else:
        for result in results:
            if ip == result["ip"]:
                result["ip_last_found"] = datetime.timestamp(datetime.now()) * 1000

    write_file(results)


def get_ips():
    contents = read_file()

    return [sub["ip"] for sub in contents]


def next_nmap():
    results = read_file()

    if len(results) == 0:
        return None

    # `or 0` put elements with None at the top of the sort
    sorted_tcp = sorted(results, key=lambda e: (e["tcp"]["nmap_last_scanned"], e["ip"]))
    sorted_udp = sorted(results, key=lambda e: (e["udp"]["nmap_last_scanned"], e["ip"]))

    if (
        sorted_tcp[0]["tcp"]["nmap_last_scanned"]
        <= sorted_udp[0]["udp"]["nmap_last_scanned"]
    ):
        return (sorted_tcp[0]["ip"], "tcp")
    else:
        return (sorted_udp[0]["ip"], "udp")


def add_nmap_results(ip, protocol, ports, state):
    results = read_file()

    if state == "down":
        for result in results:
            if ip == result["ip"]:
                if(not result[protocol]["ports"]):
                    result[protocol]["ports"] = []

                result[protocol]["nmap_last_scanned_state"] = state
                result[protocol]["nmap_last_scanned"] = (
                    datetime.timestamp(datetime.now()) * 1000
                )
        write_file(results)

    else:

        for result in results:
            if ip == result["ip"]:
                result[protocol]["ports"] = ports
                result[protocol]["nmap_last_scanned_state"] = state
                result[protocol]["nmap_last_scanned"] = (
                    datetime.timestamp(datetime.now()) * 1000
                )

        write_file(results)


def next_hydra():
    results = read_file()

    if len(results) == 0:
        return None

    tcp_results = sorted(
        results, key=lambda e: (e["tcp"]["hydra_last_scanned"], e["ip"])
    )
    udp_results = sorted(
        results, key=lambda e: (e["udp"]["hydra_last_scanned"], e["ip"])
    )

    if (
        tcp_results[0]["tcp"]["hydra_last_scanned"]
        <= udp_results[0]["udp"]["hydra_last_scanned"]
    ):
        protocol = "tcp"
        result = tcp_results[0]
    else:
        protocol = "udp"
        result = udp_results[0]

    if result.get(protocol).get("nmap_last_scanned") > 0:
        ports = result.get(protocol).get("ports", [])
        if len(ports) == 0:
            return (result["ip"], None)

        port = result.get(protocol).get("hydra_last_scanned_port", ports[0])

        try:
            index = (ports.index(port) + 1) % len(ports)
        except ValueError:
            index = 0

        return (result["ip"], ports[index])


def update_hydra_last_scan(ip, port):
    results = read_file()

    for result in results:
        if ip == result["ip"]:

            for protocol in ("tcp", "udp"):
                ports = result.get(protocol, {}).get("ports")

                if ports is not None:
                    if not port:
                        result[protocol]["hydra_last_scanned"] = (
                            datetime.timestamp(datetime.now()) * 1000
                        )
                        write_file(results)

                    if port in ports:
                        result[protocol]["hydra_last_scanned_port"] = port

                        if ports.index(port) >= len(ports) - 1:
                            result[protocol]["hydra_last_scanned"] = (
                                datetime.timestamp(datetime.now()) * 1000
                            )
                        write_file(results)


def to_dict():
    return json.load(FILE_NAME)


def write_file(json_object):
    lock.acquire()

    json_object = json.dumps(json_object, indent=4)

    with open(FILE_NAME, "w") as f:
        f.write(json_object)

    lock.release()


def read_file():
    if not path.isfile(FILE_NAME):
        return []

    json_object = []
    with open(FILE_NAME, "r") as f:
        json_object = json.load(f)

    return json_object
