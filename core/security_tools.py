import secrets
import string


def generate_password(
    length=16,
    use_uppercase=True,
    use_lowercase=True,
    use_numbers=True,
    use_symbols=True,
):
    try:
        length = int(length)
    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "Password length must be a number.",
        }

    if length < 4:
        return {
            "success": False,
            "error": "Password length must be at least 4.",
        }

    if length > 128:
        return {
            "success": False,
            "error": "Password length cannot exceed 128.",
        }

    character_pool = ""
    required_characters = []

    if use_uppercase:
        character_pool += string.ascii_uppercase
        required_characters.append(
            secrets.choice(string.ascii_uppercase)
        )

    if use_lowercase:
        character_pool += string.ascii_lowercase
        required_characters.append(
            secrets.choice(string.ascii_lowercase)
        )

    if use_numbers:
        character_pool += string.digits
        required_characters.append(
            secrets.choice(string.digits)
        )

    if use_symbols:
        safe_symbols = "!@#$%^&*()-_=+"
        character_pool += safe_symbols
        required_characters.append(
            secrets.choice(safe_symbols)
        )

    if not character_pool:
        return {
            "success": False,
            "error": "Select at least one character type.",
        }

    if length < len(required_characters):
        return {
            "success": False,
            "error": (
                "Password length is too short "
                "for the selected options."
            ),
        }

    remaining_length = (
        length - len(required_characters)
    )

    password_chars = required_characters + [
        secrets.choice(character_pool)
        for _ in range(remaining_length)
    ]

    secrets.SystemRandom().shuffle(password_chars)

    password = "".join(password_chars)

    return {
        "success": True,
        "password": password,
        "strength": get_password_strength(password),
    }


def get_password_strength(password):
    score = 0

    if len(password) >= 8:
        score += 1

    if len(password) >= 12:
        score += 1

    if any(char.isupper() for char in password):
        score += 1

    if any(char.islower() for char in password):
        score += 1

    if any(char.isdigit() for char in password):
        score += 1

    if any(
        char in "!@#$%^&*()-_=+"
        for char in password
    ):
        score += 1

    if score <= 2:
        return "Weak"

    if score <= 4:
        return "Medium"

    return "Strong"


def generate_password_text(length=16):
    result = generate_password(length=length)

    if not result["success"]:
        return result["error"]

    return (
        f"Generated password: {result['password']}\n"
        f"Strength: {result['strength']}"
    )


if __name__ == "__main__":
    print(generate_password_text(16))