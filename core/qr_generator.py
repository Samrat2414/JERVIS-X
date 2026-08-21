from datetime import datetime
from pathlib import Path

import qrcode


QR_DIR = Path("generated_qr")


def generate_qr(data, file_name=None):
    data = str(data).strip()

    if not data:
        return {
            "success": False,
            "error": "Please provide text or a URL for the QR code.",
        }

    QR_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not file_name:
        file_name = (
            "qr_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".png"
        )

    if not file_name.lower().endswith(".png"):
        file_name += ".png"

    file_path = QR_DIR / file_name

    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)

        image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        image.save(file_path)

        return {
            "success": True,
            "path": str(file_path),
            "message": f"QR code saved as {file_path}.",
        }

    except Exception as error:
        return {
            "success": False,
            "error": f"I could not generate the QR code: {error}",
        }


def generate_qr_text(data):
    result = generate_qr(data)

    if result["success"]:
        return result["message"]

    return result["error"]


if __name__ == "__main__":
    print(
        generate_qr_text(
            "https://github.com"
        )
    )