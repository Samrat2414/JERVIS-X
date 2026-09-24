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
    import core.startup_bootstrap
    import main

    calls = []

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py"],
    )

    monkeypatch.setattr(
        core.startup_bootstrap,
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
