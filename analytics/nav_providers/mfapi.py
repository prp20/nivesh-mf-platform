import requests
from datetime import datetime
from typing import Optional, List, Dict, Any


MFAPI_BASE = "https://api.mfapi.in/mf"


def fetch_nav_history(scheme_code: str) -> list[dict]:
    """Fetch NAV history for a given scheme code from MFAPI."""
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


class MFAPIProvider:
    """Provider for MFAPI mutual fund data."""
    
    def __init__(self):
        """Initialize the MFAPI provider."""
        self.base_url = MFAPI_BASE
    
    async def get_nav_data(self, scheme_code: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get NAV data for a given scheme code.
        
        Args:
            scheme_code: AMFI scheme code
            
        Returns:
            List of NAV data dictionaries with 'date' and 'nav' keys, or None if error
        """
        try:
            nav_list = fetch_nav_history(scheme_code)
            return nav_list if nav_list else None
        except Exception as e:
            print(f"Error fetching NAV data for scheme {scheme_code}: {e}")
            return None