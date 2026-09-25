import core.startup_bootstrap as bootstrap


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
