from core.intent import detect_intent

try:
    from core.ai_brain import ask_ai

    AI_BRAIN_AVAILABLE = callable(
        ask_ai
    )
except Exception:
    AI_BRAIN_AVAILABLE = False


KNOWN_INTENTS = {
    "greeting",
    "time",
    "date",
    "system_health",
    "system_info",
    "open_youtube",
    "open_google",
    "open_calculator",
    "open_notepad",
    "volume_up",
    "volume_down",
    "battery_status",
    "wifi_status",
    "search_youtube",
    "search_google",
}


def _normalize_intent_result(
    result,
):
    """
    intent.py returns:
        (intent, parameter)

    The second value is NOT a confidence score.
    """
    if isinstance(
        result,
        (tuple, list),
    ):
        if not result:
            return (
                "unknown",
                None,
            )

        intent = (
            str(
                result[0]
            ).strip().lower()
            if result[0]
            else "unknown"
        )

        parameter = (
            result[1]
            if len(result) > 1
            else None
        )

        return (
            intent,
            parameter,
        )

    if isinstance(
        result,
        dict,
    ):
        intent = str(
            result.get("intent")
            or result.get("name")
            or result.get("type")
            or "unknown"
        ).strip().lower()

        parameter = (
            result.get("parameter")
            or result.get("query")
            or result.get("value")
        )

        return (
            intent,
            parameter,
        )

    if result is None:
        return (
            "unknown",
            None,
        )

    return (
        str(result).strip().lower(),
        None,
    )


def _estimate_confidence(
    command,
    intent,
    parameter=None,
):
    command = str(
        command
    ).strip()

    if not command:
        return 0.0

    if intent in (
        "",
        "unknown",
        "none",
    ):
        return 25.0

    if intent in KNOWN_INTENTS:
        if parameter:
            return 92.0

        return 90.0

    return 70.0


def analyze_intent(
    command,
):
    command = str(
        command
    ).strip()

    if not command:
        return {
            "command": "",
            "intent": "unknown",
            "parameter": None,
            "confidence": 0.0,
            "understanding": "No Command",
            "routing_status": "Not Ready",
            "ai_fallback_ready": (
                AI_BRAIN_AVAILABLE
            ),
            "recommendations": [
                (
                    "Enter or speak a "
                    "command for JERVIS "
                    "to analyze."
                )
            ],
        }

    try:
        raw_result = (
            detect_intent(
                command
            )
        )

    except Exception as error:
        return {
            "command": command,
            "intent": "unknown",
            "parameter": None,
            "confidence": 0.0,
            "understanding": (
                "Intent Error"
            ),
            "routing_status": (
                "Needs Review"
            ),
            "ai_fallback_ready": (
                AI_BRAIN_AVAILABLE
            ),
            "recommendations": [
                (
                    "Intent detection "
                    f"failed: {error}"
                ),
                (
                    "Use AI fallback "
                    "or review the "
                    "intent rules."
                ),
            ],
        }

    intent, parameter = (
        _normalize_intent_result(
            raw_result
        )
    )

    confidence = (
        _estimate_confidence(
            command,
            intent,
            parameter,
        )
    )

    if confidence >= 85:
        understanding = "Strong"
        routing_status = "Ready"

    elif confidence >= 70:
        understanding = "Good"
        routing_status = "Ready"

    elif confidence >= 40:
        understanding = (
            "Uncertain"
        )
        routing_status = (
            "Review Recommended"
        )

    else:
        understanding = (
            "Low Confidence"
        )
        routing_status = (
            "AI Fallback Recommended"
        )

    recommendations = []

    if intent in (
        "",
        "unknown",
        "none",
    ):
        recommendations.append(
            (
                "No strong built-in "
                "intent was detected."
            )
        )

        if AI_BRAIN_AVAILABLE:
            recommendations.append(
                (
                    "AI fallback is "
                    "available for "
                    "open-ended requests."
                )
            )

        else:
            recommendations.append(
                (
                    "AI fallback is "
                    "currently unavailable."
                )
            )

    elif confidence < 70:
        recommendations.append(
            (
                "Try a more specific "
                "command with clear "
                "action words."
            )
        )

    else:
        recommendations.append(
            (
                "Intent understanding "
                "looks ready for normal "
                "routing."
            )
        )

    return {
        "command": command,
        "intent": intent,
        "parameter": parameter,
        "confidence": confidence,
        "understanding": (
            understanding
        ),
        "routing_status": (
            routing_status
        ),
        "ai_fallback_ready": (
            AI_BRAIN_AVAILABLE
        ),
        "recommendations": (
            recommendations
        ),
    }


def get_intent_system_status():
    test_commands = [
        "hello",
        "what time is it",
        "open youtube",
        "system health",
    ]

    results = [
        analyze_intent(
            command
        )
        for command in test_commands
    ]

    ready_count = sum(
        1
        for result in results
        if result[
            "routing_status"
        ] == "Ready"
    )

    score = round(
        (
            ready_count
            / len(
                test_commands
            )
        )
        * 100
    )

    if (
        AI_BRAIN_AVAILABLE
        and score < 100
    ):
        score = min(
            100,
            score + 5,
        )

    if score >= 85:
        status = "Excellent"

    elif score >= 70:
        status = "Good"

    elif score >= 50:
        status = (
            "Needs Attention"
        )

    else:
        status = "Critical"

    return {
        "score": score,
        "status": status,
        "tests": results,
        "ai_fallback_ready": (
            AI_BRAIN_AVAILABLE
        ),
    }


def get_intent_intelligence_report(
    command="system health",
):
    analysis = analyze_intent(
        command
    )

    system_status = (
        get_intent_system_status()
    )

    lines = [
        (
            "JERVIS SMART INTENT "
            "& AI INTELLIGENCE"
        ),
        "",
        (
            f"Intent Intelligence Score: "
            f"{system_status['score']}/100"
        ),
        (
            f"System Status: "
            f"{system_status['status']}"
        ),
        (
            f"AI Fallback Ready: "
            f"{'Yes' if system_status['ai_fallback_ready'] else 'No'}"
        ),
        "",
        "COMMAND ANALYSIS",
        "",
        (
            f"Command: "
            f"{analysis['command']}"
        ),
        (
            f"Detected Intent: "
            f"{analysis['intent']}"
        ),
    ]

    parameter = analysis.get(
        "parameter"
    )

    if parameter:
        lines.append(
            (
                f"Intent Parameter: "
                f"{parameter}"
            )
        )

    lines.extend(
        [
            (
                f"Routing Confidence: "
                f"{analysis['confidence']}%"
            ),
            (
                f"Understanding: "
                f"{analysis['understanding']}"
            ),
            (
                f"Routing Status: "
                f"{analysis['routing_status']}"
            ),
            "",
            "RECOMMENDATIONS",
        ]
    )

    for item in analysis[
        "recommendations"
    ]:
        lines.append(
            f"- {item}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: Intent intelligence "
                "analyzes command understanding "
                "only. It does not execute the "
                "analyzed command."
            ),
        ]
    )

    return "\n".join(
        lines
    )


if __name__ == "__main__":
    print(
        get_intent_intelligence_report(
            "system health"
        )
    )