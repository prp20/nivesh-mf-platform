import requests
from frontend.streamlit_app.config import API_BASE_URL


def get_funds():
    return requests.get(f"{API_BASE_URL}/funds").json()


def get_nav(fund_id: int):
    return requests.get(f"{API_BASE_URL}/nav/{fund_id}").json()


def get_metrics(fund_id: int):
    resp = requests.get(f"{API_BASE_URL}/metrics/{fund_id}")
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def start_metrics_job(fund_id: int):
    resp = requests.post(f"{API_BASE_URL}/metrics/jobs/{fund_id}")
    resp.raise_for_status()
    return resp.json()


def get_metrics_job(job_id: int):
    resp = requests.get(f"{API_BASE_URL}/metrics/jobs/{job_id}")
    resp.raise_for_status()
    return resp.json()


def compare_funds(fund_ids: list):
    """Compare multiple funds with their metrics"""
    funds_data = get_funds()
    fund_map = {f["id"]: f for f in funds_data}
    
    result = {"funds": []}
    
    for fund_id in fund_ids:
        if fund_id in fund_map:
            fund = fund_map[fund_id]
            metrics = get_metrics(fund_id)
            
            if metrics:
                fund["metrics"] = metrics
            else:
                fund["metrics"] = {
                    "sharpe_ratio": None,
                    "sortino_ratio": None,
                    "alpha": None,
                    "beta": None,
                    "std_deviation": None,
                    "r_squared": None,
                    "rolling_return_1y": None,
                    "rolling_return_3y": None,
                    "upside_capture": None,
                    "downside_capture": None,
                }
            
            result["funds"].append(fund)
    
    return result


def recommend(payload: dict):
    """Get fund recommendations based on risk profile and category"""
    try:
        resp = requests.post(f"{API_BASE_URL}/recommend", json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        # Return error response for UI handling
        return {
            "error": True,
            "status_code": e.response.status_code,
            "message": str(e),
            "recommendations": []
        }
    except Exception as e:
        return {
            "error": True,
            "message": str(e),
            "recommendations": []
        }

def sync_fund(fund_id: int):
    """Sync fund data: fetch latest details, NAV, and re-compute metrics"""
    try:
        resp = requests.post(f"{API_BASE_URL}/sync/{fund_id}")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": str(e),
            "messages": [],
            "errors": [str(e)],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "messages": [],
            "errors": [str(e)],
        }