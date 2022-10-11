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


def get_ips():
    contents = read_file()

    return [sub["ip"] for sub in contents]


def next_ip_to_nmap():
    results = read_file()
    # `or 0` put elements with None at the top of the sort
    results.sort(key=lambda e: e["ip_last_found"] or 0)

    return results[0]["ip"] if len(results) > 0 else None


def next_ip_to_hydra():
    pass


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
