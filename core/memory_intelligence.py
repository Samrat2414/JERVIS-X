from core.memory import load_memory, recall, recall_fact


def _safe_memory():
    try:
        memory = load_memory()
    except Exception:
        memory = {}

    return memory if isinstance(memory, dict) else {}


def _split_memory(memory):
    facts = {}
    general = {}

    for key, value in memory.items():
        if key == "facts" and isinstance(value, dict):
            facts.update(value)
        else:
            general[key] = value

    return general, facts


def get_memory_intelligence():
    memory = _safe_memory()
    general, facts = _split_memory(memory)

    general_count = len(general)
    fact_count = len(facts)
    total_items = general_count + fact_count

    keys = sorted(str(key) for key in general.keys())
    fact_keys = sorted(str(key) for key in facts.keys())

    risks = []
    insights = []
    recommendations = []
    score = 100

    if total_items == 0:
        score -= 40
        risks.append("No stored JERVIS memory items were detected.")
        recommendations.append(
            "Store useful non-sensitive preferences or facts to improve recall."
        )
    elif total_items < 3:
        score -= 10
        insights.append(
            "Memory storage is available but currently contains only a few items."
        )
    else:
        insights.append(
            f"JERVIS currently stores {total_items} memory item(s)."
        )

    normalized = {}
    duplicate_candidates = []

    for key in list(general.keys()) + list(facts.keys()):
        normalized_key = str(key).strip().lower()

        if normalized_key in normalized:
            duplicate_candidates.append(str(key))
        else:
            normalized[normalized_key] = str(key)

    if duplicate_candidates:
        score -= 10
        risks.append("Similar or duplicate memory keys may exist.")
        recommendations.append(
            "Review duplicate memory keys to keep recall clean."
        )

    if any(
        len(str(key)) > 50
        for key in list(general.keys()) + list(facts.keys())
    ):
        recommendations.append(
            "Use short, consistent memory keys for easier recall."
        )

    recall_ready = total_items > 0

    if recall_ready:
        insights.append("Memory recall is ready.")

    if fact_count:
        insights.append(
            f"{fact_count} fact-style memory item(s) are available."
        )

    if general_count:
        insights.append(
            f"{general_count} general memory item(s) are available."
        )

    if total_items >= 20:
        recommendations.append(
            "Consider periodically reviewing stored memory to remove outdated items."
        )

    if not recommendations:
        recommendations.append(
            "Memory storage and recall look healthy."
        )

    score = max(0, min(100, score))

    if score >= 85:
        status = "Excellent"
    elif score >= 70:
        status = "Good"
    elif score >= 50:
        status = "Needs Attention"
    else:
        status = "Low Memory"

    return {
        "score": score,
        "status": status,
        "total_items": total_items,
        "general_count": general_count,
        "fact_count": fact_count,
        "recall_ready": recall_ready,
        "keys": keys,
        "fact_keys": fact_keys,
        "risks": risks,
        "insights": insights,
        "recommendations": recommendations,
    }


def get_memory_recommendations():
    return get_memory_intelligence()["recommendations"]


def test_memory_recall(key):
    key = str(key).strip()

    if not key:
        return {
            "key": "",
            "found": False,
            "value": None,
            "source": "None",
        }

    value = recall(key)

    if value is not None:
        return {
            "key": key,
            "found": True,
            "value": value,
            "source": "General Memory",
        }

    fact_value = recall_fact(key)

    if fact_value is not None:
        return {
            "key": key,
            "found": True,
            "value": fact_value,
            "source": "Fact Memory",
        }

    return {
        "key": key,
        "found": False,
        "value": None,
        "source": "None",
    }


def get_memory_intelligence_report():
    result = get_memory_intelligence()

    lines = [
        "JERVIS SMART MEMORY INTELLIGENCE",
        "",
        f"Memory Health Score: {result['score']}/100",
        f"Memory Status: {result['status']}",
        f"Stored Items: {result['total_items']}",
        f"General Memory: {result['general_count']}",
        f"Fact Memory: {result['fact_count']}",
        f"Recall Ready: {'Yes' if result['recall_ready'] else 'No'}",
        "",
        "MEMORY KEYS",
        "",
    ]

    if result["keys"]:
        lines.extend(
            f"{i}. {key}"
            for i, key in enumerate(result["keys"], start=1)
        )
    else:
        lines.append("No general memory keys stored.")

    lines.extend(["", "FACT KEYS", ""])

    if result["fact_keys"]:
        lines.extend(
            f"{i}. {key}"
            for i, key in enumerate(result["fact_keys"], start=1)
        )
    else:
        lines.append("No fact memory keys stored.")

    lines.extend(["", "MEMORY RISKS"])

    if result["risks"]:
        lines.extend(f"- {item}" for item in result["risks"])
    else:
        lines.append("- No major memory risk detected.")

    lines.extend(["", "MEMORY INSIGHTS"])

    if result["insights"]:
        lines.extend(f"- {item}" for item in result["insights"])
    else:
        lines.append("- No memory insight is currently available.")

    lines.extend(["", "MEMORY RECOMMENDATIONS"])
    lines.extend(
        f"- {item}"
        for item in result["recommendations"]
    )

    lines.extend(
        [
            "",
            "Privacy: Memory Intelligence analyzes locally stored JERVIS memory data only.",
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(get_memory_intelligence_report())