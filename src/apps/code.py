from typing import Optional


def codes():
    error_code = {
        "00001": "Your ID does not exist. Please check it",
        "00002": "Spotify does not provide feature about this BGM. Please try another BGM",
        "00003": "Please type the number, not string",
        "00004": "Please set the number less than 10001"
    }

    return error_code


def num_check(num: int) -> (Optional[str], Optional[str]):
    if not isinstance(num, int):
        return None, "00003"

    if num > 10000:
        return None, "00004"

    return "OK", None