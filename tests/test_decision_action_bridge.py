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
        changed_decision,
        created["token"],
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
    verified = bridge.verify_pending_confirmation(
        decision,
        created["token"],
    )

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

    first = bridge.consume_pending_confirmation(
        decision,
        created["token"],
    )

    assert first["success"] is True
    assert first["action_name"] == "lock_pc"
    assert bridge.get_pending_confirmation() is None

    second = bridge.consume_pending_confirmation(
        decision,
        created["token"],
    )

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

    result = bridge.consume_pending_confirmation(
        decision,
        created["token"],
    )

    assert result["success"] is False
    assert result["status"] == bridge.CONFIRM
    assert bridge.get_pending_confirmation() is None
    assert "No pending decision confirmation exists" in result["message"]



def test_pending_confirmation_rejects_missing_token(monkeypatch):
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

    result = bridge.verify_pending_confirmation(decision)

    assert result["success"] is False
    assert result["status"] == bridge.CONFIRM
    assert "Confirmation token is required." in result["message"]

    # Failed verification must not consume the valid pending session.
    assert bridge.get_pending_confirmation() is not None

    bridge.clear_pending_confirmation()


def test_pending_confirmation_rejects_wrong_token(monkeypatch):
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

    wrong_token = (
        "000000"
        if created["token"] != "000000"
        else "FFFFFF"
    )

    result = bridge.consume_pending_confirmation(
        decision,
        wrong_token,
    )

    assert result["success"] is False
    assert result["status"] == bridge.CONFIRM
    assert "Invalid confirmation token." in result["message"]

    # Wrong token must not destroy the legitimate pending session.
    pending = bridge.get_pending_confirmation()
    assert pending is not None
    assert pending["token"] == created["token"]

    bridge.clear_pending_confirmation()


def test_wrong_token_attempts_increment_and_invalidate_session(monkeypatch):
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

    wrong_token = (
        "000000"
        if created["token"] != "000000"
        else "FFFFFF"
    )

    # Wrong attempt 1.
    first = bridge.verify_pending_confirmation(
        decision,
        wrong_token,
    )

    assert first["success"] is False
    assert "2 confirmation attempt(s) remaining" in first["message"]

    pending = bridge.get_pending_confirmation()
    assert pending is not None
    assert pending["failed_attempts"] == 1

    # Wrong attempt 2.
    second = bridge.verify_pending_confirmation(
        decision,
        wrong_token,
    )

    assert second["success"] is False
    assert "1 confirmation attempt(s) remaining" in second["message"]

    pending = bridge.get_pending_confirmation()
    assert pending is not None
    assert pending["failed_attempts"] == 2

    # Wrong attempt 3 reaches the limit and destroys the session.
    third = bridge.verify_pending_confirmation(
        decision,
        wrong_token,
    )

    assert third["success"] is False
    assert "Maximum confirmation attempts reached" in third["message"]
    assert bridge.get_pending_confirmation() is None

    # Any later attempt sees no authorization context.
    fourth = bridge.verify_pending_confirmation(
        decision,
        created["token"],
    )

    assert fourth["success"] is False
    assert "No pending decision confirmation exists" in fourth["message"]


def test_missing_token_does_not_increment_failed_attempts(monkeypatch):
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

    before = bridge.get_pending_confirmation()
    assert before is not None
    assert before["failed_attempts"] == 0

    result = bridge.verify_pending_confirmation(
        decision,
        None,
    )

    assert result["success"] is False
    assert "Confirmation token is required." in result["message"]

    after = bridge.get_pending_confirmation()
    assert after is not None
    assert after["failed_attempts"] == 0

    bridge.clear_pending_confirmation()


def test_correct_token_succeeds_after_failed_attempts(monkeypatch):
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

    wrong_token = (
        "000000"
        if created["token"] != "000000"
        else "FFFFFF"
    )

    first = bridge.verify_pending_confirmation(
        decision,
        wrong_token,
    )
    second = bridge.verify_pending_confirmation(
        decision,
        wrong_token,
    )

    assert first["success"] is False
    assert second["success"] is False

    pending = bridge.get_pending_confirmation()
    assert pending is not None
    assert pending["failed_attempts"] == 2

    # Correct token remains valid before the attempt limit is reached.
    confirmed = bridge.consume_pending_confirmation(
        decision,
        created["token"],
    )

    assert confirmed["success"] is True
    assert confirmed["action_name"] == "lock_pc"

    # Successful consumption still preserves v7 one-time semantics.
    assert bridge.get_pending_confirmation() is None


def test_confirmation_audit_event_records_safe_metadata(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    monkeypatch.setattr(
        bridge.time,
        "time",
        lambda: 123456.0,
    )

    event = bridge._record_confirmation_audit_event(
        "confirmation_created",
        action_name="lock_pc",
        fingerprint="abc123",
        failed_attempts=0,
        reason="Confirmation session created.",
    )

    assert event["event_type"] == "confirmation_created"
    assert event["timestamp"] == 123456.0
    assert event["action_name"] == "lock_pc"
    assert event["fingerprint"] == "abc123"
    assert event["failed_attempts"] == 0
    assert event["reason"] == "Confirmation session created."

    # Audit events must never expose confirmation secrets.
    assert "token" not in event

    trail = bridge.get_confirmation_audit_trail()

    assert len(trail) == 1
    assert trail[0] == event
    assert "token" not in trail[0]

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_trail_returns_defensive_copies():
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "confirmation_failed",
        action_name="lock_pc",
        fingerprint="abc123",
        failed_attempts=1,
        reason="Invalid confirmation token.",
    )

    first = bridge.get_confirmation_audit_trail()

    first[0]["event_type"] = "tampered"
    first.append({"event_type": "injected"})

    second = bridge.get_confirmation_audit_trail()

    assert len(second) == 1
    assert second[0]["event_type"] == "confirmation_failed"

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_trail_is_bounded(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    monkeypatch.setattr(
        bridge,
        "MAX_CONFIRMATION_AUDIT_EVENTS",
        3,
    )

    for index in range(5):
        bridge._record_confirmation_audit_event(
            f"event_{index}",
            action_name="lock_pc",
        )

    trail = bridge.get_confirmation_audit_trail()

    assert len(trail) == 3
    assert [
        event["event_type"]
        for event in trail
    ] == [
        "event_2",
        "event_3",
        "event_4",
    ]

    bridge.clear_confirmation_audit_trail()


def test_confirmation_creation_is_audited_without_token(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()

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
    assert created["token"]

    trail = bridge.get_confirmation_audit_trail()
    assert len(trail) == 1

    event = trail[0]

    assert event["event_type"] == "confirmation_created"
    assert event["action_name"] == "lock_pc"
    assert event["fingerprint"] == created["fingerprint"]
    assert event["failed_attempts"] == 0

    assert "token" not in event

    audit_values = {
        str(value)
        for value in event.values()
        if value is not None
    }

    assert created["token"] not in audit_values

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()

def test_confirmation_failures_and_lockout_are_audited_without_tokens(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()

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

    valid_token = created["token"]
    wrong_tokens = ["111111", "222222", "333333"]

    if valid_token in wrong_tokens:
        wrong_tokens = ["AAAAAA", "BBBBBB", "CCCCCC"]

    for wrong_token in wrong_tokens:
        result = bridge.consume_pending_confirmation(
            decision,
            wrong_token,
        )

        assert result["success"] is False

    assert bridge.get_pending_confirmation() is None

    trail = bridge.get_confirmation_audit_trail()

    assert [
        event["event_type"]
        for event in trail
    ] == [
        "confirmation_created",
        "confirmation_failed",
        "confirmation_failed",
        "confirmation_failed",
        "confirmation_locked_out",
    ]

    failed_events = [
        event
        for event in trail
        if event["event_type"] == "confirmation_failed"
    ]

    assert [
        event["failed_attempts"]
        for event in failed_events
    ] == [1, 2, 3]

    lockout = trail[-1]

    assert lockout["event_type"] == "confirmation_locked_out"
    assert lockout["failed_attempts"] == 3
    assert lockout["action_name"] == "lock_pc"
    assert lockout["fingerprint"] == created["fingerprint"]

    serialized_trail = repr(trail)

    # Neither the valid token nor attempted tokens may be audited.
    assert valid_token not in serialized_trail

    for wrong_token in wrong_tokens:
        assert wrong_token not in serialized_trail

    assert all(
        "token" not in event
        for event in trail
    )

    bridge.clear_confirmation_audit_trail()


def test_successful_confirmation_consumption_is_audited(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()

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

    result = bridge.consume_pending_confirmation(
        decision,
        created["token"],
    )

    assert result["success"] is True
    assert bridge.get_pending_confirmation() is None

    trail = bridge.get_confirmation_audit_trail()

    assert [
        event["event_type"]
        for event in trail
    ] == [
        "confirmation_created",
        "confirmation_consumed",
    ]

    consumed = trail[-1]

    assert consumed["action_name"] == "lock_pc"
    assert consumed["fingerprint"] == created["fingerprint"]
    assert consumed["failed_attempts"] == 0
    assert "token" not in consumed
    assert created["token"] not in repr(trail)

    bridge.clear_confirmation_audit_trail()


def test_expired_confirmation_is_audited_without_token(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()

    decision = {
        "title": "Lock the PC",
        "action": "Lock the Windows PC.",
        "source": "System Safety",
    }

    clock = {"now": 700.0}

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

    clock["now"] = (
        700.0
        + bridge.PENDING_CONFIRMATION_TTL_SECONDS
    )

    assert bridge.get_pending_confirmation() is None

    trail = bridge.get_confirmation_audit_trail()

    assert [
        event["event_type"]
        for event in trail
    ] == [
        "confirmation_created",
        "confirmation_expired",
    ]

    expired = trail[-1]

    assert expired["action_name"] == "lock_pc"
    assert expired["fingerprint"] == created["fingerprint"]
    assert expired["failed_attempts"] == 0
    assert "token" not in expired
    assert created["token"] not in repr(trail)

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_events_share_session_id(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()

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

    wrong_token = (
        "000000"
        if created["token"] != "000000"
        else "FFFFFF"
    )

    failed = bridge.consume_pending_confirmation(
        decision,
        wrong_token,
    )
    assert failed["success"] is False

    consumed = bridge.consume_pending_confirmation(
        decision,
        created["token"],
    )
    assert consumed["success"] is True

    trail = bridge.get_confirmation_audit_trail()

    assert [
        event["event_type"]
        for event in trail
    ] == [
        "confirmation_created",
        "confirmation_failed",
        "confirmation_consumed",
    ]

    session_ids = {
        event["session_id"]
        for event in trail
    }

    assert session_ids == {created["session_id"]}
    assert created["session_id"]
    assert created["token"] not in repr(trail)

    bridge.clear_confirmation_audit_trail()


def test_new_confirmation_sessions_use_distinct_session_ids(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()

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

    first = bridge.create_pending_confirmation(decision)
    first_session_id = first["session_id"]

    bridge.clear_pending_confirmation()

    second = bridge.create_pending_confirmation(decision)
    second_session_id = second["session_id"]

    assert first_session_id
    assert second_session_id
    assert first_session_id != second_session_id

    trail = bridge.get_confirmation_audit_trail()

    created_events = [
        event
        for event in trail
        if event["event_type"] == "confirmation_created"
    ]

    assert len(created_events) == 2
    assert created_events[0]["session_id"] == first_session_id
    assert created_events[1]["session_id"] == second_session_id

    assert first["token"] not in repr(trail)
    assert second["token"] not in repr(trail)

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_integrity_accepts_valid_chain():
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "confirmation_created",
        action_name="lock_pc",
        fingerprint="fingerprint-1",
        failed_attempts=0,
        reason="Created.",
        session_id="SESSION-1",
    )

    bridge._record_confirmation_audit_event(
        "confirmation_failed",
        action_name="lock_pc",
        fingerprint="fingerprint-1",
        failed_attempts=1,
        reason="Invalid confirmation token.",
        session_id="SESSION-1",
    )

    result = bridge.verify_confirmation_audit_integrity()

    assert result["valid"] is True
    assert result["event_count"] == 2
    assert result["failed_index"] is None

    trail = bridge.get_confirmation_audit_trail()

    assert trail[0]["previous_hash"] is None
    assert trail[0]["event_hash"]
    assert trail[1]["previous_hash"] == trail[0]["event_hash"]

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_integrity_detects_modified_event():
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "confirmation_created",
        action_name="lock_pc",
        reason="Created.",
        session_id="SESSION-1",
    )

    bridge._CONFIRMATION_AUDIT_TRAIL[0]["reason"] = "Tampered."

    result = bridge.verify_confirmation_audit_integrity()

    assert result["valid"] is False
    assert result["failed_index"] == 0
    assert "does not match event data" in result["reason"]

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_integrity_detects_deleted_event():
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    for index in range(3):
        bridge._record_confirmation_audit_event(
            f"event-{index}",
            session_id="SESSION-1",
        )

    del bridge._CONFIRMATION_AUDIT_TRAIL[1]

    result = bridge.verify_confirmation_audit_integrity()

    assert result["valid"] is False
    assert result["failed_index"] == 1
    assert "Previous audit hash does not match" in result["reason"]

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_integrity_detects_reordered_events():
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    for index in range(3):
        bridge._record_confirmation_audit_event(
            f"event-{index}",
            session_id="SESSION-1",
        )

    trail = bridge._CONFIRMATION_AUDIT_TRAIL
    trail[1], trail[2] = trail[2], trail[1]

    result = bridge.verify_confirmation_audit_integrity()

    assert result["valid"] is False
    assert result["failed_index"] == 1

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_clear_resets_chain_anchor():
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "old-event",
        session_id="OLD",
    )

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "new-event",
        session_id="NEW",
    )

    trail = bridge.get_confirmation_audit_trail()

    assert len(trail) == 1
    assert trail[0]["previous_hash"] is None

    result = bridge.verify_confirmation_audit_integrity()

    assert result["valid"] is True

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_integrity_survives_bounded_rollover():
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    total_events = bridge.MAX_CONFIRMATION_AUDIT_EVENTS + 5

    for index in range(total_events):
        bridge._record_confirmation_audit_event(
            f"event-{index}",
            session_id="ROLLOVER",
        )

    trail = bridge.get_confirmation_audit_trail()

    assert len(trail) == bridge.MAX_CONFIRMATION_AUDIT_EVENTS
    assert bridge._CONFIRMATION_AUDIT_ANCHOR_HASH is not None
    assert (
        trail[0]["previous_hash"]
        == bridge._CONFIRMATION_AUDIT_ANCHOR_HASH
    )

    result = bridge.verify_confirmation_audit_integrity()

    assert result["valid"] is True
    assert (
        result["event_count"]
        == bridge.MAX_CONFIRMATION_AUDIT_EVENTS
    )

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_serialization_excludes_pending_token(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()
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

    state = bridge._serialize_confirmation_audit_state()
    serialized = bridge.json.dumps(state)

    assert state["version"] == bridge.CONFIRMATION_AUDIT_STORAGE_VERSION
    assert "anchor_hash" in state
    assert isinstance(state["events"], list)

    # Confirmation credentials must remain process-local.
    assert created["token"] not in serialized
    assert "token" not in state
    assert "pending_confirmation" not in state

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_atomic_write_creates_json_file(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    data_dir = tmp_path / "data"
    audit_file = data_dir / "decision_confirmation_audit.json"

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_DATA_DIR",
        data_dir,
    )
    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    bridge._record_confirmation_audit_event(
        "confirmation_created",
        action_name="lock_pc",
        fingerprint="fingerprint-1",
        failed_attempts=0,
        reason="Created.",
        session_id="SESSION-1",
    )

    result = bridge._atomic_write_confirmation_audit_state()

    assert result == audit_file
    assert audit_file.exists()

    state = bridge.json.loads(
        audit_file.read_text(encoding="utf-8")
    )

    assert state["version"] == bridge.CONFIRMATION_AUDIT_STORAGE_VERSION
    assert state["anchor_hash"] is None
    assert len(state["events"]) == 1
    assert state["events"][0]["event_type"] == "confirmation_created"
    assert state["events"][0]["session_id"] == "SESSION-1"

    temporary_file = audit_file.with_name(
        audit_file.name + ".tmp"
    )
    assert temporary_file.exists() is False

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_atomic_write_replaces_existing_file(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)

    audit_file = data_dir / "decision_confirmation_audit.json"
    audit_file.write_text(
        '{"old": true}',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_DATA_DIR",
        data_dir,
    )
    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    bridge._record_confirmation_audit_event(
        "confirmation_created",
        session_id="SESSION-REPLACE",
    )

    bridge._atomic_write_confirmation_audit_state()

    state = bridge.json.loads(
        audit_file.read_text(encoding="utf-8")
    )

    assert "old" not in state
    assert len(state["events"]) == 1
    assert state["events"][0]["session_id"] == "SESSION-REPLACE"

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_atomic_write_cleans_temp_on_failure(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    data_dir = tmp_path / "data"
    audit_file = data_dir / "decision_confirmation_audit.json"

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_DATA_DIR",
        data_dir,
    )
    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    def fail_replace(source, destination):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(
        bridge.os,
        "replace",
        fail_replace,
    )

    try:
        bridge._atomic_write_confirmation_audit_state()
    except OSError as error:
        assert "simulated replace failure" in str(error)
    else:
        raise AssertionError("Expected atomic audit write to fail.")

    temporary_file = audit_file.with_name(
        audit_file.name + ".tmp"
    )

    assert temporary_file.exists() is False
    assert audit_file.exists() is False

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_loader_restores_valid_state(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    data_dir = tmp_path / "data"
    audit_file = data_dir / "decision_confirmation_audit.json"

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_DATA_DIR",
        data_dir,
    )
    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    bridge._record_confirmation_audit_event(
        "confirmation_created",
        action_name="lock_pc",
        fingerprint="fingerprint-restore",
        failed_attempts=0,
        reason="Created.",
        session_id="SESSION-RESTORE",
    )

    expected = bridge.get_confirmation_audit_trail()
    bridge._atomic_write_confirmation_audit_state()

    # Simulate loss of process-local state after restart.
    bridge.clear_confirmation_audit_trail()
    assert bridge.get_confirmation_audit_trail() == []

    result = bridge._load_confirmation_audit_state()

    assert result["success"] is True
    assert result["loaded"] is True
    assert result["event_count"] == 1
    assert bridge.get_confirmation_audit_trail() == expected
    assert bridge.verify_confirmation_audit_integrity()["valid"] is True

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_loader_missing_file_is_clean_noop(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    audit_file = (
        tmp_path
        / "data"
        / "decision_confirmation_audit.json"
    )

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    result = bridge._load_confirmation_audit_state()

    assert result["success"] is True
    assert result["loaded"] is False
    assert bridge.get_confirmation_audit_trail() == []


def test_confirmation_audit_loader_rejects_malformed_json_without_mutation(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "existing_live_event",
        session_id="LIVE-SESSION",
    )
    before = bridge.get_confirmation_audit_trail()

    audit_file = tmp_path / "decision_confirmation_audit.json"
    audit_file.write_text(
        "{not valid json",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    result = bridge._load_confirmation_audit_state()

    assert result["success"] is False
    assert result["loaded"] is False
    assert bridge.get_confirmation_audit_trail() == before
    assert bridge.verify_confirmation_audit_integrity()["valid"] is True

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_loader_rejects_wrong_version_without_mutation(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "existing_live_event",
        session_id="LIVE-VERSION",
    )
    before = bridge.get_confirmation_audit_trail()

    audit_file = tmp_path / "decision_confirmation_audit.json"
    audit_file.write_text(
        bridge.json.dumps(
            {
                "version": 999,
                "anchor_hash": None,
                "events": [],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    result = bridge._load_confirmation_audit_state()

    assert result["success"] is False
    assert result["loaded"] is False
    assert bridge.get_confirmation_audit_trail() == before

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_loader_rejects_tampered_chain_without_mutation(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "persisted_event",
        action_name="lock_pc",
        session_id="PERSISTED-SESSION",
    )

    state = bridge._serialize_confirmation_audit_state()

    # Tamper with hashed event data without recomputing event_hash.
    state["events"][0]["reason"] = "tampered"

    bridge.clear_confirmation_audit_trail()
    bridge._record_confirmation_audit_event(
        "existing_live_event",
        session_id="LIVE-TAMPER",
    )
    before = bridge.get_confirmation_audit_trail()

    audit_file = tmp_path / "decision_confirmation_audit.json"
    audit_file.write_text(
        bridge.json.dumps(state),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    result = bridge._load_confirmation_audit_state()

    assert result["success"] is False
    assert result["loaded"] is False
    assert bridge.get_confirmation_audit_trail() == before
    assert bridge.verify_confirmation_audit_integrity()["valid"] is True

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_loader_rejects_oversized_history_without_mutation(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "existing_live_event",
        session_id="LIVE-OVERSIZE",
    )
    before = bridge.get_confirmation_audit_trail()

    audit_file = tmp_path / "decision_confirmation_audit.json"
    audit_file.write_text(
        bridge.json.dumps(
            {
                "version": bridge.CONFIRMATION_AUDIT_STORAGE_VERSION,
                "anchor_hash": None,
                "events": [
                    {}
                    for _ in range(
                        bridge.MAX_CONFIRMATION_AUDIT_EVENTS + 1
                    )
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    result = bridge._load_confirmation_audit_state()

    assert result["success"] is False
    assert result["loaded"] is False
    assert bridge.get_confirmation_audit_trail() == before

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_loader_restores_rollover_anchor(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    data_dir = tmp_path / "data"
    audit_file = data_dir / "decision_confirmation_audit.json"

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_DATA_DIR",
        data_dir,
    )
    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    total_events = bridge.MAX_CONFIRMATION_AUDIT_EVENTS + 5

    for index in range(total_events):
        bridge._record_confirmation_audit_event(
            "rollover_test",
            action_name="lock_pc",
            fingerprint=f"fingerprint-{index}",
            failed_attempts=0,
            reason=f"Event {index}",
            session_id=f"SESSION-{index}",
        )

    assert (
        len(bridge.get_confirmation_audit_trail())
        == bridge.MAX_CONFIRMATION_AUDIT_EVENTS
    )

    assert bridge._CONFIRMATION_AUDIT_ANCHOR_HASH is not None

    expected_events = bridge.get_confirmation_audit_trail()
    expected_anchor = bridge._CONFIRMATION_AUDIT_ANCHOR_HASH

    before_integrity = bridge.verify_confirmation_audit_integrity()
    assert before_integrity["valid"] is True

    bridge._atomic_write_confirmation_audit_state()

    persisted = bridge.json.loads(
        audit_file.read_text(encoding="utf-8")
    )

    assert persisted["anchor_hash"] == expected_anchor
    assert len(persisted["events"]) == bridge.MAX_CONFIRMATION_AUDIT_EVENTS

    # Simulate a fresh process losing all process-local audit state.
    bridge.clear_confirmation_audit_trail()

    assert bridge.get_confirmation_audit_trail() == []
    assert bridge._CONFIRMATION_AUDIT_ANCHOR_HASH is None

    result = bridge._load_confirmation_audit_state()

    assert result["success"] is True
    assert result["loaded"] is True
    assert (
        result["event_count"]
        == bridge.MAX_CONFIRMATION_AUDIT_EVENTS
    )

    assert bridge._CONFIRMATION_AUDIT_ANCHOR_HASH == expected_anchor
    assert bridge.get_confirmation_audit_trail() == expected_events

    after_integrity = bridge.verify_confirmation_audit_integrity()

    assert after_integrity["valid"] is True
    assert (
        after_integrity["event_count"]
        == bridge.MAX_CONFIRMATION_AUDIT_EVENTS
    )

    # First retained event must still link to the persisted rollover anchor.
    restored = bridge.get_confirmation_audit_trail()

    assert restored[0]["previous_hash"] == expected_anchor

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_safe_persistence_reports_success(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    data_dir = tmp_path / "data"
    audit_file = data_dir / "decision_confirmation_audit.json"

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_DATA_DIR",
        data_dir,
    )
    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    bridge._record_confirmation_audit_event(
        "persistence_test",
        session_id="SESSION-PERSIST",
    )

    result = bridge._persist_confirmation_audit_state_safely()

    assert result["success"] is True
    assert result["path"] == audit_file
    assert audit_file.exists() is True

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_safe_persistence_failure_preserves_live_state(
    monkeypatch,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "persistence_failure_test",
        session_id="SESSION-LIVE",
    )

    before = bridge.get_confirmation_audit_trail()

    def fail_write():
        raise OSError("simulated disk failure")

    monkeypatch.setattr(
        bridge,
        "_atomic_write_confirmation_audit_state",
        fail_write,
    )

    result = bridge._persist_confirmation_audit_state_safely()

    assert result["success"] is False
    assert result["path"] is None
    assert "simulated disk failure" in result["message"]

    # Persistence failure must not damage the live security chain.
    assert bridge.get_confirmation_audit_trail() == before
    assert bridge.verify_confirmation_audit_integrity()["valid"] is True

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_recorder_persists_when_requested(monkeypatch):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    calls = []

    def fake_persist():
        calls.append(
            {
                "events": bridge.get_confirmation_audit_trail(),
                "anchor": bridge._CONFIRMATION_AUDIT_ANCHOR_HASH,
            }
        )
        return {
            "success": True,
            "path": None,
            "message": "Persisted.",
        }

    monkeypatch.setattr(
        bridge,
        "_persist_confirmation_audit_state_safely",
        fake_persist,
    )

    event = bridge._record_confirmation_audit_event(
        "confirmation_created",
        session_id="SESSION-PERSIST-ROUTE",
        persist=True,
    )

    assert event["event_type"] == "confirmation_created"
    assert len(calls) == 1
    assert len(calls[0]["events"]) == 1
    assert (
        calls[0]["events"][0]["event_hash"]
        == event["event_hash"]
    )

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_recorder_does_not_persist_by_default(
    monkeypatch,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    called = {"value": False}

    def fake_persist():
        called["value"] = True
        return {
            "success": True,
            "path": None,
            "message": "Persisted.",
        }

    monkeypatch.setattr(
        bridge,
        "_persist_confirmation_audit_state_safely",
        fake_persist,
    )

    bridge._record_confirmation_audit_event(
        "test_event",
        session_id="SESSION-NO-PERSIST",
    )

    assert called["value"] is False

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_recorder_survives_persistence_failure(
    monkeypatch,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    def fake_persist():
        return {
            "success": False,
            "path": None,
            "message": "simulated persistence failure",
        }

    monkeypatch.setattr(
        bridge,
        "_persist_confirmation_audit_state_safely",
        fake_persist,
    )

    event = bridge._record_confirmation_audit_event(
        "confirmation_failed",
        failed_attempts=1,
        session_id="SESSION-FAIL-SAFE",
        persist=True,
    )

    assert event["event_type"] == "confirmation_failed"
    assert len(bridge.get_confirmation_audit_trail()) == 1
    assert bridge.verify_confirmation_audit_integrity()["valid"] is True

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_rollover_is_updated_before_persistence(
    monkeypatch,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    for index in range(bridge.MAX_CONFIRMATION_AUDIT_EVENTS):
        bridge._record_confirmation_audit_event(
            "rollover_seed",
            session_id=f"SEED-{index}",
        )

    assert bridge._CONFIRMATION_AUDIT_ANCHOR_HASH is None

    captured = {}

    def fake_persist():
        captured["anchor"] = bridge._CONFIRMATION_AUDIT_ANCHOR_HASH
        captured["events"] = bridge.get_confirmation_audit_trail()

        return {
            "success": True,
            "path": None,
            "message": "Persisted.",
        }

    monkeypatch.setattr(
        bridge,
        "_persist_confirmation_audit_state_safely",
        fake_persist,
    )

    bridge._record_confirmation_audit_event(
        "rollover_trigger",
        session_id="ROLLOVER-TRIGGER",
        persist=True,
    )

    assert captured["anchor"] is not None
    assert len(captured["events"]) == bridge.MAX_CONFIRMATION_AUDIT_EVENTS
    assert (
        captured["events"][0]["previous_hash"]
        == captured["anchor"]
    )

    bridge.clear_confirmation_audit_trail()


def test_real_confirmation_lifecycle_requests_audit_persistence(
    monkeypatch,
):
    import core.decision_action_bridge as bridge

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()

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

    persisted_states = []

    def fake_persist():
        persisted_states.append(
            {
                "events": bridge.get_confirmation_audit_trail(),
                "anchor": bridge._CONFIRMATION_AUDIT_ANCHOR_HASH,
            }
        )

        return {
            "success": True,
            "path": None,
            "message": "Persisted.",
        }

    monkeypatch.setattr(
        bridge,
        "_persist_confirmation_audit_state_safely",
        fake_persist,
    )

    created = bridge.create_pending_confirmation(decision)

    assert created["success"] is True
    assert len(persisted_states) == 1

    first_state = persisted_states[0]

    assert len(first_state["events"]) == 1

    created_event = first_state["events"][0]

    assert created_event["event_type"] == "confirmation_created"
    assert created_event["action_name"] == "lock_pc"
    assert created_event["session_id"] == created["session_id"]

    # Confirmation secrets must never enter the persisted audit event.
    assert "token" not in created_event
    assert created["token"] not in str(created_event)

    assert bridge.verify_confirmation_audit_integrity()["valid"] is True

    bridge.clear_pending_confirmation()
    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_initializer_handles_clean_first_run(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    audit_file = (
        tmp_path
        / "data"
        / "decision_confirmation_audit.json"
    )

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    result = bridge.initialize_confirmation_audit_state()

    assert result["success"] is True
    assert result["loaded"] is False
    assert result["initialized"] is True
    assert result["event_count"] == 0
    assert bridge.get_confirmation_audit_trail() == []
    assert bridge.verify_confirmation_audit_integrity()["valid"] is True


def test_confirmation_audit_initializer_restores_persisted_state(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    data_dir = tmp_path / "data"
    audit_file = data_dir / "decision_confirmation_audit.json"

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_DATA_DIR",
        data_dir,
    )
    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    bridge._record_confirmation_audit_event(
        "startup_restore_test",
        action_name="lock_pc",
        fingerprint="startup-fingerprint",
        failed_attempts=0,
        reason="Startup restoration test.",
        session_id="STARTUP-SESSION",
    )

    expected = bridge.get_confirmation_audit_trail()

    bridge._atomic_write_confirmation_audit_state()

    # Simulate process-local state being lost on restart.
    bridge.clear_confirmation_audit_trail()

    result = bridge.initialize_confirmation_audit_state()

    assert result["success"] is True
    assert result["loaded"] is True
    assert result["initialized"] is True
    assert result["event_count"] == 1

    assert bridge.get_confirmation_audit_trail() == expected
    assert bridge.verify_confirmation_audit_integrity()["valid"] is True

    bridge.clear_confirmation_audit_trail()


def test_confirmation_audit_initializer_rejects_corrupt_storage_without_mutation(
    monkeypatch,
    tmp_path,
):
    import core.decision_action_bridge as bridge

    bridge.clear_confirmation_audit_trail()

    bridge._record_confirmation_audit_event(
        "existing_live_event",
        session_id="LIVE-STARTUP-STATE",
    )

    before = bridge.get_confirmation_audit_trail()

    audit_file = tmp_path / "decision_confirmation_audit.json"

    audit_file.write_text(
        "{corrupt startup audit state",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        bridge,
        "CONFIRMATION_AUDIT_FILE",
        audit_file,
    )

    result = bridge.initialize_confirmation_audit_state()

    assert result["success"] is False
    assert result["loaded"] is False
    assert result["initialized"] is False

    # Failed startup recovery must not partially replace live state.
    assert bridge.get_confirmation_audit_trail() == before
    assert bridge.verify_confirmation_audit_integrity()["valid"] is True

    bridge.clear_confirmation_audit_trail()
