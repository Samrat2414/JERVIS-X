import psutil


def get_running_processes(limit=50):
    processes = []

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "cpu_percent",
            "memory_percent",
            "status",
        ]
    ):
        try:
            info = process.info

            processes.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name") or "Unknown",
                    "cpu": round(
                        info.get("cpu_percent") or 0,
                        1,
                    ),
                    "memory": round(
                        info.get("memory_percent") or 0,
                        1,
                    ),
                    "status": info.get("status") or "Unknown",
                }
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    processes.sort(
        key=lambda item: (
            item["cpu"],
            item["memory"],
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
            f"{number}. {process['name']} "
            f"(PID {process['pid']})\n"
            f"   CPU: {process['cpu']}% "
            f"| RAM: {process['memory']}% "
            f"| Status: {process['status']}"
        )

    return "\n".join(lines)


def show_processes(limit=20):
    return format_processes(
        get_running_processes(limit)
    )


def search_processes(search_text):
    search_text = str(search_text).strip().lower()

    if not search_text:
        return "Please provide a process name."

    matches = []

    for process in get_running_processes(limit=300):
        if search_text in process["name"].lower():
            matches.append(process)

    if not matches:
        return f'No process found matching "{search_text}".'

    return format_processes(matches)


def terminate_process_by_pid(pid):
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return "Invalid PID."

    try:
        process = psutil.Process(pid)
        process_name = process.name()

        process.terminate()

        try:
            process.wait(timeout=3)
            return (
                f"Process {process_name} "
                f"(PID {pid}) terminated."
            )

        except psutil.TimeoutExpired:
            return (
                f"Process {process_name} "
                f"(PID {pid}) did not close in time."
            )

    except psutil.NoSuchProcess:
        return f"No process found with PID {pid}."

    except psutil.AccessDenied:
        return (
            f"Access denied. I could not terminate PID {pid}."
        )

    except Exception as error:
        return f"I could not terminate the process: {error}"


def terminate_process_by_name(process_name):
    process_name = str(process_name).strip().lower()

    if not process_name:
        return "Please provide a process name."

    matches = []

    for process in psutil.process_iter(
        ["pid", "name"]
    ):
        try:
            name = process.info.get("name") or ""

            if process_name in name.lower():
                matches.append(process)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
        ):
            continue

    if not matches:
        return f'No process found matching "{process_name}".'

    process = matches[0]

    try:
        name = process.name()
        pid = process.pid

        process.terminate()

        return (
            f"Terminate request sent to "
            f"{name} (PID {pid})."
        )

    except psutil.AccessDenied:
        return "Access denied. I could not terminate that process."

    except Exception as error:
        return f"I could not terminate the process: {error}"


if __name__ == "__main__":
    print(show_processes())