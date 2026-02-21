import pandas as pd
import requests
import json
from datetime import datetime, timezone
from mftool import Mftool
from tqdm import tqdm
from datetime import datetime
import yfinance as yf

url = "http://localhost:8000"
input_format = "%d-%m-%Y"
output_format = "%Y-%m-%d"

def populate_mf_data():
    master_funds_list = pd.read_csv("equity_only.csv")
    master_funds_list['inception_date'] = pd.to_datetime(master_funds_list['inception_date'], format=input_format)
    master_funds_list['inception_date'] = master_funds_list['inception_date'].dt.strftime(output_format)

    for row in tqdm(master_funds_list.iterrows()):
        req_payload = {
            'scheme_code': str(row[1]['scheme_code']),
            'scheme_name': row[1]['scheme_name'],
            'amc_name': row[1]['amc_name'],
            'plan_type': row[1]['plan_type'],
            'risk_profile': row[1]['risk_profile'],
            'inception_date': row[1]['inception_date'],
            'scheme_category': row[1]['scheme_category'],
            'scheme_subcategory': row[1]['scheme_subcategory'],
            'benchmark_index_code': row[1]['benchmark_index_code'],
            'is_active':True
        }

        response = requests.post(f"{url}/funds/", json=req_payload)
        # Check the response status code
        if response.status_code == 200 or response.status_code == 201:
            # print("Request successful!")
            # Parse the JSON response into a Python dictionary
            returned_data = response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
    return

def populate_nav_data():
    mf = Mftool()
    master_funds_list = pd.read_csv("equity_only.csv")
    scheme_codes = (
        pd.to_numeric(master_funds_list["scheme_code"], errors="coerce")
        .dropna()
        .astype(int)
        .unique()
    )
    for scheme_code in tqdm(scheme_codes):
        respnse_dict = mf.get_scheme_historical_nav(
                str(scheme_code),
                as_Dataframe=True
            )
        if respnse_dict is not None:
            respnse_dict.reset_index(inplace=True)
            respnse_dict['date'] = pd.to_datetime(respnse_dict['date'], format=input_format)
            respnse_dict['date'] = respnse_dict['date'].dt.strftime(output_format)
            respnse_dict['nav'] = respnse_dict['nav'].astype(float)
            # Convert DataFrame to dictionary with date as key and nav as value (DD-MM-YYYY format)
            nav_data = {row['date']: float(row['nav']) for _, row in respnse_dict.iterrows()}
            payload = {'scheme_code': str(scheme_code), 'nav_data': nav_data}
            response = requests.post(f"{url}/navs/bulk", json=payload)
            # Check the response status code
            if response.status_code == 200 or response.status_code == 201:
                # print("Request successful!")
                # Parse the JSON response into a Python dictionary
                returned_data = response.json()
            else:
                print(f"Request failed with status code: {response.status_code}")
                print(response.json)
        else:
            print(f"Invalid Schema {scheme_code}")
    return

def populate_benchmarks():
    ticker_list = [{"benchmark_code": "Nifty 50", "ticker":"^NSEI"},
                   {"benchmark_code": "Nifty 100", "ticker":"^CNX100"},
                   {"benchmark_code": "Nifty 200", "ticker":"^CNX200"},
                   {"benchmark_code": "Nifty 500", "ticker":"^CRSLDX"},
                   {"benchmark_code": "Nifty Midcap 150", "ticker":"^CNXMIDCAP"},
                   {"benchmark_code": "Nifty Smallcap 250", "ticker":"^CNXSC"},
                   {"benchmark_code": "Nifty Bank", "ticker":"^NSEBANK"},
                   {"benchmark_code": "Nifty IT", "ticker":"^CNXIT"},
    ]


    data = yf.download(
        ticker,
        start="2006-04-03",
        end="2025-01-01",
        interval="1d",
        auto_adjust=True
    )


    data.drop(['High', 'Low', 'Open', 'Volume'], axis=1, inplace=True)
    data.reset_index(inplace=True)
    data.columns

populate_mf_data()
populate_nav_data()