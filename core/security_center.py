from core.security_lock import (
    is_security_enabled,
    get_security_status,
)
from core.security_tools import (
    get_password_strength,
)


def get_security_analysis():
    pin_enabled = is_security_enabled()

    score = 100
    risks = []
    recommendations = []

    if not pin_enabled:
        score -= 35

        risks.append(
            "JERVIS PIN security lock is disabled."
        )

        recommendations.append(
            "Enable the JERVIS PIN security lock."
        )

    else:
        recommendations.append(
            "JERVIS PIN security lock is enabled."
        )

    # Advisory-only Windows security checks are intentionally
    # not changed automatically by JERVIS.
    recommendations.append(
        "Use a strong and unique password for Windows and important accounts."
    )

    recommendations.append(
        "Keep Windows Security and antivirus protection enabled."
    )

    recommendations.append(
        "Install trusted software only and avoid unknown downloads."
    )

    recommendations.append(
        "Keep Windows and installed applications updated."
    )

    if score >= 85:
        status = "Strong"

    elif score >= 65:
        status = "Good"

    elif score >= 40:
        status = "Needs Attention"

    else:
        status = "Critical"

    return {
        "score": score,
        "status": status,
        "pin_enabled": pin_enabled,
        "risks": risks,
        "recommendations": recommendations,
    }


def analyze_password(password):
    result = get_password_strength(
        password
    )

    return {
        "password": password,
        "strength": result,
    }


def get_security_recommendations():
    return get_security_analysis()[
        "recommendations"
    ]


def get_security_report():
    result = get_security_analysis()

    lines = [
        "JERVIS SMART SECURITY CENTER",
        "",
        f"Security Score: {result['score']}/100",
        f"Security Status: {result['status']}",
        (
            "PIN Lock: Enabled"
            if result["pin_enabled"]
            else "PIN Lock: Disabled"
        ),
        "",
        "SECURITY LOCK STATUS",
        "",
        get_security_status(),
        "",
        "DETECTED RISKS",
    ]

    if result["risks"]:
        for risk in result["risks"]:
            lines.append(
                f"- {risk}"
            )

    else:
        lines.append(
            "- No major JERVIS security risk detected."
        )

    lines.extend(
        [
            "",
            "SECURITY RECOMMENDATIONS",
        ]
    )

    for recommendation in (
        result["recommendations"]
    ):
        lines.append(
            f"- {recommendation}"
        )

    lines.extend(
        [
            "",
            (
                "Safety: Advisory mode only. "
                "JERVIS will not automatically change "
                "Windows security settings."
            ),
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        get_security_report()
    )