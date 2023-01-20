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


def test_update_nmap_results():
    result = scratch.update_nmap_results(
        [scratch_entry()], "10.10.1.1", "tcp", ["21", "22"], "up"
    )

    assert result[0]["ip"] == "10.10.1.1"
    assert result[0]["tcp"]["ports"] == ["21", "22"]
    assert result[0]["tcp"]["nmap_last_scanned_state"] == "up"
    assert result[0]["tcp"]["nmap_last_scanned"] > 0

    entry_1 = scratch_entry()
    entry_2 = scratch_entry(
        ip="10.10.1.2", tcp=scratch_sub_entry(ports=["20", "21", "22"])
    )
    result = scratch.update_nmap_results(
        [entry_1, entry_2], "10.10.1.2", "tcp", ["53"], "up"
    )

    assert result[1]["ip"] == "10.10.1.2"
    assert result[1]["tcp"]["ports"] == ["53"]


def test_next_nmap():
    assert scratch.next_nmap([]) == None

    assert scratch.next_nmap(
        [scratch_entry(tcp=scratch_sub_entry(nmap_last_scanned=1))]
    ) == ("10.10.1.1", "udp")
    assert scratch.next_nmap(
        [scratch_entry(udp=scratch_sub_entry(nmap_last_scanned=1))]
    ) == ("10.10.1.1", "tcp")

    tcp_1 = scratch_sub_entry(nmap_last_scanned=4)
    udp_1 = scratch_sub_entry(nmap_last_scanned=3)
    tcp_2 = scratch_sub_entry(nmap_last_scanned=1)
    udp_2 = scratch_sub_entry(nmap_last_scanned=2)

    assert scratch.next_nmap(
        [
            scratch_entry(ip="10.10.1.1", tcp=tcp_1, udp=udp_1),
            scratch_entry(ip="10.10.1.2", tcp=tcp_2, udp=udp_2),
        ]
    ) == ("10.10.1.2", "tcp")


def test_next_hydra():
    # Empty scratch
    assert scratch.next_hydra([]) == None

    # No open ports
    tcp_1 = scratch_sub_entry()
    udp_1 = scratch_sub_entry()
    assert scratch.next_hydra([scratch_entry(tcp=tcp_1, udp=udp_1)]) == (
        "10.10.1.1",
        "tcp",
        None,
    )

    # Get 2nd element in list of ports
    tcp_1 = scratch_sub_entry(hydra_last_scanned=2)
    udp_1 = scratch_sub_entry(
        hydra_last_scanned=1, hydra_last_scanned_port="621", ports=["621", "622"]
    )
    assert scratch.next_hydra([scratch_entry(tcp=tcp_1, udp=udp_1)]) == (
        "10.10.1.1",
        "udp",
        "622",
    )

    # Go past the end of the list
    tcp_1 = scratch_sub_entry(hydra_last_scanned=2)
    udp_1 = scratch_sub_entry(
        hydra_last_scanned=1, hydra_last_scanned_port="622", ports=["621", "622"]
    )
    assert scratch.next_hydra([scratch_entry(tcp=tcp_1, udp=udp_1)]) == (
        "10.10.1.1",
        "udp",
        "621",
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
    assert scratch.next_hydra(
        [
            scratch_entry(ip="1.1.1.1", tcp=tcp_1, udp=udp_1),
            scratch_entry(ip="1.1.1.2", tcp=tcp_2, udp=udp_2),
        ]
    ) == ("1.1.1.2", "udp", "621")

    # Go past the end of the list
    tcp_1 = scratch_sub_entry(
        hydra_last_scanned=1, hydra_last_scanned_port="21", ports=["21", "22"]
    )
    udp_1 = scratch_sub_entry(
        hydra_last_scanned=2, hydra_last_scanned_port="621", ports=["621"]
    )
    tcp_2 = scratch_sub_entry(hydra_last_scanned=3)
    udp_2 = scratch_sub_entry(hydra_last_scanned=4, ports=["621", "622"])
    assert scratch.next_hydra(
        [
            scratch_entry(ip="1.1.1.1", tcp=tcp_1, udp=udp_1),
            scratch_entry(ip="1.1.1.2", tcp=tcp_2, udp=udp_2),
        ]
    ) == ("1.1.1.1", "tcp", "22")


def test_update_hydra_last_scan():
    entry_1 = scratch_entry(tcp=scratch_sub_entry(ports=["21"]))
    with pytest.raises(Exception) as e:
        scratch.update_hydra_last_scan([entry_1], "10.10.1.1", "tcp", "22")
    assert (
        "Trying to scan port 22, on host 10.10.1.1, but it is not in the available ports list: ['21']"
        == str(e.value)
    )

    entry_1 = scratch_entry(tcp=scratch_sub_entry(ports=["21", "22"]))
    results = scratch.update_hydra_last_scan([entry_1], "10.10.1.1", "tcp", "21")

    assert len(results) == 1

    assert results[0]["tcp"]["hydra_last_scanned"] == 0
    assert results[0]["tcp"]["hydra_last_scanned_port"] == "21"

    entry_1 = scratch_entry(ip="1.1.1.1", tcp=scratch_sub_entry(ports=["21", "22"]))
    entry_2 = scratch_entry(ip="1.1.1.2", tcp=scratch_sub_entry(ports=["55", "66"]))
    results = scratch.update_hydra_last_scan([entry_1, entry_2], "1.1.1.2", "tcp", "66")

    assert len(results) == 2

    assert results[0]["tcp"]["hydra_last_scanned"] == 0
    assert results[0]["tcp"]["hydra_last_scanned_port"] == None

    assert results[1]["tcp"]["hydra_last_scanned"] > 0
    assert results[1]["tcp"]["hydra_last_scanned_port"] == "66"
