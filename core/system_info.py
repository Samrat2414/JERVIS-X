import os
import platform
import socket
import sys
from datetime import datetime

import psutil


def _bytes_to_gb(value):
    return round(
        value / (1024 ** 3),
        2,
    )


def get_system_info():
    memory = psutil.virtual_memory()

    try:
        boot_time = datetime.fromtimestamp(
            psutil.boot_time()
        ).strftime("%d %B %Y, %I:%M:%S %p")
    except Exception:
        boot_time = "Unknown"

    processor = platform.processor()

    if not processor:
        processor = os.environ.get(
            "PROCESSOR_IDENTIFIER",
            "Unknown",
        )

    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "processor": processor,
        "physical_cores": psutil.cpu_count(
            logical=False
        ),
        "logical_cores": psutil.cpu_count(
            logical=True
        ),
        "total_ram_gb": _bytes_to_gb(
            memory.total
        ),
        "available_ram_gb": _bytes_to_gb(
            memory.available
        ),
        "ram_usage_percent": memory.percent,
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "boot_time": boot_time,
    }


def get_system_info_report():
    info = get_system_info()

    return (
        "JERVIS SYSTEM INFORMATION\n\n"
        f"Hostname: {info['hostname']}\n"
        f"Operating System: "
        f"{info['os']} {info['os_release']}\n"
        f"OS Version: {info['os_version']}\n"
        f"Architecture: {info['architecture']}\n\n"
        f"Processor: {info['processor']}\n"
        f"Physical CPU Cores: "
        f"{info['physical_cores']}\n"
        f"Logical CPU Cores: "
        f"{info['logical_cores']}\n\n"
        f"Total RAM: "
        f"{info['total_ram_gb']} GB\n"
        f"Available RAM: "
        f"{info['available_ram_gb']} GB\n"
        f"RAM Usage: "
        f"{info['ram_usage_percent']}%\n\n"
        f"Python Version: "
        f"{info['python_version']}\n"
        f"Python Executable: "
        f"{info['python_executable']}\n\n"
        f"System Boot Time: "
        f"{info['boot_time']}"
    )


if __name__ == "__main__":
    print(
        get_system_info_report()
    )