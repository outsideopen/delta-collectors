import collections

import dbus


class Iwd:
    @staticmethod
    def connect(ssid):
        bus = dbus.SystemBus()

        networks = Iwd.list_networks()

        network = None
        for tmp_network in networks:
            if tmp_network["ssid"] == ssid:
                network = tmp_network
                break

        if network:
            network = dbus.Interface(
                bus.get_object("net.connman.iwd", network["device"]),
                "net.connman.iwd.Network",
            )

            network.Connect()
        else:
            raise Exception(f"Could not connect to wifi network: {ssid}")

    @staticmethod
    def disconnect(ssid):
        bus = dbus.SystemBus()

        networks = Iwd.list_networks()

        network = None
        for tmp_network in networks:
            if tmp_network["ssid"] == ssid:
                network = tmp_network
                break

        if network:
            device = dbus.Interface(
                bus.get_object("net.connman.iwd", network["station"]),
                "net.connman.iwd.Station",
            )

            device.Disconnect()
        else:
            raise Exception(f"Could not disconnect from wifi network: {ssid}")

    @staticmethod
    def list_networks():
        networks = []

        bus = dbus.SystemBus()

        manager = dbus.Interface(
            bus.get_object("net.connman.iwd", "/"), "org.freedesktop.DBus.ObjectManager"
        )
        objects = manager.GetManagedObjects()

        Obj = collections.namedtuple("Obj", ["interfaces", "children"])
        tree = Obj({}, {})
        for path in objects:
            node = tree
            elems = path.split("/")
            for subpath in ["/".join(elems[: l + 1]) for l in range(1, len(elems))]:
                if subpath not in node.children:
                    node.children[subpath] = Obj({}, {})
                node = node.children[subpath]
            node.interfaces.update(objects[path])

        root = (
            tree.children["/net"].children["/net/connman"].children["/net/connman/iwd"]
        )
        for path, phy in root.children.items():
            if "net.connman.iwd.Adapter" not in phy.interfaces:
                continue

            # properties = phy.interfaces["net.connman.iwd.Adapter"]

            for path2, device in phy.children.items():
                if "net.connman.iwd.Device" not in device.interfaces:
                    continue

                for interface in device.interfaces:
                    name = interface.rsplit(".", 1)[-1]
                    if name not in ("Device", "Station", "AccessPoint", "AdHoc"):
                        continue

                    if name != "Station":
                        continue

                    station = dbus.Interface(
                        bus.get_object("net.connman.iwd", path2),
                        "net.connman.iwd.Station",
                    )

                    for path3, rssi in station.GetOrderedNetworks():
                        properties2 = objects[path3]["net.connman.iwd.Network"]

                        networks.append(
                            {
                                "device": f"{path3}",
                                "security": f"{properties2['Type']}",
                                "signal_strength": rssi / 100,
                                "ssid": f"{properties2['Name']}",
                                "station": f"{path2}",
                            }
                        )
        return networks
