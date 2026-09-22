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
    assert data["total"] == 5
    assert len(data["checks"]) == 5
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
