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
                "ports": None,
                "nmap_last_scanned": None,
                "hydra_last_scanned": None,
            }
        )
    else:
        for result in results:
            if ip == result["ip"]:
                result["ip_last_found"] = datetime.timestamp(datetime.now()) * 1000

    write_file(results)


def add_nmap_results(ip, ports):
    results = read_file()

    for result in results:
        if ip == result["ip"]:
            result["ports"] = ports
            result["nmap_last_scanned"] = datetime.timestamp(datetime.now()) * 1000

    write_file(results)


def next_hydra():
    results = read_file()

    if len(results) == 0:
        return None

    results.sort(key=lambda e: e.get("hydra_last_scanned", 0))

    for result in results:
        ports = result.get("tcp", {}).get("ports", [])
        if len(ports) > 0:
            port_index = (result.get("hydra_last_scanned_index", -1) + 1) % len(ports)

            return (result["ip"], ports[port_index])


def update_hydra_last_scan(ip, port):
    results = read_file()

    for result in results:
        if ip == result["ip"]:

            ports = result.get("tcp", {}).get("ports", [])
            port_index = ports.index(port)

            result["hydra_last_scanned_index"] = port_index
            if port_index >= len(ports) - 1:
                result["hydra_last_scanned"] = datetime.timestamp(datetime.now()) * 1000

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

    lock.acquire()

    json_object = []
    with open(FILE_NAME, "r") as f:
        json_object = json.load(f)

    lock.release()
    return json_object
