from utils import crud
import configparser
import requests
import logging
import json


config = configparser.ConfigParser()
config.read("settings.ini")
commissionWBToken = config["settings"]["commissionWBToken"]
x_supplier_id = config["settings"]["x-supplier-id"]
logging.basicConfig(filename="load_commission.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

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
    'Cookie': f'WBToken={commissionWBToken}; x-supplier-id={x_supplier_id}'
}
response = requests.request("POST", url, headers=headers, data=payload)
categories = response.json()['data']['categories']
categories_count = len(categories)
crud.delete_categories()

i = 1
for category in categories:
    crud.add_category(category['id'], category['percent'], category['percentFBS'])
    if i % 1000 == 0:
        print(int(i // categories_count), '%')
    i += 1

logging.info(f"end {categories_count}")
