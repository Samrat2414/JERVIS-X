import json
import subprocess
import sys

from core.version import (
    APP_DISPLAY_NAME,
    APP_NAME,
    APP_TITLE,
    VERSION_TEXT,
    __version__,
)


def test_version_constants():
    assert APP_NAME == "JERVIS-X"
    assert APP_DISPLAY_NAME == "JERVIS X"
    assert __version__.count(".") == 2


def test_version_display_text():
    assert APP_TITLE == f"JERVIS X v{__version__}"
    assert VERSION_TEXT == (
        f"JERVIS-X Version {__version__} - "
        "Advanced Personal AI Virtual Assistant"
    )

def test_command_line_version():
    result = subprocess.run(
        [sys.executable, "main.py", "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == VERSION_TEXT


def test_command_line_help():
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Usage:" in result.stdout
    assert "--version" in result.stdout
    assert "Launch the JERVIS-X GUI" in result.stdout


def test_unknown_command_line_option():
    result = subprocess.run(
        [sys.executable, "main.py", "--unknown"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Unknown option: --unknown" in result.stdout
    assert "Usage:" in result.stdout


def test_command_line_diagnostics():
    result = subprocess.run(
        [sys.executable, "main.py", "--diagnostics"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS SELF-DIAGNOSTICS" in result.stdout
    assert "Health Score:" in result.stdout


def test_command_line_diagnostics_json():
    result = subprocess.run(
        [sys.executable, "main.py", "--diagnostics-json"],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert data["total"] == 6
    assert data["checks"]["Security Bootstrap"] is True
    assert data["security_bootstrap"]["healthy"] is True
    assert len(data["checks"]) == 6
    assert "healthy" in data


def test_command_line_career_intelligence():
    result = subprocess.run(
        [sys.executable, "main.py", "career intelligence"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS SMART CAREER & JOB INTELLIGENCE" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Target Role:" in result.stdout


def test_command_line_best_career_action():
    result = subprocess.run(
        [sys.executable, "main.py", "best career action"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS BEST NEXT CAREER ACTION" in result.stdout
    assert "Action:" in result.stdout
    assert "Priority:" in result.stdout
    assert "Reason:" in result.stdout


def test_command_line_career_recommendations():
    result = subprocess.run(
        [sys.executable, "main.py", "career recommendations"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS CAREER RECOMMENDATIONS" in result.stdout
    assert "Safety: Career Intelligence provides planning recommendations only." in result.stdout


def test_command_line_set_target_role():
    result = subprocess.run(
        [sys.executable, "main.py", "set target role Python Developer"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Target career role set to Python Developer." in result.stdout


def test_command_line_set_project_readiness():
    result = subprocess.run(
        [sys.executable, "main.py", "set project readiness 75"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Project readiness updated to 75.0%." in result.stdout


def test_command_line_set_resume_readiness():
    result = subprocess.run(
        [sys.executable, "main.py", "set resume readiness 80"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Resume readiness updated to 80.0%." in result.stdout


def test_command_line_set_application_readiness():
    result = subprocess.run(
        [sys.executable, "main.py", "set application readiness 70"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Application readiness updated to 70.0%." in result.stdout


def test_command_line_job_readiness():
    result = subprocess.run(
        [sys.executable, "main.py", "job readiness"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS CAREER & JOB READINESS" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Career Status:" in result.stdout
    assert "Target Role:" in result.stdout


def test_command_line_job_intelligence():
    result = subprocess.run(
        [sys.executable, "main.py", "job intelligence"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS SMART CAREER & JOB INTELLIGENCE" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Target Role:" in result.stdout
    assert "BEST NEXT CAREER ACTION" in result.stdout


def test_command_line_career_report():
    result = subprocess.run(
        [sys.executable, "main.py", "career report"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS SMART CAREER & JOB INTELLIGENCE" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Target Role:" in result.stdout
    assert "BEST NEXT CAREER ACTION" in result.stdout


def test_command_line_job_readiness_report():
    result = subprocess.run(
        [sys.executable, "main.py", "job readiness report"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS SMART CAREER & JOB INTELLIGENCE" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Target Role:" in result.stdout
    assert "BEST NEXT CAREER ACTION" in result.stdout


def test_command_line_career_intelligence_report():
    result = subprocess.run(
        [sys.executable, "main.py", "career intelligence report"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS SMART CAREER & JOB INTELLIGENCE" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Target Role:" in result.stdout
    assert "BEST NEXT CAREER ACTION" in result.stdout


def test_command_line_job_intelligence_report():
    result = subprocess.run(
        [sys.executable, "main.py", "job intelligence report"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS SMART CAREER & JOB INTELLIGENCE" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Target Role:" in result.stdout
    assert "BEST NEXT CAREER ACTION" in result.stdout


def test_command_line_career_readiness():
    result = subprocess.run(
        [sys.executable, "main.py", "career readiness"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS CAREER & JOB READINESS" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Career Status:" in result.stdout
    assert "Target Role:" in result.stdout


def test_command_line_job_readiness_score():
    result = subprocess.run(
        [sys.executable, "main.py", "job readiness score"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS CAREER & JOB READINESS" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Career Status:" in result.stdout
    assert "Target Role:" in result.stdout


def test_command_line_career_readiness_score():
    result = subprocess.run(
        [sys.executable, "main.py", "career readiness score"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS CAREER & JOB READINESS" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Career Status:" in result.stdout
    assert "Target Role:" in result.stdout


def test_command_line_career_score():
    result = subprocess.run(
        [sys.executable, "main.py", "career score"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS CAREER & JOB READINESS" in result.stdout
    assert "Job Readiness Score:" in result.stdout
    assert "Career Status:" in result.stdout
    assert "Target Role:" in result.stdout


def test_command_line_best_next_career_action():
    result = subprocess.run(
        [sys.executable, "main.py", "best next career action"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS BEST NEXT CAREER ACTION" in result.stdout
    assert "Action:" in result.stdout
    assert "Priority:" in result.stdout
    assert "Reason:" in result.stdout


def test_command_line_what_should_i_do_to_become_job_ready():
    result = subprocess.run(
        [sys.executable, "main.py", "what should i do to become job ready"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "JERVIS BEST NEXT CAREER ACTION" in result.stdout
    assert "Action:" in result.stdout
    assert "Priority:" in result.stdout
    assert "Reason:" in result.stdout


def test_command_line_security_status():
    result = subprocess.run(
        [sys.executable, "main.py", "--security-status"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "JERVIS SECURITY STATUS" in result.stdout
    assert "Component: confirmation_audit" in result.stdout
    assert "Status: HEALTHY" in result.stdout
    assert "Events:" in result.stdout
    assert "Message:" in result.stdout


def test_command_line_security_status_json():
    result = subprocess.run(
        [sys.executable, "main.py", "--security-status-json"],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    assert data["success"] is True
    assert data["component"] == "confirmation_audit"
    assert isinstance(data["event_count"], int)
    assert isinstance(data["message"], str)


def test_command_line_security_history():
    result = subprocess.run(
        [sys.executable, "main.py", "--security-history"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "JERVIS SECURITY HISTORY" in result.stdout
    assert "Component: confirmation_audit" in result.stdout
    assert "Status: HEALTHY" in result.stdout
    assert "Events:" in result.stdout
    assert "Message:" in result.stdout


def test_command_line_security_history_json():
    result = subprocess.run(
        [sys.executable, "main.py", "--security-history-json"],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    assert isinstance(data, list)
    assert len(data) >= 1

    latest = data[-1]

    assert latest["success"] is True
    assert latest["component"] == "confirmation_audit"
    assert isinstance(latest["event_count"], int)
    assert isinstance(latest["message"], str)


def test_security_history_cli_is_read_only():
    from pathlib import Path

    main_source = Path("main.py").read_text(encoding="utf-8")

    history_block_start = main_source.index(
        '    if "--security-history-json" in sys.argv:'
    )
    status_block_start = main_source.index(
        '    if "--security-status-json" in sys.argv:'
    )

    history_source = main_source[
        history_block_start:status_block_start
    ]

    assert "load_security_bootstrap_history" in history_source
    assert "initialize_security_bootstrap" not in history_source


def test_security_history_commands_do_not_change_persistent_file():
    import hashlib
    from pathlib import Path

    history_path = Path("data/security_bootstrap_history.json")

    if not history_path.exists():
        return

    before = hashlib.sha256(
        history_path.read_bytes()
    ).hexdigest()

    for option in (
        "--security-history",
        "--security-history-json",
    ):
        result = subprocess.run(
            [sys.executable, "main.py", option],
            check=True,
            capture_output=True,
            text=True,
        )

        assert result.stdout

    after = hashlib.sha256(
        history_path.read_bytes()
    ).hexdigest()

    assert after == before
