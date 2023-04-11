import configparser
import datetime

import requests
import json

from utils import crud

config = configparser.ConfigParser()
config.read("settings.ini")
WBToken = config["settings"]["WBToken"]
x_supplier_id = config["settings"]["x-supplier-id"]

url = "https://seller.wildberries.ru/ns/categories-info/suppliers-portal-analytics/api/v1/categories"

payload = json.dumps({
    "take": 7530,
    "skip": 0,
    "sort": "name",
    "order": "asc",
    "search": {}
})
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': f'WBToken={WBToken}; x-supplier-id={x_supplier_id}'
}

response = requests.request("POST", url, headers=headers, data=payload)

crud.delete_categories()

i = 1

for category in response.json()['data']['categories']:
    crud.add_category(category['id'], category['percent'], category['percentFBS'])
    if i % 1000 == 0:
        print(int(1000 // 70), '%')
