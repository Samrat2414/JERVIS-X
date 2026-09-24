from core import diagnostics


def test_packaged_app_skips_source_file_checks(monkeypatch):
    monkeypatch.setattr(
        diagnostics.sys,
        "frozen",
        True,
        raising=False,
    )

    assert diagnostics.check_required_files() == []
    assert diagnostics.check_required_folders() == []
def test_security_bootstrap_health_passes_for_valid_audit(monkeypatch):
    monkeypatch.setattr(
        diagnostics,
        "verify_confirmation_audit_integrity",
        lambda: {
            "valid": True,
            "event_count": 1,
            "failed_index": None,
            "reason": "Confirmation audit trail integrity verified.",
        },
    )

    result = diagnostics.check_security_bootstrap()

    assert result["healthy"] is True
    assert result["event_count"] == 1
    assert result["reason"] == "Confirmation audit trail integrity verified."


def test_security_bootstrap_health_fails_for_invalid_audit(monkeypatch):
    monkeypatch.setattr(
        diagnostics,
        "verify_confirmation_audit_integrity",
        lambda: {
            "valid": False,
            "event_count": 1,
            "failed_index": 0,
            "reason": "Audit event hash does not match event data.",
        },
    )

    result = diagnostics.check_security_bootstrap()

    assert result["healthy"] is False
    assert result["failed_index"] == 0
    assert result["reason"] == "Audit event hash does not match event data."

def test_run_diagnostics_includes_security_bootstrap(monkeypatch):
    monkeypatch.setattr(
        diagnostics,
        "check_required_files",
        lambda: [],
    )
    monkeypatch.setattr(
        diagnostics,
        "check_required_folders",
        lambda: [],
    )
    monkeypatch.setattr(
        diagnostics,
        "check_dependencies",
        lambda: [],
    )
    monkeypatch.setattr(
        diagnostics,
        "check_internet",
        lambda: True,
    )
    monkeypatch.setattr(
        diagnostics,
        "check_data_folder",
        lambda: True,
    )
    monkeypatch.setattr(
        diagnostics,
        "check_security_bootstrap",
        lambda: {
            "healthy": True,
            "event_count": 1,
            "failed_index": None,
            "reason": "Confirmation audit trail integrity verified.",
        },
    )

    result = diagnostics.run_diagnostics()

    assert result["checks"]["Security Bootstrap"] is True
    assert result["passed"] == 6
    assert result["total"] == 6
    assert result["healthy"] is True
    assert result["security_bootstrap"]["event_count"] == 1

def test_diagnostics_report_includes_security_failure_reason(monkeypatch):
    monkeypatch.setattr(
        diagnostics,
        "run_diagnostics",
        lambda: {
            "passed": 5,
            "total": 6,
            "healthy": False,
            "checks": {
                "Required Files": True,
                "Required Folders": True,
                "Dependencies": True,
                "Internet": True,
                "Data Folder": True,
                "Security Bootstrap": False,
            },
            "missing_files": [],
            "missing_folders": [],
            "missing_dependencies": [],
            "internet": True,
            "data_writable": True,
            "security_bootstrap": {
                "healthy": False,
                "event_count": 1,
                "failed_index": 0,
                "reason": "Audit event hash does not match event data.",
            },
        },
    )

    report = diagnostics.get_diagnostics_report()

    assert "Health Score: 5/6" in report
    assert "Security Bootstrap: FAIL" in report
    assert (
        "Security Reason: Audit event hash does not match event data."
        in report
    )
    assert "Status: JERVIS needs attention." in report

def test_security_bootstrap_handles_verifier_exception(monkeypatch):
    def raise_verification_error():
        raise OSError("audit storage unavailable")

    monkeypatch.setattr(
        diagnostics,
        "verify_confirmation_audit_integrity",
        raise_verification_error,
    )

    result = diagnostics.check_security_bootstrap()

    assert result["healthy"] is False
    assert result["event_count"] == 0
    assert result["failed_index"] is None
    assert (
        result["reason"]
        == "Security audit integrity check failed: audit storage unavailable"
    )


def test_security_bootstrap_rejects_invalid_verifier_result(monkeypatch):
    monkeypatch.setattr(
        diagnostics,
        "verify_confirmation_audit_integrity",
        lambda: None,
    )

    result = diagnostics.check_security_bootstrap()

    assert result == {
        "healthy": False,
        "event_count": 0,
        "failed_index": None,
        "reason": "Security audit integrity check returned an invalid result.",
    }
