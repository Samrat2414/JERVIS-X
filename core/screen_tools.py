import os
from datetime import datetime
from pathlib import Path

from PIL import ImageGrab


SCREENSHOT_DIR = Path("screenshots")


def take_screenshot(file_name=None):
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not file_name:
        file_name = (
            "screenshot_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".png"
        )

    if not file_name.lower().endswith(".png"):
        file_name += ".png"

    file_path = SCREENSHOT_DIR / file_name

    try:
        image = ImageGrab.grab()
        image.save(file_path)

        return {
            "success": True,
            "path": str(file_path),
            "message": f"Screenshot saved as {file_path}.",
        }

    except Exception as error:
        return {
            "success": False,
            "error": f"I could not take a screenshot: {error}",
        }


def take_screenshot_text(file_name=None):
    result = take_screenshot(file_name)

    if result["success"]:
        return result["message"]

    return result["error"]


def get_latest_screenshot():
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    screenshots = list(
        SCREENSHOT_DIR.glob("*.png")
    )

    if not screenshots:
        return None

    return max(
        screenshots,
        key=lambda file: file.stat().st_mtime,
    )


def open_screenshot_folder():
    SCREENSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        os.startfile(
            SCREENSHOT_DIR.resolve()
        )

        return "Opening screenshots folder."

    except Exception as error:
        return (
            f"I could not open the screenshots folder: {error}"
        )


if __name__ == "__main__":
    print(
        take_screenshot_text()
    )