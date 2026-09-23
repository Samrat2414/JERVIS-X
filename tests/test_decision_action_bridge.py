from core.decision_action_bridge import (
    CONFIRM,
    UNSUPPORTED,
    execute_action,
    resolve_decision_action,
)


def test_lock_pc_requires_confirmation():
    result = execute_action("lock_pc")

    assert result["success"] is False
    assert result["status"] == CONFIRM


def test_unknown_action_is_unsupported():
    result = execute_action("destroy_pc")

    assert result["success"] is False
    assert result["status"] == UNSUPPORTED


def test_alert_decision_routes_without_execution():
    decision = {
        "title": "Resolve critical JERVIS alerts",
        "action": (
            "Open Alert Intelligence and resolve critical alerts "
            "before lower-priority work."
        ),
        "source": "Alert Intelligence",
    }

    result = resolve_decision_action(decision)

    assert result["action_name"] is None
    assert result["status"] == UNSUPPORTED
    assert result["route"] == "alert intelligence"


def test_safe_action_executes_mapped_function(monkeypatch):
    called = {"value": False}

    def fake_open_task_manager():
        called["value"] = True
        return "Task Manager opened."

    monkeypatch.setitem(
        __import__(
            "core.decision_action_bridge",
            fromlist=["ACTION_MAP"],
        ).ACTION_MAP,
        "open_task_manager",
        {
            "function": fake_open_task_manager,
            "safety": "safe",
            "description": "Open Windows Task Manager.",
        },
    )

    result = execute_action("open_task_manager")

    assert result["success"] is True
    assert result["status"] == "safe"
    assert called["value"] is True


def test_disk_decision_routes_to_cleanup_analysis():
    decision = {
        "title": "Free disk space",
        "priority": "Critical",
        "action": (
            "Review large files and safe cleanup recommendations, "
            "then free disk space."
        ),
        "source": "System Health",
    }

    result = resolve_decision_action(decision)

    assert result["action_name"] is None
    assert result["status"] == "safe"
    assert result["route"] == "cleanup analysis"


def test_ram_decision_routes_to_task_manager():
    decision = {
        "title": "Reduce RAM pressure",
        "priority": "Critical",
        "action": "Close unused applications and browser tabs.",
        "source": "System Health",
    }

    result = resolve_decision_action(decision)

    assert result["action_name"] == "open_task_manager"
    assert result["status"] == "safe"
    assert "not close applications automatically" in result["message"]


def test_execute_decision_runs_safe_action(monkeypatch):
    import core.decision_action_bridge as bridge

    decision = {
        "title": "Reduce RAM usage",
        "action": "Close unused applications and browser tabs.",
        "source": "System Health",
    }

    called = {"value": False}

    def fake_task_manager():
        called["value"] = True
        return "Task Manager opened."

    monkeypatch.setitem(
        bridge.ACTION_MAP,
        "open_task_manager",
        {
            "function": fake_task_manager,
            "safety": bridge.SAFE,
            "description": "Open Windows Task Manager.",
        },
    )

    result = bridge.execute_decision(decision)

    assert result["success"] is True
    assert result["status"] == bridge.SAFE
    assert result["action_name"] == "open_task_manager"
    assert called["value"] is True


def test_execute_decision_does_not_execute_route_only_decision():
    import core.decision_action_bridge as bridge

    decision = {
        "title": "Free disk space",
        "action": (
            "Review large files and safe cleanup recommendations, "
            "then free disk space."
        ),
        "source": "System Health",
    }

    result = bridge.execute_decision(decision)

    assert result["success"] is False
    assert result["status"] == bridge.SAFE
    assert result["action_name"] is None
    assert result["route"] == "cleanup analysis"
    assert "No files will be deleted automatically" in result["message"]


def test_execute_decision_blocks_confirm_action_without_confirmation(monkeypatch):
    import core.decision_action_bridge as bridge

    monkeypatch.setattr(
        bridge,
        "resolve_decision_action",
        lambda decision: {
            "action_name": "lock_pc",
            "status": bridge.CONFIRM,
            "message": "Lock PC requires confirmation.",
        },
    )

    result = bridge.execute_decision(
        {"title": "Lock the PC"},
        confirmed=False,
    )

    assert result["success"] is False
    assert result["status"] == bridge.CONFIRM
    assert result["action_name"] == "lock_pc"
    assert "Confirmation required" in result["message"]


def test_execute_decision_runs_confirm_action_after_confirmation(monkeypatch):
    import core.decision_action_bridge as bridge

    called = {"value": False}

    def fake_lock_pc():
        called["value"] = True
        return "PC lock simulated."

    monkeypatch.setitem(
        bridge.ACTION_MAP,
        "lock_pc",
        {
            "function": fake_lock_pc,
            "safety": bridge.CONFIRM,
            "description": "Lock the Windows PC.",
        },
    )

    monkeypatch.setattr(
        bridge,
        "resolve_decision_action",
        lambda decision: {
            "action_name": "lock_pc",
            "status": bridge.CONFIRM,
            "message": "Lock PC requires confirmation.",
        },
    )

    result = bridge.execute_decision(
        {"title": "Lock the PC"},
        confirmed=True,
    )

    assert result["success"] is True
    assert result["status"] == bridge.CONFIRM
    assert result["action_name"] == "lock_pc"
    assert called["value"] is True


def test_pending_confirmation_rejects_safe_decision():
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()

    decision = {
        "title": "Reduce RAM usage",
        "action": "Close unused applications and browser tabs.",
        "source": "System Health",
    }

    result = bridge.create_pending_confirmation(decision)

    assert result["success"] is False
    assert result["status"] == bridge.SAFE
    assert bridge.get_pending_confirmation() is None


def test_pending_confirmation_binds_exact_confirm_decision(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()

    decision = {
        "title": "Lock the PC",
        "action": "Lock the Windows PC.",
        "source": "System Safety",
    }

    monkeypatch.setattr(
        bridge,
        "resolve_decision_action",
        lambda item: {
            "action_name": "lock_pc",
            "status": bridge.CONFIRM,
            "message": "Confirmation required.",
        },
    )

    result = bridge.create_pending_confirmation(decision)
    pending = bridge.get_pending_confirmation()

    assert result["success"] is True
    assert result["status"] == bridge.CONFIRM
    assert result["action_name"] == "lock_pc"

    assert pending is not None
    assert pending["action_name"] == "lock_pc"
    assert pending["fingerprint"] == result["fingerprint"]
    assert len(pending["fingerprint"]) == 64

    bridge.clear_pending_confirmation()
    assert bridge.get_pending_confirmation() is None


def test_pending_confirmation_rejects_changed_decision(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()

    original_decision = {
        "title": "Lock the PC",
        "action": "Lock the Windows PC.",
        "source": "System Safety",
    }

    changed_decision = {
        "title": "Close application",
        "action": "Close a supported application.",
        "source": "System Safety",
    }

    def fake_resolver(decision):
        if decision["title"] == "Lock the PC":
            return {
                "action_name": "lock_pc",
                "status": bridge.CONFIRM,
                "message": "Confirmation required.",
            }

        return {
            "action_name": "close_application",
            "status": bridge.CONFIRM,
            "message": "Confirmation required.",
        }

    monkeypatch.setattr(
        bridge,
        "resolve_decision_action",
        fake_resolver,
    )

    created = bridge.create_pending_confirmation(
        original_decision
    )

    assert created["success"] is True

    result = bridge.verify_pending_confirmation(
        changed_decision
    )

    assert result["success"] is False
    assert result["status"] == bridge.CONFIRM
    assert "does not match" in result["message"]

    bridge.clear_pending_confirmation()


def test_pending_confirmation_accepts_exact_decision(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()

    decision = {
        "title": "Lock the PC",
        "action": "Lock the Windows PC.",
        "source": "System Safety",
    }

    monkeypatch.setattr(
        bridge,
        "resolve_decision_action",
        lambda item: {
            "action_name": "lock_pc",
            "status": bridge.CONFIRM,
            "message": "Confirmation required.",
        },
    )

    created = bridge.create_pending_confirmation(decision)
    verified = bridge.verify_pending_confirmation(decision)

    assert created["success"] is True
    assert verified["success"] is True
    assert verified["status"] == bridge.CONFIRM
    assert verified["action_name"] == "lock_pc"
    assert verified["fingerprint"] == created["fingerprint"]

    bridge.clear_pending_confirmation()


def test_pending_confirmation_is_single_use(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()

    decision = {
        "title": "Lock the PC",
        "action": "Lock the Windows PC.",
        "source": "System Safety",
    }

    monkeypatch.setattr(
        bridge,
        "resolve_decision_action",
        lambda item: {
            "action_name": "lock_pc",
            "status": bridge.CONFIRM,
            "message": "Confirmation required.",
        },
    )

    created = bridge.create_pending_confirmation(decision)
    assert created["success"] is True

    first = bridge.consume_pending_confirmation(decision)

    assert first["success"] is True
    assert first["action_name"] == "lock_pc"
    assert bridge.get_pending_confirmation() is None

    second = bridge.consume_pending_confirmation(decision)

    assert second["success"] is False
    assert second["status"] == bridge.CONFIRM
    assert "No pending decision confirmation exists" in second["message"]


def test_pending_confirmation_expires_at_ttl(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()

    decision = {
        "title": "Lock the PC",
        "action": "Lock the Windows PC.",
        "source": "System Safety",
    }

    clock = {"now": 100.0}

    monkeypatch.setattr(
        bridge.time,
        "monotonic",
        lambda: clock["now"],
    )

    monkeypatch.setattr(
        bridge,
        "resolve_decision_action",
        lambda item: {
            "action_name": "lock_pc",
            "status": bridge.CONFIRM,
            "message": "Confirmation required.",
        },
    )

    created = bridge.create_pending_confirmation(decision)

    assert created["success"] is True

    # One second before TTL: still valid.
    clock["now"] = (
        100.0
        + bridge.PENDING_CONFIRMATION_TTL_SECONDS
        - 1
    )

    pending = bridge.get_pending_confirmation()

    assert pending is not None
    assert pending["action_name"] == "lock_pc"

    # Exactly at TTL: expired and automatically cleared.
    clock["now"] = (
        100.0
        + bridge.PENDING_CONFIRMATION_TTL_SECONDS
    )

    expired = bridge.get_pending_confirmation()

    assert expired is None
    assert bridge.get_pending_confirmation() is None


def test_expired_confirmation_cannot_be_consumed(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()

    decision = {
        "title": "Lock the PC",
        "action": "Lock the Windows PC.",
        "source": "System Safety",
    }

    clock = {"now": 500.0}

    monkeypatch.setattr(
        bridge.time,
        "monotonic",
        lambda: clock["now"],
    )

    monkeypatch.setattr(
        bridge,
        "resolve_decision_action",
        lambda item: {
            "action_name": "lock_pc",
            "status": bridge.CONFIRM,
            "message": "Confirmation required.",
        },
    )

    created = bridge.create_pending_confirmation(decision)
    assert created["success"] is True

    clock["now"] = (
        500.0
        + bridge.PENDING_CONFIRMATION_TTL_SECONDS
    )

    result = bridge.consume_pending_confirmation(decision)

    assert result["success"] is False
    assert result["status"] == bridge.CONFIRM
    assert bridge.get_pending_confirmation() is None
    assert "No pending decision confirmation exists" in result["message"]
