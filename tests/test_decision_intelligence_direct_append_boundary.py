from pathlib import Path


DECISION_MODULE = Path("core/decision_intelligence.py")


def _source():
    return DECISION_MODULE.read_text(encoding="utf-8")


def test_all_decision_insertions_use_central_add_decision_boundary():
    source = _source()

    direct_appends = source.count("decisions.append(")

    assert direct_appends == 1, (
        "Global decision intelligence contains decision insertions "
        "that bypass _add_decision(). "
        f"Found {direct_appends} direct decisions.append() calls."
    )


def test_raw_direct_append_confidence_float_conversion_is_absent():
    source = _source()

    assert '"confidence": float(' not in source, (
        "Direct decision construction performs raw float() confidence "
        "conversion outside the global _safe_confidence boundary."
    )
