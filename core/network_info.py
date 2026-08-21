import socket
from pathlib import Path

import psutil


def _bytes_to_mb(value):
    return round(
        value / (1024 ** 2),
        2,
    )


def get_local_ip():
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM,
    )

    try:
        sock.connect(
            ("8.8.8.8", 80)
        )
        return sock.getsockname()[0]

    except OSError:
        try:
            return socket.gethostbyname(
                socket.gethostname()
            )
        except OSError:
            return "Unavailable"

    finally:
        sock.close()


def check_internet():
    try:
        connection = socket.create_connection(
            ("1.1.1.1", 53),
            timeout=2,
        )
        connection.close()
        return True

    except OSError:
        return False


def get_network_interfaces():
    addresses = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    interfaces = []

    for name, address_list in addresses.items():
        interface_stat = stats.get(name)

        ipv4 = []
        mac = "Unavailable"

        for address in address_list:
            if address.family == socket.AF_INET:
                ipv4.append(address.address)

            elif (
                hasattr(psutil, "AF_LINK")
                and address.family == psutil.AF_LINK
            ):
                mac = address.address

        interfaces.append(
            {
                "name": name,
                "is_up": (
                    interface_stat.isup
                    if interface_stat
                    else False
                ),
                "speed_mbps": (
                    interface_stat.speed
                    if interface_stat
                    else 0
                ),
                "ipv4": ipv4,
                "mac": mac,
            }
        )

    return interfaces


def get_network_info():
    counters = psutil.net_io_counters()

    return {
        "hostname": socket.gethostname(),
        "local_ip": get_local_ip(),
        "internet": check_internet(),
        "bytes_sent": counters.bytes_sent,
        "bytes_received": counters.bytes_recv,
        "sent_mb": _bytes_to_mb(
            counters.bytes_sent
        ),
        "received_mb": _bytes_to_mb(
            counters.bytes_recv
        ),
        "packets_sent": counters.packets_sent,
        "packets_received": counters.packets_recv,
        "interfaces": get_network_interfaces(),
    }


def get_network_report():
    info = get_network_info()

    internet_status = (
        "Connected"
        if info["internet"]
        else "Disconnected"
    )

    lines = [
        "JERVIS NETWORK INFORMATION",
        "",
        f"Hostname: {info['hostname']}",
        f"Local IP: {info['local_ip']}",
        f"Internet: {internet_status}",
        "",
        f"Data Sent: {info['sent_mb']} MB",
        f"Data Received: {info['received_mb']} MB",
        f"Packets Sent: {info['packets_sent']}",
        f"Packets Received: {info['packets_received']}",
        "",
        "NETWORK INTERFACES",
    ]

    for interface in info["interfaces"]:
        status = (
            "UP"
            if interface["is_up"]
            else "DOWN"
        )

        ip_text = (
            ", ".join(interface["ipv4"])
            if interface["ipv4"]
            else "No IPv4"
        )

        lines.extend(
            [
                "",
                f"Interface: {interface['name']}",
                f"Status: {status}",
                f"Speed: {interface['speed_mbps']} Mbps",
                f"IPv4: {ip_text}",
                f"MAC: {interface['mac']}",
            ]
        )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_network_report()
    )