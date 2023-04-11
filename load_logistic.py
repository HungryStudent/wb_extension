import configparser
import datetime
import time

import requests
import json

from utils import crud

config = configparser.ConfigParser()
config.read("settings.ini")
WBToken = config["settings"]["WBToken"]
receptionWBToken = config["settings"]["receptionWBToken"]
x_supplier_id = config["settings"]["x-supplier-id"]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': f'WBToken={WBToken}; x-supplier-id={x_supplier_id}'
}
now_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")
end_date = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=3), "%Y-%m-%d")

response = requests.request("GET",
                            f"https://seller.wildberries.ru/ns/categories-info/suppliers-portal-analytics/api/v1/tariffs-period?date={now_date}",
                            headers=headers)

warehouses = response.json()['data']['warehouseList'][1:-2]
for warehouse in warehouses:
    try:
        logistic_base, logistic = warehouse['delivery'].split(' + ')
    except ValueError:
        logistic_base = 0
        logistic = 0

    from_client = warehouse['deliveryReturn']

    try:
        storage_base, storage = warehouse['storageMonoAndMix'].split(' + ')
    except ValueError:
        storage_base = 0
        storage = 0
    crud.update_logistic_and_storage(warehouse['warehouseName'].lower(), logistic_base,
                                     logistic, from_client, storage_base, storage)

data = json.dumps({
    "id": "json-rpc_9",
    "jsonrpc": "2.0",
    "params": {
        "dateTo": f"{end_date}T21:00:00.000Z",
        "dateFrom": f"{now_date}T01:37:15.584Z"
    },
})

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': f'WBToken={receptionWBToken}; x-supplier-id-external=e729a3a7-dabc-4595-bf73-7e82010d4e77'
}

response = requests.request("POST",
                            "https://seller-supply.wildberries.ru/ns/sm-supply/supply-manager/api/v1/supply/acceptanceCoefficientsReport",
                            headers=headers,
                            data=data)

for warehouse in response.json()['result']['report']:
    if warehouse['date'][:10] == now_date and warehouse['acceptanceType'] == 6:

        warehouse_name = warehouse['warehouseName'].replace("СЦ ", "").lower()

        if "Минск" in warehouse['warehouseName']:

        if warehouse_name == "санкт-петербург":
            crud.update_reception('санкт-петербург уткина заводь', warehouse['coefficient'])
            crud.update_reception('санкт-петербург шушары', warehouse['coefficient'])
            crud.update_reception('санкт-петербург кбт', warehouse['coefficient'])
            continue
        crud.update_reception(warehouse_name, warehouse['coefficient'])
