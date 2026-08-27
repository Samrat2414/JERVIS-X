from core.history import _load_history

TOPIC_KEYWORDS = {
    "system health": ["system health", "health score", "cpu", "ram", "disk usage"],
    "productivity": ["productivity", "tasks", "notes", "reminders"],
    "memory": ["memory intelligence", "memory score", "recall"],
    "alerts": ["alert intelligence", "critical alerts", "warning alerts"],
    "backup": ["backup intelligence", "backup health", "backup readiness"],
    "automation": ["automation intelligence", "automation score", "automation capabilities"],
    "usage": ["usage intelligence", "usage score", "usage insights"],
    "intent": ["intent intelligence", "intent score", "analyze intent"],
    "assistant": ["assistant intelligence", "assistant score", "assistant priorities", "what should i do next"],
    "network": ["network intelligence", "network health", "network activity"],
    "battery": ["battery intelligence", "power efficiency", "battery recommendations"],
    "security": ["security center", "security score", "security status"],
    "maintenance": ["maintenance advisor", "maintenance score", "priority actions"],
}

FOLLOW_UP_PATTERNS = [
    "what about it", "what about this", "what are the recommendations",
    "what are recommendations", "show recommendations", "what should i improve",
    "what should i do", "what should i do next", "show details", "give details",
    "more details", "show status", "show score", "what is the score",
    "what is the status", "why", "explain", "tell me more",
]


def _safe_history():
    try:
        history = _load_history()
    except Exception:
        history = []
    return history if isinstance(history, list) else []


def _normalize_text(value):
    return " ".join(str(value or "").strip().lower().split())


def _extract_command(item):
    if not isinstance(item, dict):
        return ""
    for key in ("command", "user", "user_message", "message", "query", "input"):
        value = item.get(key)
        if value:
            return str(value)
    return ""


def _extract_response(item):
    if not isinstance(item, dict):
        return ""
    for key in ("response", "assistant", "reply", "output"):
        value = item.get(key)
        if value:
            return str(value)
    return ""


def detect_topic(text):
    cleaned = _normalize_text(text)
    if not cleaned:
        return {"topic": "unknown", "confidence": 0.0, "matched_phrase": None}

    best_topic, best_phrase, best_score = "unknown", None, 0

    for topic, phrases in TOPIC_KEYWORDS.items():
        for phrase in phrases:
            phrase_clean = _normalize_text(phrase)
            if phrase_clean == cleaned:
                score = 100
            elif phrase_clean in cleaned:
                score = 90
            else:
                words = phrase_clean.split()
                matched = sum(1 for word in words if word in cleaned.split())
                score = round((matched / len(words)) * 70) if words else 0

            if score > best_score:
                best_topic, best_phrase, best_score = topic, phrase, score

    if best_score < 40:
        return {"topic": "unknown", "confidence": 25.0, "matched_phrase": None}

    return {
        "topic": best_topic,
        "confidence": float(best_score),
        "matched_phrase": best_phrase,
    }


def is_follow_up(command):
    cleaned = _normalize_text(command)
    if not cleaned:
        return False
    if cleaned in FOLLOW_UP_PATTERNS:
        return True

    starters = ("what about", "what are", "what is", "show", "give", "tell me", "why", "explain", "more")
    pronouns = ("it", "this", "that", "them", "those", "these", "recommendations", "details", "score", "status")

    return cleaned.startswith(starters) and any(token in cleaned.split() for token in pronouns)


def get_recent_context(limit=10):
    history = _safe_history()
    contexts = []

    for item in reversed(history[-limit:]):
        command = _extract_command(item)
        if not command:
            continue

        topic = detect_topic(command)
        contexts.append({
            "command": command,
            "response": _extract_response(item),
            "topic": topic["topic"],
            "topic_confidence": topic["confidence"],
        })

    return contexts


def get_last_meaningful_context():
    contexts = get_recent_context(limit=20)

    for context in contexts:
        if context["topic"] != "unknown":
            return context

    return contexts[0] if contexts else None


def resolve_context(command):
    direct_topic = detect_topic(command)
    follow_up = is_follow_up(command)
    previous = get_last_meaningful_context()

    if direct_topic["topic"] != "unknown":
        return {
            "command": command,
            "is_follow_up": follow_up,
            "resolved": True,
            "topic": direct_topic["topic"],
            "confidence": direct_topic["confidence"],
            "context_source": "Current Command",
            "previous_command": previous["command"] if previous else None,
            "recommended_action": "Route using the current command topic.",
        }

    if follow_up and previous:
        topic = previous.get("topic", "unknown")
        return {
            "command": command,
            "is_follow_up": True,
            "resolved": topic != "unknown",
            "topic": topic,
            "confidence": 85.0 if topic != "unknown" else 55.0,
            "context_source": "Conversation History",
            "previous_command": previous.get("command"),
            "recommended_action": (
                "Use the previous meaningful conversation topic to interpret this follow-up."
                if topic != "unknown"
                else "Ask the user to clarify the follow-up topic."
            ),
        }

    return {
        "command": command,
        "is_follow_up": follow_up,
        "resolved": False,
        "topic": "unknown",
        "confidence": 25.0,
        "context_source": "None",
        "previous_command": previous["command"] if previous else None,
        "recommended_action": "Use normal command routing or AI fallback. Ask for clarification if the request remains ambiguous.",
    }


def get_context_system_status():
    contexts = get_recent_context(limit=20)
    meaningful = [item for item in contexts if item.get("topic") != "unknown"]

    total = len(contexts)
    meaningful_count = len(meaningful)

    score = 60 if total == 0 else round(60 + (meaningful_count / total) * 40)
    score = max(0, min(100, score))

    if score >= 85:
        status = "Excellent"
    elif score >= 70:
        status = "Good"
    elif score >= 50:
        status = "Needs Attention"
    else:
        status = "Critical"

    return {
        "score": score,
        "status": status,
        "recent_entries": total,
        "meaningful_contexts": meaningful_count,
        "context_ready": meaningful_count > 0,
    }


def get_context_recommendations():
    status = get_context_system_status()
    recommendations = []

    if not status["context_ready"]:
        recommendations.append(
            "Build more conversation history so JERVIS can resolve follow-up context more reliably."
        )

    if status["recent_entries"] >= 20:
        recommendations.append(
            "Recent conversation context is rich enough for follow-up analysis."
        )

    if not recommendations:
        recommendations.append(
            "Context tracking looks ready for normal conversation continuity."
        )

    recommendations.append(
        "If a follow-up is ambiguous, JERVIS should ask for clarification instead of guessing."
    )

    return recommendations


def get_context_intelligence_report(command="what are the recommendations"):
    result = resolve_context(command)
    status = get_context_system_status()

    lines = [
        "JERVIS SMART CONTEXT & CONVERSATION INTELLIGENCE",
        "",
        f"Context Intelligence Score: {status['score']}/100",
        f"System Status: {status['status']}",
        f"Context Ready: {'Yes' if status['context_ready'] else 'No'}",
        f"Recent Context Entries: {status['recent_entries']}",
        "",
        "CONTEXT ANALYSIS",
        "",
        f"Command: {result['command']}",
        f"Follow-up Detected: {'Yes' if result['is_follow_up'] else 'No'}",
        f"Resolved Topic: {result['topic']}",
        f"Context Confidence: {result['confidence']}%",
        f"Context Source: {result['context_source']}",
    ]

    if result.get("previous_command"):
        lines.append(f"Previous Command: {result['previous_command']}")

    lines.extend([
        f"Resolution Status: {'Resolved' if result['resolved'] else 'Needs Clarification'}",
        "",
        "RECOMMENDED CONTEXT ACTION",
        f"- {result['recommended_action']}",
        "",
        "CONTEXT RECOMMENDATIONS",
    ])

    lines.extend(f"- {item}" for item in get_context_recommendations())

    lines.extend([
        "",
        "Safety: Context Intelligence analyzes conversation continuity only. It does not execute the analyzed command.",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_context_intelligence_report("what are the recommendations"))