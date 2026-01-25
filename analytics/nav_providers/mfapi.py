import requests
from datetime import datetime


MFAPI_BASE = "https://api.mfapi.in/mf"


def fetch_nav_history(scheme_code: str) -> list[dict]:
    url = f"{MFAPI_BASE}/{scheme_code}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    nav_list = []

    for entry in data.get("data", []):
        nav_list.append(
            {
                "date": datetime.strptime(entry["date"], "%d-%m-%Y").date(),
                "nav": float(entry["nav"]),
            }
        )

    return nav_list
