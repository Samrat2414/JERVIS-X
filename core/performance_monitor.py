import json
import time
from datetime import datetime
from pathlib import Path

import psutil


DATA_DIR = Path("data")
PERFORMANCE_FILE = DATA_DIR / "performance_stats.json"

SESSION_START = time.perf_counter()
_OPERATION_TIMERS = {}


def _load_stats():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not PERFORMANCE_FILE.exists():
        return {
            "startup_times": [],
            "operations": [],
        }

    try:
        with PERFORMANCE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError

        data.setdefault(
            "startup_times",
            [],
        )
        data.setdefault(
            "operations",
            [],
        )

        return data

    except (
        json.JSONDecodeError,
        OSError,
        ValueError,
    ):
        return {
            "startup_times": [],
            "operations": [],
        }


def _save_stats(data):
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with PERFORMANCE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
        )


def record_startup_time(seconds):
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        return False

    data = _load_stats()

    data["startup_times"].append(
        {
            "seconds": round(seconds, 4),
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
        }
    )

    data["startup_times"] = (
        data["startup_times"][-100:]
    )

    try:
        _save_stats(data)
        return True
    except OSError:
        return False


def get_session_uptime():
    return round(
        time.perf_counter() - SESSION_START,
        2,
    )


def start_operation(name):
    name = str(name).strip()

    if not name:
        return False

    _OPERATION_TIMERS[name] = (
        time.perf_counter()
    )

    return True


def end_operation(
    name,
    slow_threshold=1.0,
):
    name = str(name).strip()

    start_time = _OPERATION_TIMERS.pop(
        name,
        None,
    )

    if start_time is None:
        return None

    duration = (
        time.perf_counter()
        - start_time
    )

    data = _load_stats()

    entry = {
        "name": name,
        "seconds": round(
            duration,
            4,
        ),
        "slow": duration >= slow_threshold,
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
    }

    data["operations"].append(entry)

    data["operations"] = (
        data["operations"][-500:]
    )

    try:
        _save_stats(data)
    except OSError:
        pass

    return entry


def measure_operation(
    name,
    function,
    *args,
    **kwargs,
):
    start_operation(name)

    try:
        result = function(
            *args,
            **kwargs,
        )
    finally:
        performance = end_operation(name)

    return result, performance


def get_average_startup_time():
    data = _load_stats()

    times = [
        item.get("seconds", 0)
        for item in data["startup_times"]
    ]

    if not times:
        return None

    return round(
        sum(times) / len(times),
        3,
    )


def get_latest_startup_time():
    data = _load_stats()

    if not data["startup_times"]:
        return None

    return data["startup_times"][-1].get(
        "seconds"
    )


def get_slow_operations(
    limit=10,
):
    data = _load_stats()

    slow = [
        item
        for item in data["operations"]
        if item.get("slow")
    ]

    slow.sort(
        key=lambda item: item.get(
            "seconds",
            0,
        ),
        reverse=True,
    )

    return slow[:limit]


def get_slow_operations_summary(
    limit=10,
):
    operations = get_slow_operations(
        limit
    )

    if not operations:
        return "No slow operations recorded."

    lines = []

    for number, item in enumerate(
        operations,
        start=1,
    ):
        lines.append(
            f"{number}. {item['name']} "
            f"- {item['seconds']} seconds"
        )

    return "\n".join(lines)


def _bytes_to_mb(value):
    return round(
        value / (1024 * 1024),
        2,
    )


def _get_disk_usage():
    try:
        root = (
            Path.home().anchor
            or "C:\\"
        )

        return psutil.disk_usage(
            root
        ).percent

    except (
        OSError,
        PermissionError,
    ):
        return 0.0


def _performance_score(
    cpu,
    ram,
    disk,
):
    score = 100

    if cpu >= 90:
        score -= 30
    elif cpu >= 75:
        score -= 20
    elif cpu >= 60:
        score -= 10

    if ram >= 90:
        score -= 30
    elif ram >= 80:
        score -= 20
    elif ram >= 70:
        score -= 10

    if disk >= 95:
        score -= 25
    elif disk >= 85:
        score -= 15
    elif disk >= 75:
        score -= 5

    return max(
        0,
        min(100, score),
    )


def _performance_status(score):
    if score >= 85:
        return "Excellent"

    if score >= 70:
        return "Good"

    if score >= 50:
        return "Warning"

    return "Critical"


def get_live_performance(
    sample_seconds=1.0,
):
    try:
        sample_seconds = float(
            sample_seconds
        )
    except (TypeError, ValueError):
        sample_seconds = 1.0

    sample_seconds = max(
        0.1,
        min(sample_seconds, 5.0),
    )

    network_before = (
        psutil.net_io_counters()
    )

    cpu = psutil.cpu_percent(
        interval=sample_seconds
    )

    network_after = (
        psutil.net_io_counters()
    )

    ram = psutil.virtual_memory().percent
    disk = _get_disk_usage()

    upload_bytes = max(
        0,
        network_after.bytes_sent
        - network_before.bytes_sent,
    )

    download_bytes = max(
        0,
        network_after.bytes_recv
        - network_before.bytes_recv,
    )

    upload_speed = (
        upload_bytes
        / sample_seconds
    )

    download_speed = (
        download_bytes
        / sample_seconds
    )

    score = _performance_score(
        cpu,
        ram,
        disk,
    )

    return {
        "cpu": round(cpu, 1),
        "ram": round(ram, 1),
        "disk": round(disk, 1),
        "upload_mb_s": _bytes_to_mb(
            upload_speed
        ),
        "download_mb_s": _bytes_to_mb(
            download_speed
        ),
        "score": score,
        "status": _performance_status(
            score
        ),
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
    }


def get_live_performance_report():
    result = get_live_performance()

    return (
        "JERVIS LIVE SYSTEM PERFORMANCE\n\n"
        f"CPU Usage: {result['cpu']}%\n"
        f"RAM Usage: {result['ram']}%\n"
        f"Disk Usage: {result['disk']}%\n\n"
        f"Upload Speed: "
        f"{result['upload_mb_s']} MB/s\n"
        f"Download Speed: "
        f"{result['download_mb_s']} MB/s\n\n"
        f"Performance Score: "
        f"{result['score']}/100\n"
        f"Performance Status: "
        f"{result['status']}"
    )


def get_performance_report():
    latest = get_latest_startup_time()
    average = get_average_startup_time()
    uptime = get_session_uptime()

    latest_text = (
        f"{latest} seconds"
        if latest is not None
        else "Not recorded"
    )

    average_text = (
        f"{average} seconds"
        if average is not None
        else "Not available"
    )

    return (
        "JERVIS PERFORMANCE REPORT\n\n"
        f"Session Uptime: {uptime} seconds\n"
        f"Latest Startup Time: {latest_text}\n"
        f"Average Startup Time: {average_text}\n\n"
        "Slow Operations:\n"
        f"{get_slow_operations_summary()}"
    )


if __name__ == "__main__":
    print(
        get_live_performance_report()
    )

    print()
    print(
        get_performance_report()
    )