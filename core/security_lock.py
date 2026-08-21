import hashlib
import json
from pathlib import Path


DATA_DIR = Path("data")
SECURITY_FILE = DATA_DIR / "security.json"

DEFAULT_PIN = "1234"


def _hash_pin(pin):
    return hashlib.sha256(
        str(pin).encode("utf-8")
    ).hexdigest()


def _load_security():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not SECURITY_FILE.exists():
        data = {
            "pin_hash": _hash_pin(DEFAULT_PIN),
            "enabled": False,
            "failed_attempts": 0,
        }

        _save_security(data)
        return data

    try:
        with SECURITY_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        data.setdefault(
            "pin_hash",
            _hash_pin(DEFAULT_PIN),
        )
        data.setdefault(
            "enabled",
            False,
        )
        data.setdefault(
            "failed_attempts",
            0,
        )

        return data

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {
            "pin_hash": _hash_pin(DEFAULT_PIN),
            "enabled": False,
            "failed_attempts": 0,
        }


def _save_security(data):
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with SECURITY_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
        )


def is_security_enabled():
    data = _load_security()

    return bool(
        data.get("enabled", False)
    )


def enable_security():
    data = _load_security()
    data["enabled"] = True

    try:
        _save_security(data)
        return "JERVIS app lock enabled."

    except OSError as error:
        return (
            f"Could not enable app lock: "
            f"{error}"
        )


def disable_security():
    data = _load_security()
    data["enabled"] = False
    data["failed_attempts"] = 0

    try:
        _save_security(data)
        return "JERVIS app lock disabled."

    except OSError as error:
        return (
            f"Could not disable app lock: "
            f"{error}"
        )


def verify_pin(pin):
    data = _load_security()

    if (
        _hash_pin(pin)
        == data["pin_hash"]
    ):
        data["failed_attempts"] = 0

        try:
            _save_security(data)
        except OSError:
            pass

        return {
            "success": True,
            "message": "PIN verified.",
        }

    data["failed_attempts"] += 1

    try:
        _save_security(data)
    except OSError:
        pass

    return {
        "success": False,
        "message": "Incorrect PIN.",
        "failed_attempts": data[
            "failed_attempts"
        ],
    }


def change_pin(
    current_pin,
    new_pin,
):
    verification = verify_pin(
        current_pin
    )

    if not verification["success"]:
        return "Current PIN is incorrect."

    new_pin = str(new_pin).strip()

    if (
        not new_pin.isdigit()
        or len(new_pin) < 4
        or len(new_pin) > 8
    ):
        return (
            "New PIN must contain "
            "4 to 8 digits."
        )

    data = _load_security()
    data["pin_hash"] = _hash_pin(
        new_pin
    )
    data["failed_attempts"] = 0

    try:
        _save_security(data)

        return "JERVIS PIN changed successfully."

    except OSError as error:
        return (
            f"Could not change PIN: "
            f"{error}"
        )


def get_security_status():
    data = _load_security()

    return (
        f"App Lock: "
        f"{'Enabled' if data['enabled'] else 'Disabled'}\n"
        f"Failed Attempts: "
        f"{data['failed_attempts']}"
    )


if __name__ == "__main__":
    print(get_security_status())
    print(verify_pin("1234"))