from flask import current_app


def get_hotline_info() -> dict:
    return {
                "national_hotline": current_app.config["NATIONAL_HOTLINE_NUMBER"],
        "text_line": "ADUN Counselling: +2348125744137 / counselling@edu.ng",
        "emergency": "If you are in immediate danger, call the Nigeria Police emergency line (112) or your local emergency number.",
    }
