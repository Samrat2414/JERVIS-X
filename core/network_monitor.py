import socket

import psutil


def is_internet_connected():
    try:
        socket.create_connection(
            ("8.8.8.8", 53),
            timeout=3,
        ).close()

        return True

    except OSError:
        return False


def get_local_ip():
    try:
        hostname = socket.gethostname()

        return socket.gethostbyname(
            hostname
        )

    except Exception:
        return "Unavailable"


def get_network_io():
    counters = psutil.net_io_counters()

    return {
        "bytes_sent": counters.bytes_sent,
        "bytes_received": counters.bytes_recv,
        "mb_sent": round(
            counters.bytes_sent / (1024 ** 2),
            2,
        ),
        "mb_received": round(
            counters.bytes_recv / (1024 ** 2),
            2,
        ),
    }


def get_active_interfaces():
    stats = psutil.net_if_stats()
    addresses = psutil.net_if_addrs()

    interfaces = []

    for name, stat in stats.items():
        if not stat.isup:
            continue

        ip_address = "Unavailable"

        for address in addresses.get(
            name,
            [],
        ):
            if address.family == socket.AF_INET:
                ip_address = address.address
                break

        interfaces.append(
            {
                "name": name,
                "ip": ip_address,
                "speed": stat.speed,
            }
        )

    return interfaces


def get_network_summary():
    connected = is_internet_connected()
    local_ip = get_local_ip()
    io = get_network_io()
    interfaces = get_active_interfaces()

    connection_text = (
        "Connected"
        if connected
        else "Disconnected"
    )

    lines = [
        f"Internet: {connection_text}",
        f"Local IP: {local_ip}",
        f"Data Sent: {io['mb_sent']} MB",
        f"Data Received: {io['mb_received']} MB",
    ]

    if interfaces:
        lines.append("")
        lines.append("Active Interfaces:")

        for interface in interfaces:
            lines.append(
                f"- {interface['name']} "
                f"| IP: {interface['ip']} "
                f"| Speed: {interface['speed']} Mbps"
            )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_network_summary()
    )