from flask import current_app


def get_hotline_info() -> dict:
    return {
        "national_hotline": current_app.config["NATIONAL_HOTLINE_NUMBER"],
        "text_line": "Text HOME to 741741 (Crisis Text Line)",
        "emergency": "If you are in immediate danger, call your local emergency number (e.g. 911).",
    }
