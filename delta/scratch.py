import json
import operator
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


def next_nmap(results):
    if len(results) == 0:
        return None

    sorted_tcp = sorted(
        results, key=lambda e: (e.get("tcp", {}).get("nmap_last_scanned", 0), e["ip"])
    )
    sorted_udp = sorted(
        results, key=lambda e: (e.get("udp", {}).get("nmap_last_scanned", 0), e["ip"])
    )

    if sorted_tcp[0].get("tcp", {}).get("nmap_last_scanned", 0) <= sorted_udp[0].get(
        "udp", {}
    ).get("nmap_last_scanned", 0):
        return (sorted_tcp[0]["ip"], "tcp")
    else:
        return (sorted_udp[0]["ip"], "udp")


def update_nmap_results(results, ip, protocol, ports, state):
    for result in results:
        if ip == result["ip"]:
            if protocol not in result:
                result[protocol] = {}

            result[protocol]["ports"] = ports if ports else []

            result[protocol]["nmap_last_scanned_state"] = state
            result[protocol]["nmap_last_scanned"] = (
                datetime.timestamp(datetime.now()) * 1000
            )

    return results


def next_hydra(results):
    if len(results) == 0:
        return None

    tcp_results = sorted(
        results, key=lambda e: (e.get("tcp", {}).get("hydra_last_scanned", 0), e["ip"])
    )
    udp_results = sorted(
        results, key=lambda e: (e.get("udp", {}).get("hydra_last_scanned", 0), e["ip"])
    )

    oldest_tcp = tcp_results[0] if "tcp" in tcp_results[0] else None
    oldest_udp = udp_results[0] if "udp" in udp_results[0] else None

    if not oldest_tcp and not oldest_udp:
        return None
    if not oldest_tcp:
        protocol = "udp"
        result = oldest_udp
    elif not oldest_udp:
        protocol = "tcp"
        result = tcp_results[0]
    elif oldest_tcp["tcp"].get("hydra_last_scanned", 0) <= oldest_udp["udp"].get(
        "hydra_last_scanned", 0
    ):
        protocol = "tcp"
        result = tcp_results[0]
    else:
        protocol = "udp"
        result = udp_results[0]

    ports = result[protocol].get("ports", [])
    if len(ports) == 0:
        return (result["ip"], protocol, None)

    port = result[protocol].get("hydra_last_scanned_port", ports[0])

    try:
        index = (ports.index(port) + 1) % len(ports)
    except ValueError:
        index = 0

    return (result["ip"], protocol, ports[index])


def update_hydra_last_scan(input, ip, protocol, port):
    results = input.copy()

    for result in results:
        if ip == result["ip"]:
            ports = result.get(protocol, {}).get("ports", [])
            if not port:
                result[protocol]["hydra_last_scanned"] = (
                    datetime.timestamp(datetime.now()) * 1000
                )

            elif port in ports:
                result[protocol]["hydra_last_scanned_port"] = port

                if ports.index(port) >= len(ports) - 1:
                    result[protocol]["hydra_last_scanned"] = (
                        datetime.timestamp(datetime.now()) * 1000
                    )

            else:
                raise Exception(
                    f"Trying to scan port {port}, on host {ip}, but it is not in the available ports list: {ports}"
                )
    return results


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
