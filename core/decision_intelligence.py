import math

from core.system_health import get_system_health
from core.alert_intelligence import get_alert_intelligence
from core.productivity_intelligence import get_productivity_intelligence
from core.memory_intelligence import get_memory_intelligence
from core.personal_assistant_intelligence import get_personal_assistant_intelligence
from core.context_intelligence import get_context_system_status
from core.startup_bootstrap import get_security_decision
from core.confirmation_threat_decision_intelligence import (
    get_confirmation_threat_decision,
)
from core.confirmation_threat_trend_decision_intelligence import (
    get_confirmation_threat_trend_decision,
)
from core.confirmation_threat_forecast_decision_intelligence import (
    get_confirmation_threat_forecast_decision,
)
from core.confirmation_threat_forecast_calibration_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_decision,
)
from core.confirmation_threat_forecast_calibration_trend_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_decision,
)
from core.confirmation_threat_forecast_calibration_trend_forecast_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_decision,
)
from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision,
)
from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence,
)
from core.confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence import (
    get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence,
)


PRIORITY_WEIGHT = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


def _safe_result(function):
    try:
        result = function()
    except Exception:
        result = {}

    return result if isinstance(result, dict) else {}


def _number(data, *keys, default=0):
    for key in keys:
        value = data.get(key)

        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass

    return float(default)


def _safe_confidence(value):
    # Global decision confidence is a bounded 0-100 ranking value.
    #
    # Preserve valid existing values exactly after float conversion.
    # In particular, do not reinterpret 0-1 values as percentages.
    #
    # Malformed, boolean, non-finite, or out-of-range confidence must
    # fail closed so it cannot gain ranking influence.
    if isinstance(value, bool):
        return 0.0

    try:
        confidence = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0

    if not math.isfinite(confidence):
        return 0.0

    if confidence < 0.0 or confidence > 100.0:
        return 0.0

    return confidence


def _safe_priority(value):
    """Return a canonical fail-closed decision priority."""
    try:
        if value in PRIORITY_WEIGHT:
            return value
    except (TypeError, ValueError):
        pass

    return "Low"


def _safe_text(value):
    if isinstance(value, str):
        return value
    return ""


def _add_decision(
    decisions,
    title,
    priority,
    reason,
    impact,
    confidence,
    action,
    source,
):
    decisions.append(
        {
            "title": _safe_text(title),
            "priority": _safe_priority(priority),
            "reason": _safe_text(reason),
            "impact": _safe_text(impact),
            "confidence": _safe_confidence(confidence),
            "action": _safe_text(action),
            "source": _safe_text(source),
        }
    )


def _collect_decisions():
    system = _safe_result(get_system_health)
    alerts = _safe_result(get_alert_intelligence)
    productivity = _safe_result(get_productivity_intelligence)
    memory = _safe_result(get_memory_intelligence)
    assistant = _safe_result(get_personal_assistant_intelligence)
    context = _safe_result(get_context_system_status)
    security = _safe_result(get_security_decision)
    threat_decision = _safe_result(
        get_confirmation_threat_decision
    )
    trend_threat_decision = _safe_result(
        get_confirmation_threat_trend_decision
    )

    forecast_threat_decision = _safe_result(
        get_confirmation_threat_forecast_decision
    )

    calibration_threat_decision = _safe_result(
        get_confirmation_threat_forecast_calibration_decision
    )
    calibration_trend_threat_decision = _safe_result(
        get_confirmation_threat_forecast_calibration_trend_decision
    )
    calibration_trend_forecast_threat_decision = _safe_result(
        get_confirmation_threat_forecast_calibration_trend_forecast_decision
    )
    calibration_trend_forecast_calibration_threat_decision = _safe_result(
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_decision
    )
    calibration_trend_forecast_calibration_trend_threat_decision = _safe_result(
        get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_decision_intelligence
    )

    decisions = []

    system_score = _number(
        system,
        "score",
        "health_score",
        default=100,
    )

    cpu = _number(
        system,
        "cpu_usage",
        "cpu_percent",
        "cpu",
        default=0,
    )

    ram_data = system.get("ram", {})
    if isinstance(ram_data, dict):
        ram = _number(ram_data, "percent", default=0)
    else:
        ram = _number(
            system, "ram_usage", "ram_percent", "memory_percent", default=0
        )

    disk_data = system.get("disk", {})
    if isinstance(disk_data, dict):
        disk = _number(disk_data, "percent", default=0)
    else:
        disk = _number(
            system, "disk_usage", "disk_percent", default=0
        )

    critical_alerts = int(
        _number(
            alerts,
            "critical_alerts",
            "critical_count",
            default=0,
        )
    )

    active_alerts = int(
        _number(
            alerts,
            "active_alerts",
            "total_alerts",
            default=0,
        )
    )

    pending_tasks = int(
        _number(
            productivity,
            "pending_tasks",
            default=0,
        )
    )

    completion_rate = _number(
        productivity,
        "completion_rate",
        default=100,
    )

    active_reminders = int(
        _number(
            productivity,
            "active_reminders",
            default=0,
        )
    )

    memory_score = _number(
        memory,
        "score",
        default=100,
    )

    recall_ready = bool(
        memory.get(
            "recall_ready",
            True,
        )
    )

    assistant_score = _number(
        assistant,
        "score",
        default=100,
    )

    context_score = _number(
        context,
        "score",
        default=100,
    )

    context_ready = bool(
        context.get(
            "context_ready",
            False,
        )
    )

    # Critical alerts should dominate the decision list.
    if critical_alerts > 0:
        _add_decision(
            decisions,
            "Resolve critical JERVIS alerts",
            "Critical",
            (
                f"{critical_alerts} critical alert(s) "
                "are currently detected."
            ),
            "System stability and reliability",
            98,
            (
                "Open Alert Intelligence and resolve "
                "critical alerts before lower-priority work."
            ),
            "Alert Intelligence",
        )

    # Disk pressure.
    if disk >= 95:
        _add_decision(
            decisions,
            "Free disk space",
            "Critical",
            f"Disk usage is critically high at {disk:.1f}%.",
            "Storage availability and system stability",
            97,
            (
                "Review large files and safe cleanup "
                "recommendations, then free disk space."
            ),
            "System Health",
        )
    elif disk >= 85:
        _add_decision(
            decisions,
            "Reduce disk usage",
            "High",
            f"Disk usage is high at {disk:.1f}%.",
            "Storage performance and future capacity",
            94,
            "Move or remove unnecessary large files.",
            "System Health",
        )

    # RAM pressure.
    if ram >= 90:
        _add_decision(
            decisions,
            "Reduce RAM pressure",
            "Critical",
            f"RAM usage is critically high at {ram:.1f}%.",
            "System responsiveness",
            96,
            "Close unused applications and browser tabs.",
            "System Health",
        )
    elif ram >= 80:
        _add_decision(
            decisions,
            "Reduce RAM usage",
            "High",
            f"RAM usage is high at {ram:.1f}%.",
            "System responsiveness",
            92,
            "Close unused applications and browser tabs.",
            "System Health",
        )

    # CPU pressure.
    if cpu >= 90:
        _add_decision(
            decisions,
            "Reduce CPU load",
            "Critical",
            f"CPU usage is critically high at {cpu:.1f}%.",
            "System responsiveness and performance",
            95,
            "Review high-CPU processes and close unnecessary workloads.",
            "System Health",
        )
    elif cpu >= 80:
        _add_decision(
            decisions,
            "Review high CPU usage",
            "High",
            f"CPU usage is high at {cpu:.1f}%.",
            "System performance",
            90,
            "Check running processes for unnecessary CPU-heavy activity.",
            "System Health",
        )

    # Generic system-health fallback.
    if (
        system_score < 70
        and disk < 85
        and ram < 80
        and cpu < 80
    ):
        _add_decision(
            decisions,
            "Review system health warnings",
            "High" if system_score < 50 else "Medium",
            (
                f"System Health score is "
                f"{int(system_score)}/100."
            ),
            "Overall PC reliability",
            88,
            "Open System Health and review detected problems.",
            "System Health",
        )

    # Productivity decisions.
    if pending_tasks >= 10:
        _add_decision(
            decisions,
            "Reduce task backlog",
            "High",
            f"{pending_tasks} pending tasks are active.",
            "Focus and productivity",
            91,
            "Select the three highest-priority tasks and complete them first.",
            "Productivity Intelligence",
        )
    elif pending_tasks > 0:
        _add_decision(
            decisions,
            "Complete the highest-priority pending task",
            "Medium",
            f"{pending_tasks} pending task(s) remain.",
            "Daily productivity",
            86,
            "Review pending tasks and complete the most important one next.",
            "Productivity Intelligence",
        )

    if completion_rate < 25 and pending_tasks > 0:
        _add_decision(
            decisions,
            "Improve task completion rate",
            "Medium",
            (
                f"Task completion rate is only "
                f"{completion_rate:.1f}%."
            ),
            "Productivity consistency",
            84,
            "Reduce task overload and focus on fewer active priorities.",
            "Productivity Intelligence",
        )

    if active_reminders >= 5:
        _add_decision(
            decisions,
            "Review active reminders",
            "Medium",
            f"{active_reminders} active reminders are stored.",
            "Schedule awareness",
            82,
            "Review reminders and clear or complete outdated items.",
            "Productivity Intelligence",
        )

    # Memory/context decisions.
    if memory_score < 70 or not recall_ready:
        _add_decision(
            decisions,
            "Review JERVIS memory health",
            "Medium",
            (
                f"Memory Health score is "
                f"{int(memory_score)}/100."
            ),
            "Personalized recall reliability",
            83,
            "Open Memory Intelligence and review recall readiness.",
            "Memory Intelligence",
        )

    if context_score < 70 or not context_ready:
        _add_decision(
            decisions,
            "Improve conversation context readiness",
            "Low",
            (
                f"Context Intelligence score is "
                f"{int(context_score)}/100."
            ),
            "Follow-up understanding",
            78,
            "Use clear topic commands and build more meaningful conversation history.",
            "Context Intelligence",
        )

    if assistant_score < 70:
        _add_decision(
            decisions,
            "Review Personal Assistant Intelligence",
            "Medium",
            (
                f"Assistant Intelligence score is "
                f"{int(assistant_score)}/100."
            ),
            "Overall JERVIS decision readiness",
            85,
            "Review assistant priorities and recommended next actions.",
            "Personal Assistant Intelligence",
        )

    # Active alerts without critical alerts.
    if active_alerts > 0 and critical_alerts == 0:
        _add_decision(
            decisions,
            "Review active alerts",
            "Medium",
            f"{active_alerts} active alert(s) are available.",
            "Preventive system maintenance",
            87,
            "Open Alert Intelligence and review active warnings.",
            "Alert Intelligence",
        )

    # V31: Confirmation threat decision intelligence.
    #
    # This is advisory only. It may enter global ranking, but it
    # must never become an automatic execution path.
    threat_priority = threat_decision.get("priority")

    if threat_priority in {"Critical", "High", "Medium"}:
        _add_decision(
            decisions,
            threat_decision.get(
                "title",
                "Review confirmation threat activity",
            ),
            threat_priority,
            threat_decision.get(
                "reason",
                "Confirmation threat analysis requires review.",
            ),
            threat_decision.get(
                "impact",
                "Confirmation security and audit trust",
            ),
            threat_decision.get(
                "confidence",
                95.0,
            ),
            threat_decision.get(
                "action",
                "Review Confirmation Threat Analysis manually.",
            ),
            threat_decision.get(
                "source",
                "Confirmation Threat Decision Intelligence",
            ),
        )
    # V33: Confirmation threat trend decision intelligence.
    #
    # V34: Confirmation threat forecast decision intelligence.
    #
    # Low priority remains advisory-only and is intentionally
    # excluded from the global ranked decision list.
    forecast_threat_priority = forecast_threat_decision.get(
        "priority"
    )

    if forecast_threat_priority in {
        "Critical",
        "High",
        "Medium",
    }:
        _add_decision(
            decisions,
            forecast_threat_decision.get(
            "title",
            "Review confirmation threat forecast",
            ),
            forecast_threat_priority,
            forecast_threat_decision.get(
            "reason",
            "Confirmation threat forecast requires review.",
            ),
            forecast_threat_decision.get(
            "impact",
            "Confirmation security forecast",
            ),
            forecast_threat_decision.get(
            "confidence",
            0.0,
            ),
            forecast_threat_decision.get(
            "action",
            "Review confirmation threat forecast.",
            ),
            forecast_threat_decision.get(
            "source",
            "Confirmation Threat Forecast Decision Intelligence",
            ),
        )
    # This is advisory only. Low-priority monitoring decisions
    # remain outside the global ranking, matching the V31 policy.
    # This must never become an automatic execution path.
    # V35: Confirmation threat forecast calibration decision intelligence.
    #
    # Low-priority calibration monitoring remains advisory-only and is
    # intentionally excluded from the global ranked decision list.
    # This must never become an automatic execution path.
    calibration_threat_priority = calibration_threat_decision.get(
        "priority"
    )

    if calibration_threat_priority in {
        "Critical",
        "High",
        "Medium",
    }:
        _add_decision(
            decisions,
            calibration_threat_decision.get(
            "title",
            "Review confirmation threat forecast calibration",
            ),
            calibration_threat_priority,
            calibration_threat_decision.get(
            "reason",
            "Confirmation threat forecast calibration requires review.",
            ),
            calibration_threat_decision.get(
            "impact",
            "Confirmation threat forecast calibration",
            ),
            calibration_threat_decision.get(
            "confidence",
            0.0,
            ),
            calibration_threat_decision.get(
            "action",
            "Review confirmation threat forecast calibration manually.",
            ),
            calibration_threat_decision.get(
            "source",
            "Confirmation Threat Forecast Calibration Decision Intelligence",
            ),
        )

    # V36: Confirmation threat forecast calibration trend decision intelligence.
    #
    # Low-priority calibration-trend monitoring remains advisory-only and is
    # intentionally excluded from the global ranked decision list.
    # This must never become an automatic execution path.
    calibration_trend_threat_priority = (
        calibration_trend_threat_decision.get("priority")
    )

    if calibration_trend_threat_priority in {
        "Critical",
        "High",
        "Medium",
    }:
        _add_decision(
            decisions,
            calibration_trend_threat_decision.get(
            "title",
            "Review confirmation threat forecast calibration trend",
            ),
            calibration_trend_threat_priority,
            calibration_trend_threat_decision.get(
            "reason",
            (
            "Confirmation threat forecast calibration trend "
            "requires review."
            ),
            ),
            calibration_trend_threat_decision.get(
            "impact",
            "Confirmation threat forecast calibration trend",
            ),
            calibration_trend_threat_decision.get(
            "confidence",
            0.0,
            ),
            calibration_trend_threat_decision.get(
            "action",
            (
            "Review confirmation threat forecast calibration "
            "trend manually."
            ),
            ),
            calibration_trend_threat_decision.get(
            "source",
            (
            "Confirmation Threat Forecast Calibration Trend "
            "Decision Intelligence"
            ),
            ),
        )

    # V37: Confirmation threat forecast calibration trend forecast
    # decision intelligence.
    #
    # Low-priority calibration-trend forecast monitoring remains
    # advisory-only and is intentionally excluded from the global ranked
    # decision list. This must never become an automatic execution path.
    calibration_trend_forecast_threat_priority = (
        calibration_trend_forecast_threat_decision.get("priority")
    )

    if calibration_trend_forecast_threat_priority in {
        "Critical",
        "High",
        "Medium",
    }:
        _add_decision(
            decisions,
            calibration_trend_forecast_threat_decision.get(
            "title",
            (
            "Review confirmation threat forecast calibration "
            "trend forecast"
            ),
            ),
            calibration_trend_forecast_threat_priority,
            calibration_trend_forecast_threat_decision.get(
            "reason",
            (
            "Confirmation threat forecast calibration trend "
            "forecast requires review."
            ),
            ),
            calibration_trend_forecast_threat_decision.get(
            "impact",
            (
            "Confirmation threat forecast calibration trend "
            "forecast"
            ),
            ),
            calibration_trend_forecast_threat_decision.get(
            "confidence",
            0.0,
            ),
            calibration_trend_forecast_threat_decision.get(
            "action",
            (
            "Review confirmation threat forecast calibration "
            "trend forecast manually."
            ),
            ),
            calibration_trend_forecast_threat_decision.get(
            "source",
            (
            "Confirmation Threat Forecast Calibration Trend "
            "Forecast Decision Intelligence"
            ),
            ),
        )

    # V38: Confirmation threat forecast calibration trend forecast
    # calibration decision intelligence.
    #
    # Low-priority calibration monitoring remains advisory-only and is
    # intentionally excluded from the global ranked decision list.
    # This must never become an automatic execution path.
    calibration_trend_forecast_calibration_threat_priority = (
        calibration_trend_forecast_calibration_threat_decision.get("priority")
    )

    if calibration_trend_forecast_calibration_threat_priority in {
        "Critical",
        "High",
        "Medium",
    }:
        _add_decision(
            decisions,
            calibration_trend_forecast_calibration_threat_decision.get(
            "title",
            (
            "Review confirmation threat forecast calibration "
            "trend forecast calibration"
            ),
            ),
            calibration_trend_forecast_calibration_threat_priority,
            calibration_trend_forecast_calibration_threat_decision.get(
            "reason",
            (
            "Confirmation threat forecast calibration trend "
            "forecast calibration requires review."
            ),
            ),
            calibration_trend_forecast_calibration_threat_decision.get(
            "impact",
            (
            "Confirmation threat forecast calibration trend "
            "forecast calibration"
            ),
            ),
            calibration_trend_forecast_calibration_threat_decision.get(
            "confidence",
            0.0,
            ),
            calibration_trend_forecast_calibration_threat_decision.get(
            "action",
            (
            "Review confirmation threat forecast calibration "
            "trend forecast calibration manually."
            ),
            ),
            calibration_trend_forecast_calibration_threat_decision.get(
            "source",
            (
            "Confirmation Threat Forecast Calibration Trend "
            "Forecast Calibration Decision Intelligence"
            ),
            ),
        )

    # V39: Confirmation threat forecast calibration trend forecast
    # calibration trend decision intelligence.
    #
    # Low-priority calibration-trend monitoring remains advisory-only and is
    # intentionally excluded from the global ranked decision list.
    # This must never become an automatic execution path.
    calibration_trend_forecast_calibration_trend_threat_priority = (
        calibration_trend_forecast_calibration_trend_threat_decision.get("priority")
    )

    if calibration_trend_forecast_calibration_trend_threat_priority in {
        "Critical",
        "High",
        "Medium",
    }:
        _add_decision(
            decisions,
            calibration_trend_forecast_calibration_trend_threat_decision.get(
            "title",
            (
            "Review confirmation threat forecast calibration "
            "trend forecast calibration trend"
            ),
            ),
            calibration_trend_forecast_calibration_trend_threat_priority,
            calibration_trend_forecast_calibration_trend_threat_decision.get(
            "reason",
            (
            "Confirmation threat forecast calibration trend "
            "forecast calibration trend requires review."
            ),
            ),
            calibration_trend_forecast_calibration_trend_threat_decision.get(
            "impact",
            (
            "Confirmation threat forecast calibration trend "
            "forecast calibration trend"
            ),
            ),
            calibration_trend_forecast_calibration_trend_threat_decision.get(
            "confidence",
            0.0,
            ),
            calibration_trend_forecast_calibration_trend_threat_decision.get(
            "action",
            calibration_trend_forecast_calibration_trend_threat_decision.get(
            "recommended_action",
            (
            "Review confirmation threat forecast calibration "
            "trend forecast calibration trend manually."
            ),
            ),
            ),
            calibration_trend_forecast_calibration_trend_threat_decision.get(
            "source",
            (
            "Confirmation Threat Forecast Calibration Trend "
            "Forecast Calibration Trend Decision Intelligence"
            ),
            ),
        )
    trend_threat_priority = trend_threat_decision.get("priority")

    if trend_threat_priority in {"Critical", "High", "Medium"}:
        _add_decision(
            decisions,
            trend_threat_decision.get(
                "title",
                "Review confirmation threat trend",
            ),
            trend_threat_priority,
            trend_threat_decision.get(
                "reason",
                "Confirmation threat trend requires review.",
            ),
            trend_threat_decision.get(
                "impact",
                "Confirmation security trend",
            ),
            trend_threat_decision.get(
                "confidence",
                95.0,
            ),
            trend_threat_decision.get(
                "action",
                "Review confirmation threat trend manually.",
            ),
            trend_threat_decision.get(
                "source",
                "Confirmation Threat Trend Decision Intelligence",
            ),
        )

    # V44: Confirmation threat forecast calibration trend forecast
    # calibration trend confidence reliability decision intelligence.
    #
    # Advisory only. It may enter global ranking, but must never
    # become an automatic execution path.
    reliability_threat_decision = get_confirmation_threat_forecast_calibration_trend_forecast_calibration_trend_confidence_reliability_decision_intelligence()

    reliability_threat_priority = (
        reliability_threat_decision.get("priority")
    )

    if reliability_threat_priority in {
        "Critical",
        "High",
        "Medium",
    }:
        _add_decision(
            decisions,
            reliability_threat_decision.get(
            "title",
            (
            "Review confirmation threat forecast calibration "
            "trend forecast calibration trend confidence "
            "reliability"
            ),
            ),
            reliability_threat_priority,
            reliability_threat_decision.get(
            "reason",
            (
            "Confirmation threat confidence reliability "
            "requires review."
            ),
            ),
            reliability_threat_decision.get(
            "impact",
            (
            "Confirmation threat confidence reliability "
            "assessment"
            ),
            ),
            float(
            reliability_threat_decision.get(
            "confidence",
            0.0,
            )
            ),
            reliability_threat_decision.get(
            "action",
            reliability_threat_decision.get(
            "recommended_action",
            (
            "Review confirmation threat confidence "
            "reliability manually."
            ),
            ),
            ),
            reliability_threat_decision.get(
            "source",
            (
            "Confirmation Threat Forecast Calibration Trend "
            "Forecast Calibration Trend Confidence "
            "Reliability Decision Intelligence"
            ),
            ),
        )

    # Security bootstrap decisions.
    security_priority = security.get("priority")

    if security_priority in {"Critical", "High"}:
        _add_decision(
            decisions,
            security.get(
                "title",
                "Review security bootstrap health",
            ),
            security_priority,
            security.get(
                "reason",
                "Security bootstrap instability detected.",
            ),
            security.get(
                "impact",
                "Security bootstrap reliability",
            ),
            security.get(
                "confidence",
                90.0,
            ),
            security.get(
                "action",
                "Review Security Health Intelligence.",
            ),
            security.get(
                "source",
                "Security Health Intelligence",
            ),
        )
    if not decisions:
        _add_decision(
            decisions,
            "Continue normal JERVIS operation",
            "Low",
            "No urgent decision condition is currently detected.",
            "Stable daily operation",
            90,
            "Continue normal work and periodically review intelligence dashboards.",
            "Decision Intelligence",
        )

    # Rank by priority first, confidence second.
    decisions.sort(
        key=lambda item: (
            PRIORITY_WEIGHT.get(
                item["priority"],
                0,
            ),
            item["confidence"],
        ),
        reverse=True,
    )

    for rank, item in enumerate(
        decisions,
        start=1,
    ):
        item["rank"] = rank

    return decisions


def get_decision_intelligence():
    decisions = _collect_decisions()

    critical = sum(
        1
        for item in decisions
        if item["priority"] == "Critical"
    )

    high = sum(
        1
        for item in decisions
        if item["priority"] == "High"
    )

    medium = sum(
        1
        for item in decisions
        if item["priority"] == "Medium"
    )

    # Decision readiness measures whether JERVIS has a
    # clear, confident ranked action plan.
    average_confidence = round(
        sum(
            item["confidence"]
            for item in decisions
        )
        / len(decisions),
        1,
    )

    readiness_score = round(
        min(
            100,
            average_confidence
            + min(
                10,
                len(decisions) * 2,
            ),
        )
    )

    if readiness_score >= 90:
        readiness = "Excellent"
    elif readiness_score >= 75:
        readiness = "Ready"
    elif readiness_score >= 60:
        readiness = "Moderate"
    else:
        readiness = "Needs Attention"

    if critical > 0:
        decision_status = "Critical Action Required"
    elif high > 0:
        decision_status = "High Priority Action"
    elif medium > 0:
        decision_status = "Action Recommended"
    else:
        decision_status = "Stable"

    best = decisions[0]

    alternatives = [
        item
        for item in decisions[1:4]
    ]

    recommendations = []

    if critical > 0:
        recommendations.append(
            "Complete critical decisions before medium or low-priority work."
        )

    if high > 0:
        recommendations.append(
            "After critical items, address high-priority decisions in ranked order."
        )

    if len(decisions) > 5:
        recommendations.append(
            "Avoid acting on every recommendation at once; follow the ranked decision list."
        )

    recommendations.append(
        "Re-run Decision Intelligence after completing a major action so priorities can be recalculated."
    )

    return {
        "score": readiness_score,
        "status": decision_status,
        "readiness": readiness,
        "total_decisions": len(decisions),
        "critical_decisions": critical,
        "high_decisions": high,
        "medium_decisions": medium,
        "average_confidence": average_confidence,
        "best_next_action": best,
        "alternative_actions": alternatives,
        "decisions": decisions,
        "recommendations": recommendations,
    }


def get_ranked_decisions(limit=10):
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError(
            "limit must be an integer."
        )

    if limit < 0:
        raise ValueError(
            "limit must be greater than or equal to 0."
        )

    result = get_decision_intelligence()

    if not isinstance(result, dict):
        raise TypeError(
            "decision intelligence result must be a dictionary"
        )

    if "decisions" not in result:
        raise KeyError("decisions")

    decisions = result["decisions"]

    if not isinstance(decisions, list):
        raise TypeError(
            "decisions must be a list"
        )

    for item in decisions:
        if not isinstance(item, dict):
            raise TypeError(
                "decision items must be dictionaries"
            )

    return decisions[:limit]


def get_best_next_action():
    result = get_decision_intelligence()

    if not isinstance(result, dict):
        raise TypeError(
            "decision intelligence result must be a dictionary."
        )

    if "best_next_action" not in result:
        raise KeyError(
            "best_next_action"
        )

    best_next_action = result["best_next_action"]

    if not isinstance(best_next_action, dict):
        raise TypeError(
            "best_next_action must be a dictionary."
        )

    if not best_next_action:
        raise ValueError(
            "best_next_action must not be empty."
        )

    return best_next_action


def get_decision_recommendations():
    result = get_decision_intelligence()

    if not isinstance(result, dict):
        raise TypeError(
            "decision intelligence result "
            "must be a dictionary"
        )

    if "recommendations" not in result:
        raise KeyError("recommendations")

    recommendations = result["recommendations"]

    if not isinstance(recommendations, list):
        raise TypeError(
            "recommendations must be a list"
        )

    if not recommendations:
        raise ValueError(
            "recommendations must not be empty"
        )

    for item in recommendations:
        if not isinstance(item, str):
            raise TypeError(
                "recommendation items "
                "must be strings"
            )

        if not item.strip():
            raise ValueError(
                "recommendation items "
                "must not be blank"
            )

    return recommendations


def get_decision_intelligence_report():
    result = get_decision_intelligence()

    if not isinstance(result, dict):
        raise TypeError(
            "decision intelligence result must be a dictionary."
        )

    if "decisions" not in result:
        raise KeyError("decisions")

    decisions = result["decisions"]

    if not isinstance(decisions, list):
        raise TypeError(
            "decisions must be a list."
        )

    if "best_next_action" not in result:
        raise KeyError("best_next_action")

    best_next_action = result["best_next_action"]

    if not isinstance(best_next_action, dict):
        raise TypeError(
            "best_next_action must be a dictionary."
        )

    if "alternative_actions" not in result:
        raise KeyError("alternative_actions")

    alternative_actions = result["alternative_actions"]

    if not isinstance(alternative_actions, list):
        raise TypeError(
            "alternative_actions must be a list."
        )

    if "recommendations" not in result:
        raise KeyError("recommendations")

    recommendations = result["recommendations"]

    if not isinstance(recommendations, list):
        raise TypeError(
            "recommendations must be a list."
        )

    lines = [
        "JERVIS SMART DECISION INTELLIGENCE",
        "",
        (
            f"Decision Readiness Score: "
            f"{result['score']}/100"
        ),
        (
            f"Decision Status: "
            f"{result['status']}"
        ),
        (
            f"Decision Readiness: "
            f"{result['readiness']}"
        ),
        (
            f"Average Confidence: "
            f"{result['average_confidence']}%"
        ),
        "",
        "DECISION SUMMARY",
        "",
        (
            f"Total Decisions: "
            f"{result['total_decisions']}"
        ),
        (
            f"Critical: "
            f"{result['critical_decisions']}"
        ),
        (
            f"High: "
            f"{result['high_decisions']}"
        ),
        (
            f"Medium: "
            f"{result['medium_decisions']}"
        ),
        "",
        "RANKED DECISIONS",
        "",
    ]

    for item in result["decisions"]:
        lines.extend(
            [
                (
                    f"DECISION #{item['rank']} "
                    f"- {item['title']}"
                ),
                (
                    f"Priority: "
                    f"{item['priority']}"
                ),
                (
                    f"Reason: "
                    f"{item['reason']}"
                ),
                (
                    f"Impact: "
                    f"{item['impact']}"
                ),
                (
                    f"Confidence: "
                    f"{item['confidence']}%"
                ),
                (
                    f"Recommended Action: "
                    f"{item['action']}"
                ),
                (
                    f"Source: "
                    f"{item['source']}"
                ),
                "",
            ]
        )

    best = result[
        "best_next_action"
    ]

    lines.extend(
        [
            "BEST NEXT ACTION",
            "",
            (
                f"{best['title']} "
                f"({best['priority']})"
            ),
            (
                f"- {best['action']}"
            ),
            "",
            "ALTERNATIVE ACTIONS",
        ]
    )

    if result["alternative_actions"]:
        for item in result[
            "alternative_actions"
        ]:
            lines.append(
                (
                    f"- #{item['rank']} "
                    f"{item['title']} "
                    f"({item['priority']})"
                )
            )
    else:
        lines.append(
            "- No alternative action is currently required."
        )

    lines.extend(
        [
            "",
            "DECISION RECOMMENDATIONS",
        ]
    )

    for item in result[
        "recommendations"
    ]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: Decision Intelligence ranks and recommends actions only. "
                "It does not automatically execute system or productivity actions."
            ),
        ]
    )

    return "\n".join(
        lines
    )


if __name__ == "__main__":
    print(
        get_decision_intelligence_report()
    )
