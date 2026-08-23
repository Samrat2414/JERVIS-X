import socket

import psutil


NETWORK_WARNING_SENT_MB = 250.0
NETWORK_WARNING_RECEIVED_MB = 1000.0


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


def get_active_network_interfaces():
    return [
        interface
        for interface in get_network_interfaces()
        if interface.get("is_up")
    ]


def get_primary_interface():
    active = get_active_network_interfaces()

    if not active:
        return None

    local_ip = get_local_ip()

    for interface in active:
        if local_ip in interface.get("ipv4", []):
            return interface

    for interface in active:
        ipv4 = interface.get("ipv4", [])

        if any(
            not address.startswith("127.")
            and not address.startswith("169.254.")
            for address in ipv4
        ):
            return interface

    return active[0]


def get_network_health():
    info = get_network_info()
    active = [
        interface
        for interface in info["interfaces"]
        if interface.get("is_up")
    ]

    problems = []
    recommendations = []

    if not info["internet"]:
        problems.append(
            "Internet connection is unavailable."
        )
        recommendations.append(
            "Check Wi-Fi, Ethernet, router, or ISP connectivity."
        )

    if not active:
        problems.append(
            "No active network interface was detected."
        )
        recommendations.append(
            "Enable Wi-Fi or connect an Ethernet adapter."
        )

    if info["local_ip"] in (
        "Unavailable",
        "127.0.0.1",
    ):
        problems.append(
            "A usable local network IP address was not detected."
        )
        recommendations.append(
            "Reconnect the active network adapter or renew the IP configuration."
        )

    if info["local_ip"].startswith("169.254."):
        problems.append(
            "The system appears to be using an automatic private IP address."
        )
        recommendations.append(
            "Check DHCP/router connectivity because Windows may not have received a normal local IP address."
        )

    primary = get_primary_interface()

    if primary:
        speed = primary.get(
            "speed_mbps",
            0,
        )

        if speed <= 0:
            recommendations.append(
                "The active adapter did not report a link speed."
            )

        elif speed < 50:
            recommendations.append(
                "The active network link speed is relatively low."
            )

    if not problems:
        status = "Healthy"
    elif info["internet"] and active:
        status = "Warning"
    else:
        status = "Critical"

    if not recommendations:
        recommendations.append(
            "Network connectivity appears normal."
        )

    return {
        "status": status,
        "internet": info["internet"],
        "local_ip": info["local_ip"],
        "active_interfaces": active,
        "primary_interface": primary,
        "problems": problems,
        "recommendations": recommendations,
    }


def get_network_activity_analysis():
    info = get_network_info()

    notes = []

    if info["sent_mb"] >= NETWORK_WARNING_SENT_MB:
        notes.append(
            (
                f"Total transmitted data is "
                f"{info['sent_mb']} MB since system startup."
            )
        )

    if info["received_mb"] >= NETWORK_WARNING_RECEIVED_MB:
        notes.append(
            (
                f"Total received data is "
                f"{info['received_mb']} MB since system startup."
            )
        )

    if not notes:
        notes.append(
            "No unusual cumulative network activity threshold was detected."
        )

    return {
        "sent_mb": info["sent_mb"],
        "received_mb": info["received_mb"],
        "packets_sent": info["packets_sent"],
        "packets_received": info["packets_received"],
        "notes": notes,
    }


def get_network_recommendations():
    health = get_network_health()

    return health["recommendations"]


def get_network_health_report():
    health = get_network_health()
    activity = get_network_activity_analysis()
    primary = health.get("primary_interface")

    lines = [
        "JERVIS SMART NETWORK INTELLIGENCE",
        "",
        f"Network Health: {health['status']}",
        (
            "Internet: Connected"
            if health["internet"]
            else "Internet: Disconnected"
        ),
        f"Local IP: {health['local_ip']}",
        f"Active Interfaces: {len(health['active_interfaces'])}",
    ]

    if primary:
        lines.extend(
            [
                "",
                "PRIMARY INTERFACE",
                f"Name: {primary.get('name', 'Unknown')}",
                f"Speed: {primary.get('speed_mbps', 0)} Mbps",
                (
                    "IPv4: "
                    + (
                        ", ".join(primary.get("ipv4", []))
                        if primary.get("ipv4")
                        else "No IPv4"
                    )
                ),
                f"MAC: {primary.get('mac', 'Unavailable')}",
            ]
        )

    lines.extend(
        [
            "",
            "NETWORK ACTIVITY",
            f"Data Sent: {activity['sent_mb']} MB",
            f"Data Received: {activity['received_mb']} MB",
            f"Packets Sent: {activity['packets_sent']}",
            f"Packets Received: {activity['packets_received']}",
            "",
            "DETECTED PROBLEMS",
        ]
    )

    if health["problems"]:
        for problem in health["problems"]:
            lines.append(
                f"- {problem}"
            )
    else:
        lines.append(
            "- No major network problem detected."
        )

    lines.extend(
        [
            "",
            "RECOMMENDATIONS",
        ]
    )

    for recommendation in health["recommendations"]:
        lines.append(
            f"- {recommendation}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: Monitoring and recommendations only. "
                "JERVIS will not automatically change Windows network settings."
            ),
        ]
    )

    return "\n".join(lines)


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
        get_network_health_report()
    )

    print()
    print(
        get_network_report()
    )