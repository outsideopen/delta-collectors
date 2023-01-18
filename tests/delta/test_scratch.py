import pytest

from delta import scratch


def scratch_entry(ip="10.10.1.1", ip_last_found=0, tcp=None, udp=None):
    entry = {}
    entry["ip"] = ip
    entry["ip_last_found"] = ip_last_found

    if tcp:
        entry["tcp"] = tcp

    if udp:
        entry["udp"] = udp

    return entry


def scratch_sub_entry(
    nmap_last_scanned=0,
    hydra_last_scanned=0,
    ports=[],
    nmap_last_scanned_state="up",
    hydra_last_scanned_port=None,
):
    entry = {}
    entry["nmap_last_scanned"] = nmap_last_scanned
    entry["hydra_last_scanned"] = hydra_last_scanned
    entry["ports"] = ports
    entry["nmap_last_scanned_state"] = nmap_last_scanned_state
    entry["hydra_last_scanned_port"] = hydra_last_scanned_port

    return entry


def test_next_nmap():
    assert None == scratch.next_nmap([])

    assert ("10.10.1.1", "udp") == scratch.next_nmap(
        [scratch_entry(tcp=scratch_sub_entry(nmap_last_scanned=1))]
    )

    assert ("10.10.1.1", "tcp") == scratch.next_nmap(
        [scratch_entry(udp=scratch_sub_entry(nmap_last_scanned=1))]
    )

    tcp_1 = scratch_sub_entry(nmap_last_scanned=4)
    udp_1 = scratch_sub_entry(nmap_last_scanned=3)
    tcp_2 = scratch_sub_entry(nmap_last_scanned=1)
    udp_2 = scratch_sub_entry(nmap_last_scanned=2)

    assert ("10.10.1.2", "tcp") == scratch.next_nmap(
        [
            scratch_entry(ip="10.10.1.1", tcp=tcp_1, udp=udp_1),
            scratch_entry(ip="10.10.1.2", tcp=tcp_2, udp=udp_2),
        ]
    )


def test_next_hydra():
    # Empty scratch
    assert None == scratch.next_hydra([])

    # No open ports
    tcp_1 = scratch_sub_entry()
    udp_1 = scratch_sub_entry()
    assert ("10.10.1.1", "tcp", None) == scratch.next_hydra(
        [scratch_entry(tcp=tcp_1, udp=udp_1)]
    )

    # Get 2nd element in list of ports
    tcp_1 = scratch_sub_entry(hydra_last_scanned=2)
    udp_1 = scratch_sub_entry(
        hydra_last_scanned=1, hydra_last_scanned_port="621", ports=["621", "622"]
    )
    assert ("10.10.1.1", "udp", "622") == scratch.next_hydra(
        [scratch_entry(tcp=tcp_1, udp=udp_1)]
    )

    # Go past the end of the list
    tcp_1 = scratch_sub_entry(hydra_last_scanned=2)
    udp_1 = scratch_sub_entry(
        hydra_last_scanned=1, hydra_last_scanned_port="622", ports=["621", "622"]
    )
    assert ("10.10.1.1", "udp", "621") == scratch.next_hydra(
        [scratch_entry(tcp=tcp_1, udp=udp_1)]
    )

    # 2 Hosts
    tcp_1 = scratch_sub_entry(
        hydra_last_scanned=3, hydra_last_scanned_port="22", ports=["21", "22"]
    )
    udp_1 = scratch_sub_entry(
        hydra_last_scanned=4, hydra_last_scanned_port="621", ports=["621"]
    )
    tcp_2 = scratch_sub_entry(hydra_last_scanned=2)
    udp_2 = scratch_sub_entry(hydra_last_scanned=1, ports=["621", "622"])
    assert ("1.1.1.2", "udp", "621") == scratch.next_hydra(
        [
            scratch_entry(ip="1.1.1.1", tcp=tcp_1, udp=udp_1),
            scratch_entry(ip="1.1.1.2", tcp=tcp_2, udp=udp_2),
        ]
    )

    # Go past the end of the list
    tcp_1 = scratch_sub_entry(
        hydra_last_scanned=1, hydra_last_scanned_port="21", ports=["21", "22"]
    )
    udp_1 = scratch_sub_entry(
        hydra_last_scanned=2, hydra_last_scanned_port="621", ports=["621"]
    )
    tcp_2 = scratch_sub_entry(hydra_last_scanned=3)
    udp_2 = scratch_sub_entry(hydra_last_scanned=4, ports=["621", "622"])
    assert ("1.1.1.1", "tcp", "22") == scratch.next_hydra(
        [
            scratch_entry(ip="1.1.1.1", tcp=tcp_1, udp=udp_1),
            scratch_entry(ip="1.1.1.2", tcp=tcp_2, udp=udp_2),
        ]
    )
