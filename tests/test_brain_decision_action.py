from core import brain


def test_ranked_decision_action_preview(monkeypatch):
    decisions = [
        {
            "title": "First decision",
            "action": "Review alerts.",
            "source": "Alert Intelligence",
            "rank": 1,
        },
        {
            "title": "Free disk space",
            "action": (
                "Review large files and safe cleanup recommendations, "
                "then free disk space."
            ),
            "source": "System Health",
            "rank": 2,
        },
    ]

    monkeypatch.setattr(
        brain,
        "get_ranked_decisions",
        lambda limit=10: decisions,
    )

    result = brain.process_command("decision action 2")

    assert "Rank: 2" in result
    assert "Decision: Free disk space" in result
    assert "Bridge Status: safe" in result
    assert "Route: cleanup analysis" in result
    assert "No action was executed." in result


def test_decision_action_rejects_invalid_rank():
    result = brain.process_command("decision action abc")

    assert result == (
        "Invalid decision rank. "
        "Example: decision action 2"
    )


def test_decision_action_rejects_unavailable_rank(monkeypatch):
    decisions = [
        {
            "title": "Only decision",
            "action": "Review alerts.",
            "source": "Alert Intelligence",
            "rank": 1,
        },
    ]

    monkeypatch.setattr(
        brain,
        "get_ranked_decisions",
        lambda limit=10: decisions,
    )

    result = brain.process_command("decision action 99")

    assert result == (
        "Decision rank 99 is not available. "
        "Available ranks: 1-1."
    )


def test_execute_ranked_decision_action(monkeypatch):
    decisions = [
        {
            "title": "Reduce RAM usage",
            "action": "Close unused applications and browser tabs.",
            "source": "System Health",
            "rank": 1,
        },
    ]

    monkeypatch.setattr(
        brain,
        "get_ranked_decisions",
        lambda limit=10: decisions,
    )

    called = {}

    def fake_execute_decision(decision, confirmed=False, target=None):
        called["decision"] = decision
        called["confirmed"] = confirmed

        return {
            "success": True,
            "status": "safe",
            "action_name": "open_task_manager",
            "route": None,
            "message": "Task Manager execution simulated.",
        }

    monkeypatch.setattr(
        brain,
        "execute_decision",
        fake_execute_decision,
    )

    result = brain.process_command(
        "execute decision action 1"
    )

    assert called["decision"] == decisions[0]
    assert called["confirmed"] is False
    assert "JERVIS DECISION ACTION EXECUTION" in result
    assert "Action: open_task_manager" in result
    assert "Success: Yes" in result
    assert "Task Manager execution simulated." in result


def test_execute_decision_action_rejects_invalid_rank(monkeypatch):
    called = {"value": False}

    def fake_execute_decision(decision, confirmed=False, target=None):
        called["value"] = True
        return {}

    monkeypatch.setattr(
        brain,
        "execute_decision",
        fake_execute_decision,
    )

    result = brain.process_command(
        "execute decision action abc"
    )

    assert result == (
        "Invalid decision rank. "
        "Example: execute decision action 3"
    )
    assert called["value"] is False


def test_confirm_decision_action_rejects_safe_action(monkeypatch):
    decisions = [
        {
            "title": "Reduce RAM usage",
            "action": "Close unused applications and browser tabs.",
            "source": "System Health",
            "rank": 1,
        },
    ]

    monkeypatch.setattr(
        brain,
        "get_ranked_decisions",
        lambda limit=10: decisions,
    )

    monkeypatch.setattr(
        brain,
        "resolve_decision_action",
        lambda decision: {
            "action_name": "open_task_manager",
            "status": "safe",
            "message": "Safe action.",
        },
    )

    called = {"value": False}

    def fake_execute_decision(decision, confirmed=False, target=None):
        called["value"] = True
        return {}

    monkeypatch.setattr(
        brain,
        "execute_decision",
        fake_execute_decision,
    )

    result = brain.process_command(
        "confirm decision action 1 A7F29C"
    )

    assert "Confirmation rejected." in result
    assert "Status: safe" in result
    assert called["value"] is False


def test_confirm_decision_action_uses_pending_context(monkeypatch):
    decisions = [
        {
            "title": "Lock the PC",
            "action": "Lock the Windows PC.",
            "source": "System Safety",
            "rank": 1,
        },
    ]

    monkeypatch.setattr(
        brain,
        "get_ranked_decisions",
        lambda limit=10: decisions,
    )

    monkeypatch.setattr(
        brain,
        "resolve_decision_action",
        lambda decision: {
            "action_name": "lock_pc",
            "status": brain.CONFIRM,
            "message": "Confirmation required.",
        },
    )

    pending = {"created": False, "consumed": False}
    calls = []

    def fake_create_pending_confirmation(decision):
        pending["created"] = True
        return {
            "success": True,
            "status": brain.CONFIRM,
            "action_name": "lock_pc",
            "token": "A7F29C",
            "message": "Pending confirmation context created.",
        }

    def fake_consume_pending_confirmation(decision, token=None):
        pending["received_token"] = token

        if not pending["created"] or pending["consumed"]:
            return {
                "success": False,
                "status": brain.CONFIRM,
                "message": "No pending decision confirmation exists.",
            }

        if token != "A7F29C":
            return {
                "success": False,
                "status": brain.CONFIRM,
                "message": "Invalid confirmation token.",
            }

        pending["consumed"] = True
        return {
            "success": True,
            "status": brain.CONFIRM,
            "action_name": "lock_pc",
            "message": "Pending confirmation verified and consumed.",
        }

    def fake_execute_decision(decision, confirmed=False, target=None):
        calls.append(
            {
                "decision": decision,
                "confirmed": confirmed,
            }
        )

        return {
            "success": True,
            "status": brain.CONFIRM,
            "action_name": "lock_pc",
            "route": None,
            "message": "PC lock simulated.",
        }

    monkeypatch.setattr(
        brain,
        "create_pending_confirmation",
        fake_create_pending_confirmation,
    )
    monkeypatch.setattr(
        brain,
        "consume_pending_confirmation",
        fake_consume_pending_confirmation,
    )
    monkeypatch.setattr(
        brain,
        "execute_decision",
        fake_execute_decision,
    )

    pending_result = brain.process_command(
        "execute decision action 1"
    )

    assert pending["created"] is True
    assert calls == []
    assert "PENDING CONFIRMATION" in pending_result
    assert "Confirmation Token: A7F29C" in pending_result
    assert "confirm decision action 1 A7F29C" in pending_result
    assert "No confirmation-required action was executed." in pending_result

    confirmed_result = brain.process_command(
        "confirm decision action 1 A7F29C"
    )

    assert pending["consumed"] is True
    assert pending["received_token"] == "A7F29C"
    assert len(calls) == 1
    assert calls[0]["decision"] == decisions[0]
    assert calls[0]["confirmed"] is True
    assert "JERVIS DECISION ACTION CONFIRMED" in confirmed_result
    assert "Action: lock_pc" in confirmed_result
    assert "Success: Yes" in confirmed_result
    assert "PC lock simulated." in confirmed_result

    replay_result = brain.process_command(
        "confirm decision action 1 A7F29C"
    )

    assert len(calls) == 1
    assert "Confirmation rejected." in replay_result
    assert "No pending decision confirmation exists." in replay_result


def test_confirm_decision_action_rejects_invalid_rank(monkeypatch):
    called = {"value": False}

    def fake_execute_decision(decision, confirmed=False, target=None):
        called["value"] = True
        return {}

    monkeypatch.setattr(
        brain,
        "execute_decision",
        fake_execute_decision,
    )

    result = brain.process_command(
        "confirm decision action abc"
    )

    assert result == (
        "Invalid confirmation command. "
        "Example: confirm decision action 3 A7F29C"
    )
    assert called["value"] is False



def test_confirm_decision_action_rejects_wrong_token(monkeypatch):
    decisions = [
        {
            "title": "Lock the PC",
            "action": "Lock the Windows PC.",
            "source": "System Safety",
            "rank": 1,
        },
    ]

    monkeypatch.setattr(
        brain,
        "get_ranked_decisions",
        lambda limit=10: decisions,
    )

    monkeypatch.setattr(
        brain,
        "resolve_decision_action",
        lambda decision: {
            "action_name": "lock_pc",
            "status": brain.CONFIRM,
            "message": "Confirmation required.",
        },
    )

    received = {}
    executed = {"value": False}

    def fake_consume_pending_confirmation(decision, token=None):
        received["decision"] = decision
        received["token"] = token

        return {
            "success": False,
            "status": brain.CONFIRM,
            "action_name": "lock_pc",
            "message": "Invalid confirmation token.",
        }

    def fake_execute_decision(decision, confirmed=False, target=None):
        executed["value"] = True
        return {}

    monkeypatch.setattr(
        brain,
        "consume_pending_confirmation",
        fake_consume_pending_confirmation,
    )

    monkeypatch.setattr(
        brain,
        "execute_decision",
        fake_execute_decision,
    )

    result = brain.process_command(
        "confirm decision action 1 BAD999"
    )

    assert received["decision"] == decisions[0]
    assert received["token"] == "BAD999"
    assert executed["value"] is False

    assert "Confirmation rejected." in result
    assert "Invalid confirmation token." in result
