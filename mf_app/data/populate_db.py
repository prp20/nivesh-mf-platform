import pandas as pd
import requests
import json
from datetime import datetime, timezone
from mftool import Mftool
from tqdm import tqdm
from datetime import datetime

url = "http://localhost:8000/funds/"
input_format = "%d-%m-%Y"
output_format = "%Y-%m-%d"

def populate_mf_data():
    master_funds_list = pd.read_csv("scheme_master_with_benchmark.csv")
    master_funds_list
    for row in tqdm(master_funds_list.iterrows()):
        req_payload = {
            'scheme_code': str(row[1]['scheme_code']),
            'scheme_name': row[1]['scheme_name'],
            'amc_name': row[1]['amc_name'],
            'plan_type': row[1]['plan_type'],
            'risk_profile': row[1]['risk_profile'],
            'inception_date': datetime.strptime(row[1]['inception_date'],input_format).strftime(output_format),
            'scheme_category': row[1]['scheme_category'],
            'scheme_subcategory': row[1]['scheme_subcategory'],
            'benchmark_index_code': row[1]['benchmark_index_code'],
            'is_active':True
        }

        response = requests.post(url, json=req_payload)
        # Check the response status code
        if response.status_code == 200 or response.status_code == 201:
            # print("Request successful!")
            # Parse the JSON response into a Python dictionary
            returned_data = response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
    return

populate_mf_data()