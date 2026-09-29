"""
V38 contract specification.

This file freezes the intended public contract for Confirmation Threat
Forecast Calibration Trend Forecast Calibration Intelligence before the
production engine is created.

V38 remains deterministic, advisory-only, read-only, and incapable of
automatic security execution.
"""

V38_REQUIRED_INPUT_FIELDS = {
    "calibration_trend_forecast_score",
    "calibration_trend_forecast_classification",
    "forecast_direction",
    "snapshots_evaluated",
    "latest_calibration_score",
    "projected_calibration_score",
    "projected_score_change",
    "forecast_confidence",
    "sufficient_history",
    "integrity_valid",
    "history_truncated",
    "human_review_required",
    "automation_allowed",
    "read_only",
}


V38_REQUIRED_OUTPUT_FIELDS = {
    "calibration_score",
    "calibration_classification",
    "forecast_score",
    "forecast_classification",
    "forecast_direction",
    "forecast_confidence",
    "calibration_delta",
    "integrity_valid",
    "sufficient_history",
    "history_truncated",
    "indicators",
    "recommendations",
    "human_review_required",
    "automation_allowed",
    "read_only",
}


def test_v38_contract_consumes_verified_v37_forecast_fields():
    assert V38_REQUIRED_INPUT_FIELDS == {
        "calibration_trend_forecast_score",
        "calibration_trend_forecast_classification",
        "forecast_direction",
        "snapshots_evaluated",
        "latest_calibration_score",
        "projected_calibration_score",
        "projected_score_change",
        "forecast_confidence",
        "sufficient_history",
        "integrity_valid",
        "history_truncated",
        "human_review_required",
        "automation_allowed",
        "read_only",
    }


def test_v38_contract_defines_explicit_output_schema():
    assert V38_REQUIRED_OUTPUT_FIELDS == {
        "calibration_score",
        "calibration_classification",
        "forecast_score",
        "forecast_classification",
        "forecast_direction",
        "forecast_confidence",
        "calibration_delta",
        "integrity_valid",
        "sufficient_history",
        "history_truncated",
        "indicators",
        "recommendations",
        "human_review_required",
        "automation_allowed",
        "read_only",
    }


def test_v38_contract_preserves_v37_confidence_name():
    assert "forecast_confidence" in V38_REQUIRED_INPUT_FIELDS
    assert "confidence" not in V38_REQUIRED_INPUT_FIELDS


def test_v38_contract_requires_integrity_state():
    assert {
        "integrity_valid",
        "sufficient_history",
        "history_truncated",
    } <= V38_REQUIRED_OUTPUT_FIELDS


def test_v38_contract_requires_human_review_state():
    assert "human_review_required" in V38_REQUIRED_OUTPUT_FIELDS


def test_v38_contract_is_read_only():
    required_safety_fields = {
        "automation_allowed",
        "read_only",
    }

    assert required_safety_fields <= V38_REQUIRED_OUTPUT_FIELDS


def test_v38_contract_has_no_execution_fields():
    forbidden = {
        "execute",
        "execute_action",
        "execute_decision",
        "automatic_execution",
        "pending_confirmation",
        "confirmation_token",
        "system_action",
    }

    assert V38_REQUIRED_OUTPUT_FIELDS.isdisjoint(forbidden)


def test_v38_contract_separates_calibration_from_forecast():
    assert "calibration_score" in V38_REQUIRED_OUTPUT_FIELDS
    assert "forecast_score" in V38_REQUIRED_OUTPUT_FIELDS

    assert "calibration_classification" in V38_REQUIRED_OUTPUT_FIELDS
    assert "forecast_classification" in V38_REQUIRED_OUTPUT_FIELDS


def test_v38_contract_exposes_calibration_delta():
    assert "calibration_delta" in V38_REQUIRED_OUTPUT_FIELDS