from datetime import datetime
from pathlib import Path

from core.backup_manager import (
    get_backups,
    get_latest_backup,
)


STALE_BACKUP_HOURS = 72


def _backup_timestamp(backup):
    if not backup:
        return None

    if isinstance(backup, dict):
        for key in (
            "timestamp",
            "created_at",
            "created",
            "date",
        ):
            value = backup.get(key)

            if value:
                return value

    return None


def _parse_backup_time(value):
    if not value:
        return None

    value = str(value).strip()

    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y%m%d_%H%M%S",
        "%Y-%m-%d_%H-%M-%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                value,
                fmt,
            )
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(
            value
        )
    except ValueError:
        return None


def _backup_path(backup):
    if not backup:
        return None

    if isinstance(backup, dict):
        for key in (
            "path",
            "file",
            "backup_path",
            "location",
        ):
            value = backup.get(key)

            if value:
                return Path(value)

    if isinstance(
        backup,
        (str, Path),
    ):
        return Path(backup)

    return None


def get_backup_intelligence():
    backups = get_backups()

    if not backups:
        backups = []

    latest = get_latest_backup()

    backup_count = len(backups)

    latest_path = _backup_path(
        latest
    )

    latest_exists = False

    if latest_path:
        try:
            latest_exists = (
                latest_path.exists()
            )
        except OSError:
            latest_exists = False

    latest_time_text = _backup_timestamp(
        latest
    )

    latest_time = _parse_backup_time(
        latest_time_text
    )

    age_hours = None

    if latest_time:
        age_seconds = (
            datetime.now()
            - latest_time
        ).total_seconds()

        age_hours = round(
            max(
                0,
                age_seconds / 3600,
            ),
            2,
        )

    risks = []
    recommendations = []

    score = 100

    if backup_count == 0:
        score -= 50

        risks.append(
            "No backups are currently available."
        )

        recommendations.append(
            "Create a backup before making major changes to JERVIS."
        )

    if latest and not latest_exists:
        score -= 25

        risks.append(
            "The latest backup record exists, but its backup path is unavailable."
        )

        recommendations.append(
            "Verify the backup location and create a fresh backup."
        )

    if (
        age_hours is not None
        and age_hours
        > STALE_BACKUP_HOURS
    ):
        score -= 20

        risks.append(
            (
                f"The latest backup is "
                f"{age_hours} hours old."
            )
        )

        recommendations.append(
            "Create a newer backup to improve recovery readiness."
        )

    if (
        backup_count > 0
        and latest_exists
        and (
            age_hours is None
            or age_hours
            <= STALE_BACKUP_HOURS
        )
    ):
        recommendations.append(
            "Backup availability looks healthy."
        )

    score = max(
        0,
        min(
            100,
            score,
        ),
    )

    if score >= 85:
        status = "Excellent"

    elif score >= 70:
        status = "Good"

    elif score >= 50:
        status = "Needs Attention"

    else:
        status = "Critical"

    recovery_ready = (
        backup_count > 0
        and latest_exists
    )

    return {
        "score": score,
        "status": status,
        "backup_count": backup_count,
        "latest_backup": latest,
        "latest_exists": latest_exists,
        "latest_age_hours": age_hours,
        "recovery_ready": recovery_ready,
        "risks": risks,
        "recommendations": recommendations,
    }


def get_backup_recommendations():
    return get_backup_intelligence()[
        "recommendations"
    ]


def get_backup_intelligence_report():
    result = get_backup_intelligence()

    lines = [
        "JERVIS SMART BACKUP & RECOVERY INTELLIGENCE",
        "",
        (
            f"Backup Health Score: "
            f"{result['score']}/100"
        ),
        (
            f"Backup Status: "
            f"{result['status']}"
        ),
        (
            f"Backup Count: "
            f"{result['backup_count']}"
        ),
        (
            f"Recovery Ready: "
            f"{'Yes' if result['recovery_ready'] else 'No'}"
        ),
        "",
        "LATEST BACKUP",
        "",
    ]

    latest = result[
        "latest_backup"
    ]

    if latest:
        lines.append(
            str(latest)
        )

        if (
            result[
                "latest_age_hours"
            ]
            is not None
        ):
            lines.append(
                (
                    f"Age: "
                    f"{result['latest_age_hours']} hours"
                )
            )

        lines.append(
            (
                f"Backup Path Available: "
                f"{'Yes' if result['latest_exists'] else 'No'}"
            )
        )

    else:
        lines.append(
            "No latest backup available."
        )

    lines.extend(
        [
            "",
            "DETECTED RISKS",
        ]
    )

    if result["risks"]:
        for risk in result[
            "risks"
        ]:
            lines.append(
                f"- {risk}"
            )

    else:
        lines.append(
            "- No major backup risk detected."
        )

    lines.extend(
        [
            "",
            "BACKUP RECOMMENDATIONS",
        ]
    )

    for recommendation in result[
        "recommendations"
    ]:
        lines.append(
            f"- {recommendation}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: Backup intelligence is advisory. "
                "Restore operations should only run "
                "after explicit user confirmation."
            ),
        ]
    )

    return "\n".join(
        lines
    )


if __name__ == "__main__":
    print(
        get_backup_intelligence_report()
    )