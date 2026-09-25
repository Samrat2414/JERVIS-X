import core.startup_bootstrap as bootstrap


import pytest


@pytest.fixture(autouse=True)
def isolate_security_bootstrap_history(tmp_path, monkeypatch):
    """Keep startup bootstrap tests isolated from production history."""

    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "security_bootstrap_history.json"

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    yield

    bootstrap.clear_security_bootstrap_history()


def test_security_bootstrap_returns_success(monkeypatch):
    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "loaded": True,
            "initialized": True,
            "event_count": 3,
            "message": "Audit initialized.",
        },
    )

    result = bootstrap.initialize_security_bootstrap()

    assert result["success"] is True
    assert result["component"] == "confirmation_audit"
    assert result["loaded"] is True
    assert result["event_count"] == 3


def test_security_bootstrap_preserves_initializer_failure(monkeypatch):
    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": False,
            "loaded": False,
            "initialized": False,
            "event_count": 0,
            "message": "Audit recovery failed.",
        },
    )

    result = bootstrap.initialize_security_bootstrap()

    assert result["success"] is False
    assert result["component"] == "confirmation_audit"
    assert result["message"] == "Audit recovery failed."


def test_security_bootstrap_contains_initializer_exception(monkeypatch):
    def fail():
        raise OSError("storage unavailable")

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        fail,
    )

    result = bootstrap.initialize_security_bootstrap()

    assert result["success"] is False
    assert result["component"] == "confirmation_audit"
    assert "storage unavailable" in result["message"]


def test_security_bootstrap_rejects_invalid_result(monkeypatch):
    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: None,
    )

    result = bootstrap.initialize_security_bootstrap()

    assert result["success"] is False
    assert result["component"] == "confirmation_audit"
    assert "invalid result" in result["message"].lower()


def test_main_gui_path_runs_security_bootstrap_before_gui(monkeypatch):
    import sys

    import gui.app
    import core.performance_monitor
    import main

    calls = []

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py"],
    )

    monkeypatch.setattr(
        bootstrap,
        "initialize_security_bootstrap",
        lambda: (
            calls.append("security_bootstrap")
            or {
                "success": True,
                "component": "confirmation_audit",
                "loaded": True,
                "initialized": True,
                "event_count": 1,
                "message": "Initialized.",
            }
        ),
    )

    monkeypatch.setattr(
        gui.app,
        "run_gui",
        lambda: calls.append("run_gui"),
    )

    monkeypatch.setattr(
        core.performance_monitor,
        "record_startup_time",
        lambda value: calls.append("startup_time"),
    )

    result = main.main()

    assert result is None

    assert "security_bootstrap" in calls
    assert "run_gui" in calls

    assert calls.index("security_bootstrap") < calls.index("run_gui")


def test_main_logs_successful_security_bootstrap(monkeypatch):
    import sys

    import gui.app
    import core.logger
    import core.performance_monitor
    import main

    logs = []

    monkeypatch.setattr(sys, "argv", ["main.py"])

    monkeypatch.setattr(
        bootstrap,
        "initialize_security_bootstrap",
        lambda: {
            "success": True,
            "component": "confirmation_audit",
            "loaded": True,
            "initialized": True,
            "event_count": 2,
            "message": "Confirmation audit initialized.",
        },
    )

    monkeypatch.setattr(gui.app, "run_gui", lambda: None)
    monkeypatch.setattr(
        core.performance_monitor,
        "record_startup_time",
        lambda value: None,
    )
    monkeypatch.setattr(
        core.logger,
        "log_info",
        lambda message: logs.append(("info", str(message))),
    )
    monkeypatch.setattr(
        core.logger,
        "log_warning",
        lambda message: logs.append(("warning", str(message))),
    )

    main.main()

    assert any(
        level == "info"
        and "security" in message.lower()
        and "confirmation_audit" in message
        for level, message in logs
    )


def test_main_logs_security_bootstrap_failure_and_still_runs_gui(monkeypatch):
    import sys

    import gui.app
    import core.logger
    import core.performance_monitor
    import main

    calls = []
    logs = []

    monkeypatch.setattr(sys, "argv", ["main.py"])

    monkeypatch.setattr(
        bootstrap,
        "initialize_security_bootstrap",
        lambda: {
            "success": False,
            "component": "confirmation_audit",
            "message": "Audit recovery failed.",
        },
    )

    monkeypatch.setattr(
        gui.app,
        "run_gui",
        lambda: calls.append("run_gui"),
    )
    monkeypatch.setattr(
        core.performance_monitor,
        "record_startup_time",
        lambda value: None,
    )
    monkeypatch.setattr(
        core.logger,
        "log_info",
        lambda message: logs.append(("info", str(message))),
    )
    monkeypatch.setattr(
        core.logger,
        "log_warning",
        lambda message: logs.append(("warning", str(message))),
    )

    main.main()

    assert "run_gui" in calls
    assert any(
        level == "warning"
        and "Audit recovery failed." in message
        for level, message in logs
    )


def test_main_logs_invalid_security_bootstrap_result_and_still_runs_gui(
    monkeypatch,
):
    import sys

    import gui.app
    import core.logger
    import core.performance_monitor
    import main

    calls = []
    warnings = []

    monkeypatch.setattr(sys, "argv", ["main.py"])

    monkeypatch.setattr(
        bootstrap,
        "initialize_security_bootstrap",
        lambda: None,
    )

    monkeypatch.setattr(
        gui.app,
        "run_gui",
        lambda: calls.append("run_gui"),
    )
    monkeypatch.setattr(
        core.performance_monitor,
        "record_startup_time",
        lambda value: None,
    )
    monkeypatch.setattr(core.logger, "log_info", lambda message: None)
    monkeypatch.setattr(
        core.logger,
        "log_warning",
        lambda message: warnings.append(str(message)),
    )

    main.main()

    assert "run_gui" in calls
    assert any(
        "invalid" in message.lower()
        for message in warnings
    )


def test_security_bootstrap_exposes_latest_status(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "loaded": True,
            "initialized": True,
            "event_count": 4,
            "message": "Audit initialized.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    status = bootstrap.get_security_bootstrap_status()

    assert status["success"] is True
    assert status["component"] == "confirmation_audit"
    assert status["event_count"] == 4
    assert status["message"] == "Audit initialized."


def test_security_bootstrap_status_tracks_failure(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": False,
            "loaded": False,
            "initialized": False,
            "event_count": 0,
            "message": "Audit recovery failed.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    status = bootstrap.get_security_bootstrap_status()

    assert status["success"] is False
    assert status["component"] == "confirmation_audit"
    assert status["event_count"] == 0
    assert status["message"] == "Audit recovery failed."


def test_security_bootstrap_status_returns_copy(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "loaded": True,
            "initialized": True,
            "event_count": 2,
            "message": "Audit initialized.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    first = bootstrap.get_security_bootstrap_status()
    first["success"] = False
    first["event_count"] = 999

    second = bootstrap.get_security_bootstrap_status()

    assert second["success"] is True
    assert second["event_count"] == 2


def test_security_bootstrap_status_tracks_initializer_exception(monkeypatch):
    import core.startup_bootstrap as bootstrap

    def fail():
        raise OSError("storage unavailable")

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        fail,
    )

    result = bootstrap.initialize_security_bootstrap()
    status = bootstrap.get_security_bootstrap_status()

    assert result["success"] is False
    assert status["success"] is False
    assert status["component"] == "confirmation_audit"
    assert "storage unavailable" in status["message"]


def test_security_bootstrap_status_tracks_invalid_result(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: None,
    )

    result = bootstrap.initialize_security_bootstrap()
    status = bootstrap.get_security_bootstrap_status()

    assert result["success"] is False
    assert status["success"] is False
    assert status["component"] == "confirmation_audit"
    assert "invalid result" in status["message"].lower()


def test_security_bootstrap_records_status_history(monkeypatch):
    import core.startup_bootstrap as bootstrap

    bootstrap.clear_security_bootstrap_history()

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "loaded": True,
            "initialized": True,
            "event_count": 3,
            "message": "Audit initialized.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    history = bootstrap.get_security_bootstrap_history()

    assert len(history) == 1
    assert history[0]["success"] is True
    assert history[0]["component"] == "confirmation_audit"
    assert history[0]["event_count"] == 3
    assert history[0]["message"] == "Audit initialized."


def test_security_bootstrap_history_records_multiple_results(monkeypatch):
    import core.startup_bootstrap as bootstrap

    bootstrap.clear_security_bootstrap_history()

    results = iter(
        [
            {
                "success": True,
                "loaded": True,
                "initialized": True,
                "event_count": 1,
                "message": "First startup.",
            },
            {
                "success": False,
                "loaded": False,
                "initialized": False,
                "event_count": 0,
                "message": "Second startup failed.",
            },
        ]
    )

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: next(results),
    )

    bootstrap.initialize_security_bootstrap()
    bootstrap.initialize_security_bootstrap()

    history = bootstrap.get_security_bootstrap_history()

    assert len(history) == 2
    assert history[0]["success"] is True
    assert history[0]["message"] == "First startup."
    assert history[1]["success"] is False
    assert history[1]["message"] == "Second startup failed."


def test_security_bootstrap_history_records_exception(monkeypatch):
    import core.startup_bootstrap as bootstrap

    bootstrap.clear_security_bootstrap_history()

    def fail():
        raise OSError("history storage unavailable")

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        fail,
    )

    bootstrap.initialize_security_bootstrap()

    history = bootstrap.get_security_bootstrap_history()

    assert len(history) == 1
    assert history[0]["success"] is False
    assert history[0]["component"] == "confirmation_audit"
    assert "history storage unavailable" in history[0]["message"]


def test_security_bootstrap_history_returns_defensive_copies(monkeypatch):
    import core.startup_bootstrap as bootstrap

    bootstrap.clear_security_bootstrap_history()

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "loaded": True,
            "initialized": True,
            "event_count": 7,
            "message": "Protected history.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    first = bootstrap.get_security_bootstrap_history()

    first[0]["success"] = False
    first[0]["event_count"] = 999
    first.append({"success": False})

    second = bootstrap.get_security_bootstrap_history()

    assert len(second) == 1
    assert second[0]["success"] is True
    assert second[0]["event_count"] == 7


def test_clear_security_bootstrap_history(monkeypatch):
    import core.startup_bootstrap as bootstrap

    bootstrap.clear_security_bootstrap_history()

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "loaded": True,
            "initialized": True,
            "event_count": 1,
            "message": "Recorded.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    assert len(bootstrap.get_security_bootstrap_history()) == 1

    bootstrap.clear_security_bootstrap_history()

    assert bootstrap.get_security_bootstrap_history() == []


def test_security_bootstrap_history_persists_to_disk(tmp_path, monkeypatch):
    import json

    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "security_bootstrap_history.json"

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
        raising=False,
    )

    bootstrap.clear_security_bootstrap_history()

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "loaded": True,
            "initialized": True,
            "event_count": 5,
            "message": "Persistent audit initialized.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    assert history_path.exists()

    data = json.loads(
        history_path.read_text(encoding="utf-8")
    )

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["success"] is True
    assert data[0]["component"] == "confirmation_audit"
    assert data[0]["event_count"] == 5
    assert data[0]["message"] == "Persistent audit initialized."


def test_security_bootstrap_history_loads_from_disk(tmp_path, monkeypatch):
    import json

    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "security_bootstrap_history.json"

    history_path.write_text(
        json.dumps(
            [
                {
                    "success": True,
                    "component": "confirmation_audit",
                    "event_count": 8,
                    "message": "Recovered persistent history.",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    history = bootstrap.load_security_bootstrap_history()

    assert len(history) == 1
    assert history[0]["success"] is True
    assert history[0]["component"] == "confirmation_audit"
    assert history[0]["event_count"] == 8
    assert history[0]["message"] == "Recovered persistent history."

    current = bootstrap.get_security_bootstrap_history()

    assert current == history


def test_security_bootstrap_history_load_handles_missing_file(
    tmp_path,
    monkeypatch,
):
    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "missing_history.json"

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    history = bootstrap.load_security_bootstrap_history()

    assert history == []
    assert bootstrap.get_security_bootstrap_history() == []


def test_security_bootstrap_history_load_handles_corrupt_json(
    tmp_path,
    monkeypatch,
):
    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "corrupt_history.json"
    history_path.write_text(
        "{ definitely not valid json",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    history = bootstrap.load_security_bootstrap_history()

    assert history == []
    assert bootstrap.get_security_bootstrap_history() == []


def test_security_bootstrap_history_load_rejects_invalid_structure(
    tmp_path,
    monkeypatch,
):
    import json

    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "invalid_history.json"
    history_path.write_text(
        json.dumps(
            {
                "success": True,
                "message": "This should have been a list.",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    history = bootstrap.load_security_bootstrap_history()

    assert history == []
    assert bootstrap.get_security_bootstrap_history() == []


def test_security_bootstrap_appends_to_persisted_history(
    tmp_path,
    monkeypatch,
):
    import json

    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "security_bootstrap_history.json"

    history_path.write_text(
        json.dumps(
            [
                {
                    "success": True,
                    "component": "confirmation_audit",
                    "event_count": 2,
                    "message": "Previous process startup.",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "loaded": True,
            "initialized": True,
            "event_count": 6,
            "message": "Current process startup.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    history = bootstrap.get_security_bootstrap_history()

    assert len(history) == 2

    assert history[0]["message"] == "Previous process startup."
    assert history[0]["event_count"] == 2

    assert history[1]["message"] == "Current process startup."
    assert history[1]["event_count"] == 6

    persisted = json.loads(
        history_path.read_text(encoding="utf-8")
    )

    assert len(persisted) == 2
    assert persisted[0]["message"] == "Previous process startup."
    assert persisted[1]["message"] == "Current process startup."


def test_security_history_cli_does_not_append_history(tmp_path):
    import json
    import subprocess
    import sys

    history_path = tmp_path / "security_bootstrap_history.json"

    history_path.write_text(
        json.dumps(
            [
                {
                    "success": True,
                    "component": "confirmation_audit",
                    "event_count": 4,
                    "message": "Existing startup.",
                }
            ]
        ),
        encoding="utf-8",
    )

    script = """
from pathlib import Path
import core.startup_bootstrap as bootstrap

bootstrap.SECURITY_BOOTSTRAP_HISTORY_FILE = Path(r'%s')
bootstrap.clear_security_bootstrap_history()
bootstrap.load_security_bootstrap_history()

history = bootstrap.get_security_bootstrap_history()

assert len(history) == 1
assert history[0]["message"] == "Existing startup."
""" % str(history_path)

    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    persisted = json.loads(
        history_path.read_text(encoding="utf-8")
    )

    assert len(persisted) == 1
    assert persisted[0]["message"] == "Existing startup."


def test_security_bootstrap_history_retains_latest_100_entries(
    tmp_path,
    monkeypatch,
):
    import json

    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "security_bootstrap_history.json"

    existing = [
        {
            "success": True,
            "component": "confirmation_audit",
            "event_count": index,
            "message": f"Startup {index}.",
        }
        for index in range(100)
    ]

    history_path.write_text(
        json.dumps(existing),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "loaded": True,
            "initialized": True,
            "event_count": 100,
            "message": "Startup 100.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    history = bootstrap.get_security_bootstrap_history()

    assert len(history) == 100
    assert history[0]["message"] == "Startup 1."
    assert history[-1]["message"] == "Startup 100."

    persisted = json.loads(
        history_path.read_text(encoding="utf-8")
    )

    assert len(persisted) == 100
    assert persisted[0]["message"] == "Startup 1."
    assert persisted[-1]["message"] == "Startup 100."


def test_security_bootstrap_history_below_limit_is_not_trimmed(
    tmp_path,
    monkeypatch,
):
    import json

    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "security_bootstrap_history.json"

    existing = [
        {
            "success": True,
            "component": "confirmation_audit",
            "event_count": index,
            "message": f"Startup {index}.",
        }
        for index in range(98)
    ]

    history_path.write_text(
        json.dumps(existing),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "event_count": 98,
            "message": "Startup 98.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    history = bootstrap.get_security_bootstrap_history()

    assert len(history) == 99
    assert history[0]["message"] == "Startup 0."
    assert history[-1]["message"] == "Startup 98."


def test_security_bootstrap_history_exact_limit_is_preserved(
    tmp_path,
    monkeypatch,
):
    import json

    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "security_bootstrap_history.json"

    existing = [
        {
            "success": True,
            "component": "confirmation_audit",
            "event_count": index,
            "message": f"Startup {index}.",
        }
        for index in range(99)
    ]

    history_path.write_text(
        json.dumps(existing),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    monkeypatch.setattr(
        bootstrap,
        "initialize_confirmation_audit_state",
        lambda: {
            "success": True,
            "event_count": 99,
            "message": "Startup 99.",
        },
    )

    bootstrap.initialize_security_bootstrap()

    history = bootstrap.get_security_bootstrap_history()

    assert len(history) == 100
    assert history[0]["message"] == "Startup 0."
    assert history[-1]["message"] == "Startup 99."


def test_security_bootstrap_history_load_trims_oversized_history(
    tmp_path,
    monkeypatch,
):
    import json

    import core.startup_bootstrap as bootstrap

    history_path = tmp_path / "security_bootstrap_history.json"

    existing = [
        {
            "success": True,
            "component": "confirmation_audit",
            "event_count": index,
            "message": f"Startup {index}.",
        }
        for index in range(150)
    ]

    history_path.write_text(
        json.dumps(existing),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bootstrap,
        "SECURITY_BOOTSTRAP_HISTORY_FILE",
        history_path,
    )

    bootstrap.clear_security_bootstrap_history()

    history = bootstrap.load_security_bootstrap_history()

    assert len(history) == 100
    assert history[0]["event_count"] == 50
    assert history[0]["message"] == "Startup 50."
    assert history[-1]["event_count"] == 149
    assert history[-1]["message"] == "Startup 149."

    current = bootstrap.get_security_bootstrap_history()

    assert current == history


def test_security_health_unknown_without_history():
    import core.startup_bootstrap as bootstrap

    bootstrap.clear_security_bootstrap_history()

    health = bootstrap.get_security_health_score()

    assert health["score"] == 0
    assert health["status"] == "UNKNOWN"
    assert health["total_events"] == 0
    assert health["successful_events"] == 0
    assert health["failed_events"] == 0
    assert health["success_rate"] == 0.0
    assert health["consecutive_failures"] == 0


def test_security_health_is_healthy_for_successful_history(
    monkeypatch,
):
    import core.startup_bootstrap as bootstrap

    history = [
        {"success": True}
        for _ in range(10)
    ]

    monkeypatch.setattr(
        bootstrap,
        "_security_bootstrap_history",
        history,
    )

    health = bootstrap.get_security_health_score()

    assert health["score"] == 100
    assert health["status"] == "HEALTHY"
    assert health["total_events"] == 10
    assert health["successful_events"] == 10
    assert health["failed_events"] == 0
    assert health["success_rate"] == 100.0
    assert health["consecutive_failures"] == 0


def test_security_health_warning_for_one_recent_failure(
    monkeypatch,
):
    import core.startup_bootstrap as bootstrap

    history = [
        {"success": True}
        for _ in range(9)
    ] + [
        {"success": False}
    ]

    monkeypatch.setattr(
        bootstrap,
        "_security_bootstrap_history",
        history,
    )

    health = bootstrap.get_security_health_score()

    assert health["score"] == 79
    assert health["status"] == "WARNING"
    assert health["successful_events"] == 9
    assert health["failed_events"] == 1
    assert health["success_rate"] == 90.0
    assert health["consecutive_failures"] == 1


def test_security_health_critical_for_three_consecutive_failures(
    monkeypatch,
):
    import core.startup_bootstrap as bootstrap

    history = [
        {"success": True}
        for _ in range(7)
    ] + [
        {"success": False},
        {"success": False},
        {"success": False},
    ]

    monkeypatch.setattr(
        bootstrap,
        "_security_bootstrap_history",
        history,
    )

    health = bootstrap.get_security_health_score()

    assert health["score"] == 39
    assert health["status"] == "CRITICAL"
    assert health["successful_events"] == 7
    assert health["failed_events"] == 3
    assert health["success_rate"] == 70.0
    assert health["consecutive_failures"] == 3


def test_security_health_two_consecutive_failures_caps_score(
    monkeypatch,
):
    import core.startup_bootstrap as bootstrap

    history = [
        {"success": True}
        for _ in range(18)
    ] + [
        {"success": False},
        {"success": False},
    ]

    monkeypatch.setattr(
        bootstrap,
        "_security_bootstrap_history",
        history,
    )

    health = bootstrap.get_security_health_score()

    assert health["score"] == 59
    assert health["status"] == "CRITICAL"
    assert health["success_rate"] == 90.0
    assert health["consecutive_failures"] == 2


def test_security_health_recommendation_unknown(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "get_security_health_score",
        lambda: {
            "status": "UNKNOWN",
            "score": 0,
            "consecutive_failures": 0,
        },
    )

    result = bootstrap.get_security_health_recommendation()

    assert result["status"] == "UNKNOWN"
    assert result["score"] == 0
    assert result["priority"] == "MEDIUM"
    assert result["requires_manual_review"] is False
    assert result["automation_allowed"] is False
    assert result["source"] == "Security Health Intelligence"


def test_security_health_recommendation_healthy(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "get_security_health_score",
        lambda: {
            "status": "HEALTHY",
            "score": 100,
            "consecutive_failures": 0,
        },
    )

    result = bootstrap.get_security_health_recommendation()

    assert result["status"] == "HEALTHY"
    assert result["priority"] == "NONE"
    assert result["requires_manual_review"] is False
    assert result["automation_allowed"] is False
    assert "No corrective action" in result["recommended_action"]


def test_security_health_recommendation_warning(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "get_security_health_score",
        lambda: {
            "status": "WARNING",
            "score": 79,
            "consecutive_failures": 1,
        },
    )

    result = bootstrap.get_security_health_recommendation()

    assert result["status"] == "WARNING"
    assert result["score"] == 79
    assert result["priority"] == "HIGH"
    assert result["requires_manual_review"] is True
    assert result["automation_allowed"] is False
    assert "1 consecutive failure" in result["reason"]


def test_security_health_recommendation_critical(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "get_security_health_score",
        lambda: {
            "status": "CRITICAL",
            "score": 39,
            "consecutive_failures": 3,
        },
    )

    result = bootstrap.get_security_health_recommendation()

    assert result["status"] == "CRITICAL"
    assert result["score"] == 39
    assert result["priority"] == "CRITICAL"
    assert result["requires_manual_review"] is True
    assert result["automation_allowed"] is False
    assert "3 consecutive failure" in result["reason"]


def test_security_decision_unknown(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "get_security_health_recommendation",
        lambda: {
            "status": "UNKNOWN",
            "score": 0,
            "priority": "MEDIUM",
            "reason": "Security bootstrap history is not available.",
            "recommended_action": "Generate security history.",
            "requires_manual_review": False,
            "automation_allowed": False,
            "source": "Security Health Intelligence",
        },
    )

    result = bootstrap.get_security_decision()

    assert result["title"] == "Establish security bootstrap history"
    assert result["priority"] == "Medium"
    assert result["confidence"] == 90.0
    assert result["impact"] == "Security health visibility"
    assert result["requires_manual_review"] is False
    assert result["automation_allowed"] is False
    assert result["source"] == "Security Health Intelligence"


def test_security_decision_healthy(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "get_security_health_recommendation",
        lambda: {
            "status": "HEALTHY",
            "score": 100,
            "priority": "NONE",
            "reason": "Security bootstrap health is healthy.",
            "recommended_action": "No corrective action is required.",
            "requires_manual_review": False,
            "automation_allowed": False,
            "source": "Security Health Intelligence",
        },
    )

    result = bootstrap.get_security_decision()

    assert result["title"] == "Maintain security bootstrap health"
    assert result["priority"] == "Low"
    assert result["confidence"] == 100.0
    assert result["impact"] == "Security bootstrap reliability"
    assert result["requires_manual_review"] is False
    assert result["automation_allowed"] is False


def test_security_decision_warning(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "get_security_health_recommendation",
        lambda: {
            "status": "WARNING",
            "score": 79,
            "priority": "HIGH",
            "reason": "Recent security bootstrap instability detected.",
            "recommended_action": "Review security bootstrap history.",
            "requires_manual_review": True,
            "automation_allowed": False,
            "source": "Security Health Intelligence",
        },
    )

    result = bootstrap.get_security_decision()

    assert result["title"] == "Review security bootstrap instability"
    assert result["priority"] == "High"
    assert result["confidence"] == 95.0
    assert result["impact"] == "Security bootstrap reliability"
    assert result["requires_manual_review"] is True
    assert result["automation_allowed"] is False


def test_security_decision_critical(monkeypatch):
    import core.startup_bootstrap as bootstrap

    monkeypatch.setattr(
        bootstrap,
        "get_security_health_recommendation",
        lambda: {
            "status": "CRITICAL",
            "score": 39,
            "priority": "CRITICAL",
            "reason": "Critical security bootstrap instability detected.",
            "recommended_action": "Inspect security initialization failures.",
            "requires_manual_review": True,
            "automation_allowed": False,
            "source": "Security Health Intelligence",
        },
    )

    result = bootstrap.get_security_decision()

    assert (
        result["title"]
        == "Resolve critical security bootstrap instability"
    )
    assert result["priority"] == "Critical"
    assert result["confidence"] == 99.0
    assert (
        result["impact"]
        == "Security-sensitive automation reliability"
    )
    assert result["requires_manual_review"] is True
    assert result["automation_allowed"] is False
