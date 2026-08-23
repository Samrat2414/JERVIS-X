import os
from datetime import datetime

import psutil


PROTECTED_PIDS = {0, 4}
PROTECTED_NAMES = {
    "system idle process",
    "system",
    "registry",
    "memory compression",
}


def _safe_round(value, digits=1):
    try:
        return round(float(value or 0), digits)
    except (TypeError, ValueError):
        return 0.0


def _process_to_dict(process, include_details=False):
    try:
        with process.oneshot():
            info = {
                "pid": process.pid,
                "name": process.name() or "Unknown",
                "cpu": _safe_round(process.cpu_percent(interval=None)),
                "ram": _safe_round(process.memory_percent()),
                "status": process.status(),
            }

            if include_details:
                try:
                    info["path"] = process.exe()
                except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                    info["path"] = "Unavailable"

                try:
                    info["username"] = process.username()
                except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                    info["username"] = "Unavailable"

                try:
                    created = process.create_time()
                    info["create_time"] = datetime.fromtimestamp(
                        created
                    ).strftime("%Y-%m-%d %H:%M:%S")
                except (psutil.AccessDenied, psutil.NoSuchProcess, OSError, ValueError):
                    info["create_time"] = "Unavailable"

                try:
                    info["threads"] = process.num_threads()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    info["threads"] = "Unavailable"

                try:
                    memory = process.memory_info()
                    info["memory_mb"] = round(
                        memory.rss / (1024 ** 2),
                        2,
                    )
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    info["memory_mb"] = "Unavailable"

            return info

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
    ):
        return None


def get_running_processes(limit=50):
    """Return running processes sorted by CPU usage then RAM usage."""
    try:
        limit = max(1, int(limit))
    except (TypeError, ValueError):
        limit = 50

    processes = []

    # First pass initializes psutil CPU counters.
    for process in psutil.process_iter():
        try:
            process.cpu_percent(interval=None)
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    # Small system-wide sample improves per-process CPU readings.
    psutil.cpu_percent(interval=0.15)

    for process in psutil.process_iter():
        item = _process_to_dict(process)

        if item is not None:
            processes.append(item)

    processes.sort(
        key=lambda item: (
            item.get("cpu", 0),
            item.get("ram", 0),
        ),
        reverse=True,
    )

    return processes[:limit]


def format_processes(processes):
    if not processes:
        return "No running processes found."

    lines = []

    for number, process in enumerate(
        processes,
        start=1,
    ):
        lines.append(
            f"{number}. {process.get('name', 'Unknown')} "
            f"(PID {process.get('pid', 'Unknown')})"
        )

        lines.append(
            f"   CPU: {process.get('cpu', 0)}% "
            f"| RAM: {process.get('ram', 0)}% "
            f"| Status: {process.get('status', 'unknown')}"
        )

    return "\n".join(lines)


def show_processes(limit=20):
    return format_processes(
        get_running_processes(limit)
    )


def search_processes(search_text):
    search_text = str(search_text).strip().lower()

    if not search_text:
        return 'Enter a process name, for example: find process notepad'

    matches = []

    for process in psutil.process_iter():
        try:
            name = process.name() or ""

            if search_text in name.lower():
                item = _process_to_dict(
                    process,
                    include_details=True,
                )

                if item:
                    matches.append(item)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    if not matches:
        return f'No process found matching "{search_text}".'

    lines = [
        f'PROCESS SEARCH RESULTS: "{search_text}"',
        "",
    ]

    for number, process in enumerate(
        matches,
        start=1,
    ):
        lines.extend(
            [
                (
                    f"{number}. {process['name']} "
                    f"(PID {process['pid']})"
                ),
                (
                    f"   CPU: {process['cpu']}% | "
                    f"RAM: {process['ram']}% | "
                    f"Status: {process['status']}"
                ),
                f"   Path: {process['path']}",
                "",
            ]
        )

    return "\n".join(lines).rstrip()


def get_process_by_pid(pid):
    """Return detailed information for one PID."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return None

    try:
        process = psutil.Process(pid)

        return _process_to_dict(
            process,
            include_details=True,
        )

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
    ):
        return None


def get_process_details(pid):
    process = get_process_by_pid(pid)

    if not process:
        return f"No accessible process found with PID {pid}."

    return (
        "JERVIS PROCESS DETAILS\n\n"
        f"Name: {process['name']}\n"
        f"PID: {process['pid']}\n"
        f"Status: {process['status']}\n"
        f"CPU Usage: {process['cpu']}%\n"
        f"RAM Usage: {process['ram']}%\n"
        f"Memory: {process['memory_mb']} MB\n"
        f"Threads: {process['threads']}\n"
        f"Started: {process['create_time']}\n"
        f"User: {process['username']}\n"
        f"Executable: {process['path']}"
    )


def is_safe_to_terminate(pid):
    """Return (allowed, reason). Blocks obvious Windows/system-critical targets."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False, "Invalid PID."

    if pid == os.getpid():
        return False, "JERVIS cannot terminate its own Python process."

    if pid in PROTECTED_PIDS:
        return False, f"PID {pid} is a protected system process."

    try:
        process = psutil.Process(pid)
        name = (process.name() or "").strip().lower()

        if name in PROTECTED_NAMES:
            return False, f"{process.name()} is protected."

        try:
            username = (process.username() or "").lower()
        except psutil.AccessDenied:
            username = ""

        # Conservative protection for common Windows service/system accounts.
        if (
            username.endswith("\\system")
            or "local service" in username
            or "network service" in username
        ):
            return (
                False,
                f"{process.name()} appears to be a Windows system/service process.",
            )

        return True, "Process can be terminated after explicit user confirmation."

    except psutil.NoSuchProcess:
        return False, f"No process found with PID {pid}."

    except psutil.AccessDenied:
        return False, f"Access denied for PID {pid}."


def terminate_process_by_pid(pid):
    """
    Terminate one process by PID.

    This function never bypasses Windows permissions and refuses obvious
    system-critical processes. GUI/brain code should still ask the user for
    confirmation before calling it.
    """
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return "Invalid PID."

    allowed, reason = is_safe_to_terminate(pid)

    if not allowed:
        return f"Termination blocked: {reason}"

    try:
        process = psutil.Process(pid)
        name = process.name()

        process.terminate()

        try:
            process.wait(timeout=3)

        except psutil.TimeoutExpired:
            return (
                f"{name} (PID {pid}) did not exit within 3 seconds. "
                "JERVIS did not force-kill it."
            )

        return f"{name} (PID {pid}) terminated successfully."

    except psutil.NoSuchProcess:
        return f"No process found with PID {pid}."

    except psutil.AccessDenied:
        return f"Access denied. Could not terminate PID {pid}."

    except Exception as error:
        return f"Could not terminate PID {pid}: {error}"


def terminate_process_by_name(process_name):
    """
    Terminate matching processes by name.

    Intended to be called only after explicit user confirmation.
    Protected processes are skipped.
    """
    process_name = str(process_name).strip().lower()

    if not process_name:
        return "Enter a process name."

    matched = []
    terminated = []
    blocked = []
    failed = []

    for process in psutil.process_iter(["pid", "name"]):
        try:
            name = process.info.get("name") or ""

            if process_name not in name.lower():
                continue

            pid = process.info["pid"]
            matched.append(
                (pid, name)
            )

            allowed, reason = is_safe_to_terminate(pid)

            if not allowed:
                blocked.append(
                    f"{name} (PID {pid}): {reason}"
                )
                continue

            result = terminate_process_by_pid(pid)

            if "terminated successfully" in result.lower():
                terminated.append(result)
            else:
                failed.append(result)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    if not matched:
        return f'No process found matching "{process_name}".'

    lines = []

    if terminated:
        lines.append("TERMINATED")
        lines.extend(
            f"- {item}"
            for item in terminated
        )

    if blocked:
        if lines:
            lines.append("")

        lines.append("BLOCKED FOR SAFETY")
        lines.extend(
            f"- {item}"
            for item in blocked
        )

    if failed:
        if lines:
            lines.append("")

        lines.append("NOT TERMINATED")
        lines.extend(
            f"- {item}"
            for item in failed
        )

    return "\n".join(lines)


def get_process_manager_report(limit=10):
    return (
        "JERVIS SMART PROCESS MANAGER\n\n"
        "TOP RUNNING PROCESSES\n\n"
        f"{show_processes(limit)}\n\n"
        "Safety: Process termination requires explicit user confirmation "
        "and protected system processes are blocked."
    )


if __name__ == "__main__":
    print(
        get_process_manager_report(10)
    )