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


def test_security_decision_command_healthy(monkeypatch):
    monkeypatch.setattr(
        brain,
        "get_security_decision",
        lambda: {
            "title": "Maintain security bootstrap health",
            "priority": "Low",
            "reason": "Security bootstrap health is healthy at 100/100.",
            "impact": "Security bootstrap reliability",
            "confidence": 100.0,
            "action": "No corrective action is required.",
            "source": "Security Health Intelligence",
            "requires_manual_review": False,
            "automation_allowed": False,
        },
    )

    result = brain.process_command("security decision")

    assert "JERVIS SECURITY DECISION" in result
    assert "Maintain security bootstrap health" in result
    assert "Priority: Low" in result
    assert "Confidence: 100.0%" in result
    assert "Manual Review Required: False" in result
    assert "Automation Allowed: False" in result
    assert "No security action is executed automatically." in result


def test_security_decision_command_critical(monkeypatch):
    monkeypatch.setattr(
        brain,
        "get_security_decision",
        lambda: {
            "title": "Resolve critical security bootstrap instability",
            "priority": "Critical",
            "reason": "Critical security bootstrap instability detected.",
            "impact": "Security-sensitive automation reliability",
            "confidence": 99.0,
            "action": (
                "Inspect confirmation audit initialization failures "
                "before relying on security-sensitive automation."
            ),
            "source": "Security Health Intelligence",
            "requires_manual_review": True,
            "automation_allowed": False,
        },
    )

    result = brain.process_command("security health decision")

    assert "Resolve critical security bootstrap instability" in result
    assert "Priority: Critical" in result
    assert "Confidence: 99.0%" in result
    assert "Manual Review Required: True" in result
    assert "Automation Allowed: False" in result


def test_security_decision_command_aliases(monkeypatch):
    monkeypatch.setattr(
        brain,
        "get_security_decision",
        lambda: {
            "title": "Test security decision",
            "priority": "High",
            "reason": "Test reason.",
            "impact": "Security reliability",
            "confidence": 95.0,
            "action": "Review security health.",
            "source": "Security Health Intelligence",
            "requires_manual_review": True,
            "automation_allowed": False,
        },
    )

    commands = [
        "security decision",
        "security health decision",
        "security decision intelligence",
        "security bootstrap decision",
    ]

    for command in commands:
        result = brain.process_command(command)

        assert "JERVIS SECURITY DECISION" in result
        assert "Test security decision" in result
        assert "Automation Allowed: False" in result


def test_security_decision_command_is_advisory_only(monkeypatch):
    called = {"count": 0}

    def fake_security_decision():
        called["count"] += 1

        return {
            "title": "Review security bootstrap instability",
            "priority": "High",
            "reason": "Security bootstrap instability detected.",
            "impact": "Security bootstrap reliability",
            "confidence": 95.0,
            "action": "Review Security Health Intelligence.",
            "source": "Security Health Intelligence",
            "requires_manual_review": True,
            "automation_allowed": False,
        }

    monkeypatch.setattr(
        brain,
        "get_security_decision",
        fake_security_decision,
    )

    result = brain.process_command("security decision")

    assert called["count"] == 1
    assert "Automation Allowed: False" in result
    assert "advisory only" in result
    assert "No security action is executed automatically." in result

def test_confirmation_audit_status_command(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_status",
        lambda: {
            "status": "healthy",
            "integrity_valid": True,
            "event_count": 7,
            "max_events": 100,
            "has_rollover_anchor": True,
            "latest_event_type": "confirmation_rejected",
        },
    )

    result = brain.process_command(
        "confirmation audit status"
    )

    assert "JERVIS CONFIRMATION AUDIT STATUS" in result
    assert "Status: healthy" in result
    assert "Integrity Valid: True" in result
    assert "Stored Events: 7" in result
    assert "Maximum Events: 100" in result
    assert "Rollover Anchor Present: True" in result
    assert "Latest Event Type: confirmation_rejected" in result
    assert "read-only" in result


def test_confirmation_audit_status_aliases(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_status",
        lambda: {
            "status": "healthy",
            "integrity_valid": True,
            "event_count": 0,
            "max_events": 100,
            "has_rollover_anchor": False,
            "latest_event_type": None,
        },
    )

    commands = [
        "confirmation audit status",
        "confirmation security status",
        "confirmation audit health",
        "audit integrity status",
    ]

    for command in commands:
        result = brain.process_command(command)

        assert "JERVIS CONFIRMATION AUDIT STATUS" in result
        assert "Status: healthy" in result


def test_confirmation_audit_status_integrity_failure(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_status",
        lambda: {
            "status": "integrity_failure",
            "integrity_valid": False,
            "event_count": 5,
            "max_events": 100,
            "has_rollover_anchor": False,
            "latest_event_type": "confirmation_created",
        },
    )

    result = brain.process_command(
        "confirmation audit status"
    )

    assert "Status: integrity_failure" in result
    assert "Integrity Valid: False" in result
    assert "Stored Events: 5" in result


def test_confirmation_audit_status_handles_empty_history(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_status",
        lambda: {
            "status": "healthy",
            "integrity_valid": True,
            "event_count": 0,
            "max_events": 100,
            "has_rollover_anchor": False,
            "latest_event_type": None,
        },
    )

    result = brain.process_command(
        "confirmation audit status"
    )

    assert "Stored Events: 0" in result
    assert "Latest Event Type: None" in result


def test_confirmation_audit_status_command_is_read_only(monkeypatch):
    import core.brain as brain

    calls = {"status": 0}

    def fake_status():
        calls["status"] += 1

        return {
            "status": "healthy",
            "integrity_valid": True,
            "event_count": 3,
            "max_events": 100,
            "has_rollover_anchor": False,
            "latest_event_type": "confirmation_rejected",
        }

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_status",
        fake_status,
    )

    result = brain.process_command(
        "confirmation audit status"
    )

    assert calls["status"] == 1
    assert "read-only" in result
    assert (
        "No confirmation state or audit event is modified."
        in result
    )


def test_confirmation_audit_intelligence_report_command(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_intelligence_report",
        lambda: "TEST CONFIRMATION AUDIT INTELLIGENCE REPORT",
    )

    result = brain.process_command(
        "confirmation audit intelligence"
    )

    assert result == "TEST CONFIRMATION AUDIT INTELLIGENCE REPORT"


def test_confirmation_audit_intelligence_report_aliases(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_intelligence_report",
        lambda: "TEST AUDIT REPORT",
    )

    commands = [
        "confirmation audit intelligence",
        "confirmation audit intelligence report",
        "confirmation intelligence",
        "confirmation intelligence report",
    ]

    for command in commands:
        result = brain.process_command(command)

        assert result == "TEST AUDIT REPORT"


def test_confirmation_audit_score_command(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_intelligence",
        lambda: {
            "score": 72,
            "status": "warning",
            "integrity_valid": True,
            "event_count": 9,
            "failed_confirmations": 3,
            "lockouts": 0,
            "expired_confirmations": 1,
            "successful_confirmations": 5,
            "automation_allowed": False,
            "read_only": True,
        },
    )

    result = brain.process_command(
        "confirmation audit score"
    )

    assert "JERVIS CONFIRMATION AUDIT INTELLIGENCE SCORE" in result
    assert "Score: 72/100" in result
    assert "Status: warning" in result
    assert "Integrity Valid: True" in result
    assert "Audit Events: 9" in result
    assert "Failed Confirmations: 3" in result
    assert "Lockouts: 0" in result
    assert "Expired Confirmations: 1" in result
    assert "Successful Confirmations: 5" in result
    assert "read-only" in result
    assert "Automatic execution is disabled." in result


def test_confirmation_audit_score_alias(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_intelligence",
        lambda: {
            "score": 100,
            "status": "healthy",
            "integrity_valid": True,
            "event_count": 0,
            "failed_confirmations": 0,
            "lockouts": 0,
            "expired_confirmations": 0,
            "successful_confirmations": 0,
            "automation_allowed": False,
            "read_only": True,
        },
    )

    result = brain.process_command(
        "confirmation intelligence score"
    )

    assert "Score: 100/100" in result
    assert "Status: healthy" in result


def test_confirmation_audit_score_integrity_failure(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_intelligence",
        lambda: {
            "score": 0,
            "status": "critical",
            "integrity_valid": False,
            "event_count": 5,
            "failed_confirmations": 0,
            "lockouts": 0,
            "expired_confirmations": 0,
            "successful_confirmations": 0,
            "automation_allowed": False,
            "read_only": True,
        },
    )

    result = brain.process_command(
        "confirmation audit score"
    )

    assert "Score: 0/100" in result
    assert "Status: critical" in result
    assert "Integrity Valid: False" in result


def test_confirmation_audit_intelligence_brain_route_is_read_only(
    monkeypatch,
):
    import core.brain as brain

    calls = {
        "intelligence": 0,
    }

    def fake_intelligence():
        calls["intelligence"] += 1

        return {
            "score": 100,
            "status": "healthy",
            "integrity_valid": True,
            "event_count": 0,
            "failed_confirmations": 0,
            "lockouts": 0,
            "expired_confirmations": 0,
            "successful_confirmations": 0,
            "automation_allowed": False,
            "read_only": True,
        }

    monkeypatch.setattr(
        brain,
        "get_confirmation_audit_intelligence",
        fake_intelligence,
    )

    result = brain.process_command(
        "confirmation audit score"
    )

    assert calls["intelligence"] == 1
    assert "read-only" in result
    assert "Automatic execution is disabled." in result


def test_confirmation_threat_analysis_command(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_analysis_report",
        lambda: "TEST V30 THREAT REPORT",
    )

    result = brain.process_command(
        "confirmation threat analysis"
    )

    assert result == "TEST V30 THREAT REPORT"


def test_confirmation_threat_analysis_aliases(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_analysis_report",
        lambda: "TEST V30 THREAT REPORT",
    )

    commands = [
        "confirmation threat analysis",
        "confirmation threat analysis report",
        "confirmation risk analysis",
        "confirmation risk",
    ]

    for command in commands:
        result = brain.process_command(command)

        assert result == "TEST V30 THREAT REPORT"


def test_confirmation_threat_score_command(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_analysis",
        lambda: {
            "risk_score": 82,
            "risk_classification": "high",
            "integrity_valid": True,
            "event_count": 14,
            "human_review_required": True,
        },
    )

    result = brain.process_command(
        "confirmation threat score"
    )

    assert "JERVIS CONFIRMATION THREAT ANALYSIS SCORE" in result
    assert "Risk Score: 82/100" in result
    assert "Risk Classification: high" in result
    assert "Integrity Valid: True" in result
    assert "Audit Events: 14" in result
    assert "Human Review Required: True" in result
    assert "read-only" in result
    assert "Automatic execution is disabled." in result


def test_confirmation_risk_score_alias(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_analysis",
        lambda: {
            "risk_score": 35,
            "risk_classification": "moderate",
            "integrity_valid": True,
            "event_count": 5,
            "human_review_required": False,
        },
    )

    result = brain.process_command(
        "confirmation risk score"
    )

    assert "Risk Score: 35/100" in result
    assert "Risk Classification: moderate" in result
    assert "Human Review Required: False" in result


def test_confirmation_threat_score_integrity_failure(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_analysis",
        lambda: {
            "risk_score": 100,
            "risk_classification": "critical",
            "integrity_valid": False,
            "event_count": 9,
            "human_review_required": True,
        },
    )

    result = brain.process_command(
        "confirmation threat score"
    )

    assert "Risk Score: 100/100" in result
    assert "Risk Classification: critical" in result
    assert "Integrity Valid: False" in result
    assert "Human Review Required: True" in result


def test_confirmation_threat_score_is_read_only(monkeypatch):
    import core.brain as brain

    calls = {"analysis": 0}

    def fake_analysis():
        calls["analysis"] += 1

        return {
            "risk_score": 10,
            "risk_classification": "low",
            "integrity_valid": True,
            "event_count": 2,
            "human_review_required": False,
        }

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_analysis",
        fake_analysis,
    )

    result = brain.process_command(
        "confirmation threat score"
    )

    assert calls["analysis"] == 1
    assert "read-only" in result
    assert "Automatic execution is disabled." in result


def test_confirmation_threat_trend_command(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_trend_report",
        lambda: "TEST V32 TREND REPORT",
    )

    result = brain.process_command(
        "confirmation threat trend"
    )

    assert result == "TEST V32 TREND REPORT"


def test_confirmation_threat_trend_report_aliases(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_trend_report",
        lambda: "TEST V32 TREND REPORT",
    )

    commands = [
        "confirmation threat trend",
        "confirmation threat trend intelligence",
        "confirmation threat trend report",
        "confirmation risk trend",
        "confirmation risk trend report",
    ]

    for command in commands:
        result = brain.process_command(command)

        assert result == "TEST V32 TREND REPORT"


def test_confirmation_threat_trend_score_command(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_trend_intelligence",
        lambda: {
            "trend_score": 48,
            "trend_classification": "worsening",
            "integrity_valid": True,
            "sufficient_history": True,
            "history_truncated": False,
            "retained_event_count": 42,
            "retention_limit": 100,
            "failure_delta": 4,
            "lockout_delta": 1,
            "expiry_delta": 2,
            "success_delta": -3,
            "human_review_required": True,
            "automation_allowed": False,
            "read_only": True,
        },
    )

    result = brain.process_command(
        "confirmation threat trend score"
    )

    assert "JERVIS CONFIRMATION THREAT TREND SCORE" in result
    assert "Trend Score: 48" in result
    assert "Trend Classification: worsening" in result
    assert "Integrity Valid: True" in result
    assert "Sufficient History: True" in result
    assert "History Truncated: False" in result
    assert "Retained Events: 42/100" in result
    assert "Failure Delta: 4" in result
    assert "Lockout Delta: 1" in result
    assert "Expiry Delta: 2" in result
    assert "Success Delta: -3" in result
    assert "Human Review Required: True" in result
    assert "read-only" in result
    assert "Automatic execution is disabled." in result


def test_confirmation_risk_trend_score_alias(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_trend_intelligence",
        lambda: {
            "trend_score": 20,
            "trend_classification": "worsening",
            "integrity_valid": True,
            "sufficient_history": True,
            "history_truncated": False,
            "retained_event_count": 20,
            "retention_limit": 100,
            "failure_delta": 2,
            "lockout_delta": 0,
            "expiry_delta": 1,
            "success_delta": -1,
            "human_review_required": False,
        },
    )

    result = brain.process_command(
        "confirmation risk trend score"
    )

    assert "Trend Score: 20" in result
    assert "Trend Classification: worsening" in result
    assert "Human Review Required: False" in result


def test_confirmation_threat_trend_insufficient_history(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_trend_intelligence",
        lambda: {
            "trend_score": 0,
            "trend_classification": "insufficient_data",
            "integrity_valid": True,
            "sufficient_history": False,
            "history_truncated": False,
            "retained_event_count": 0,
            "retention_limit": 100,
            "failure_delta": 0,
            "lockout_delta": 0,
            "expiry_delta": 0,
            "success_delta": 0,
            "human_review_required": False,
        },
    )

    result = brain.process_command(
        "confirmation threat trend score"
    )

    assert "Trend Score: 0" in result
    assert "Trend Classification: insufficient_data" in result
    assert "Sufficient History: False" in result
    assert "Retained Events: 0/100" in result
    assert "Human Review Required: False" in result


def test_confirmation_threat_trend_integrity_failure(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_trend_intelligence",
        lambda: {
            "trend_score": 100,
            "trend_classification": "critical",
            "integrity_valid": False,
            "sufficient_history": True,
            "history_truncated": False,
            "retained_event_count": 75,
            "retention_limit": 100,
            "failure_delta": 8,
            "lockout_delta": 3,
            "expiry_delta": 4,
            "success_delta": -5,
            "human_review_required": True,
        },
    )

    result = brain.process_command(
        "confirmation threat trend score"
    )

    assert "Trend Score: 100" in result
    assert "Trend Classification: critical" in result
    assert "Integrity Valid: False" in result
    assert "Human Review Required: True" in result


def test_confirmation_threat_trend_score_is_read_only(monkeypatch):
    import core.brain as brain

    calls = {"trend": 0}

    def fake_trend():
        calls["trend"] += 1

        return {
            "trend_score": 10,
            "trend_classification": "stable",
            "integrity_valid": True,
            "sufficient_history": True,
            "history_truncated": False,
            "retained_event_count": 15,
            "retention_limit": 100,
            "failure_delta": 0,
            "lockout_delta": 0,
            "expiry_delta": 0,
            "success_delta": 1,
            "human_review_required": False,
            "automation_allowed": False,
            "read_only": True,
        }

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_trend_intelligence",
        fake_trend,
    )

    result = brain.process_command(
        "confirmation threat trend score"
    )

    assert calls["trend"] == 1
    assert "read-only" in result
    assert "Automatic execution is disabled." in result


def test_confirmation_threat_forecast_command(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_forecast_report",
        lambda: "TEST V34 FORECAST REPORT",
    )

    result = brain.process_command(
        "confirmation threat forecast"
    )

    assert result == "TEST V34 FORECAST REPORT"


def test_confirmation_threat_forecast_aliases(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_forecast_report",
        lambda: "TEST V34 FORECAST REPORT",
    )

    commands = [
        "confirmation threat forecast",
        "confirmation threat forecast report",
        "confirmation forecast",
        "confirmation forecast report",
        "confirmation risk forecast",
    ]

    for command in commands:
        assert (
            brain.process_command(command)
            == "TEST V34 FORECAST REPORT"
        )


def test_confirmation_threat_forecast_score(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_forecast_intelligence",
        lambda: {
            "forecast_score": 55,
            "forecast_classification": "rapidly_worsening",
            "current_trend_score": 40,
            "current_trend_classification": "worsening",
            "projected_direction": "worsening",
            "forecast_confidence": 70.0,
            "risk_acceleration": 30,
            "human_review_required": True,
            "automation_allowed": False,
            "read_only": True,
        },
    )

    result = brain.process_command(
        "confirmation threat forecast score"
    )

    assert "JERVIS CONFIRMATION THREAT FORECAST SCORE" in result
    assert "Forecast Score: 55" in result
    assert "Forecast Classification: rapidly_worsening" in result
    assert "Current Trend Score: 40" in result
    assert "Current Trend Classification: worsening" in result
    assert "Projected Direction: worsening" in result
    assert "Forecast Confidence: 70.0%" in result
    assert "Risk Acceleration: 30" in result
    assert "Human Review Required: True" in result
    assert "read-only" in result
    assert "Automatic security execution is disabled." in result


def test_confirmation_forecast_score_aliases(monkeypatch):
    import core.brain as brain

    calls = {"forecast": 0}

    def fake_forecast():
        calls["forecast"] += 1

        return {
            "forecast_score": 10,
            "forecast_classification": "stable",
            "current_trend_score": 5,
            "current_trend_classification": "stable",
            "projected_direction": "stable",
            "forecast_confidence": 70.0,
            "risk_acceleration": 10,
            "human_review_required": False,
            "automation_allowed": False,
            "read_only": True,
        }

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_forecast_intelligence",
        fake_forecast,
    )

    commands = [
        "confirmation threat forecast score",
        "confirmation forecast score",
        "confirmation risk forecast score",
    ]

    for command in commands:
        result = brain.process_command(command)

        assert "Forecast Score: 10" in result
        assert "Forecast Classification: stable" in result
        assert "Projected Direction: stable" in result
        assert "Human Review Required: False" in result

    assert calls["forecast"] == len(commands)


def test_confirmation_forecast_insufficient_data(monkeypatch):
    import core.brain as brain

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_forecast_intelligence",
        lambda: {
            "forecast_score": 0,
            "forecast_classification": "insufficient_data",
            "current_trend_score": 0,
            "current_trend_classification": "insufficient_data",
            "projected_direction": "unknown",
            "forecast_confidence": 0.0,
            "risk_acceleration": 0,
            "human_review_required": False,
            "automation_allowed": False,
            "read_only": True,
        },
    )

    result = brain.process_command(
        "confirmation forecast score"
    )

    assert "Forecast Score: 0" in result
    assert "Forecast Classification: insufficient_data" in result
    assert "Projected Direction: unknown" in result
    assert "Forecast Confidence: 0.0%" in result


def test_confirmation_forecast_brain_route_is_read_only(monkeypatch):
    import core.brain as brain

    calls = {"forecast": 0}

    def fake_forecast():
        calls["forecast"] += 1

        return {
            "forecast_score": 100,
            "forecast_classification": "rapidly_worsening",
            "current_trend_score": 90,
            "current_trend_classification": "rapidly_worsening",
            "projected_direction": "worsening",
            "forecast_confidence": 70.0,
            "risk_acceleration": 100,
            "human_review_required": True,
            "automation_allowed": False,
            "read_only": True,
        }

    monkeypatch.setattr(
        brain,
        "get_confirmation_threat_forecast_intelligence",
        fake_forecast,
    )

    result = brain.process_command(
        "confirmation threat forecast score"
    )

    assert calls["forecast"] == 1
    assert "Human Review Required: True" in result
    assert "read-only" in result
    assert "Automatic security execution is disabled." in result
