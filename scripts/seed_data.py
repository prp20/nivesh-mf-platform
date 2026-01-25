import csv
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


def load_funds():
    with open("data/funds.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            payload = {
                "scheme_code": row["scheme_code"],
                "fund_name": row["fund_name"],
                "category": row["category"],
                "sub_category": row["sub_category"],
                "benchmark": row["benchmark"],
                "aum": float(row["aum"]),
                "ter": float(row["ter"]),
                "launch_date": row["launch_date"],
            }
            r = requests.post(f"{BASE_URL}/funds", json=payload)
            print("Fund:", r.status_code, r.json())


def load_managers():
    with open("data/fund_managers.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = requests.post(
                f"{BASE_URL}/fund-managers",
                json={
                    "name": row["name"],
                    "experience_years": int(row["experience_years"]),
                },
            )
            print("Manager:", r.status_code, r.json())


def load_mappings():
    with open("data/fund_manager_mapping.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # fetch fund by scheme_code
            funds = requests.get(f"{BASE_URL}/funds").json()
            fund = next(
                f for f in funds if f["scheme_code"] == row["scheme_code"]
            )

            managers = requests.get(f"{BASE_URL}/fund-managers").json()
            manager = next(
                m for m in managers if m["name"] == row["manager_name"]
            )

            r = requests.post(
                f"{BASE_URL}/funds/{fund['id']}/managers/{manager['id']}"
            )
            print("Mapping:", r.status_code)


def main():
    load_funds()
    load_managers()
    load_mappings()


if __name__ == "__main__":
    main()
