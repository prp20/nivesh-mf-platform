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
